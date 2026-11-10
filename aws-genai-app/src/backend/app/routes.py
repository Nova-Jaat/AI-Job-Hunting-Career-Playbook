import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.rag_pipeline import RAGPipeline
from app.vector_store import OpenSearchVectorStore
from app.bedrock_client import BedrockService
from app.utils import recursive_chunk_text

logger = logging.getLogger("aws-genai-backend.routes")
api_router = APIRouter()

rag_pipeline = RAGPipeline()
vector_store = OpenSearchVectorStore()
bedrock_service = BedrockService()

# ----------------- Request / Response Models -----------------

class MessageModel(BaseModel):
    role: str = Field(..., description="Role of the sender: 'user' or 'assistant'")
    content: str = Field(..., description="Text content of the message")

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User prompt or query")
    history: List[MessageModel] = Field(default=[], description="Prior conversation turns")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of vector chunks to retrieve")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    use_hybrid: bool = Field(default=True, description="Enable hybrid BM25 + k-NN search")

class SourceCitation(BaseModel):
    doc_id: Optional[str]
    source: Optional[str]
    score: Optional[float]
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    usage: Dict[str, Any]
    model: Optional[str]

class IngestDocumentRequest(BaseModel):
    doc_id: str
    content: str
    source: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    metadata: Dict[str, Any] = {}

class IngestResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    status: str

# ----------------- API Endpoints -----------------

@api_router.post("/chat", response_model=ChatResponse, summary="Synchronous RAG Chat")
async def chat_endpoint(request: ChatRequest):
    """
    Execute full enterprise RAG query with Bedrock and OpenSearch Serverless
    """
    try:
        history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
        result = rag_pipeline.query(
            question=request.question,
            chat_history=history_dicts,
            top_k=request.top_k,
            temperature=request.temperature,
            use_hybrid=request.use_hybrid
        )
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            usage=result["usage"],
            model=result["model"]
        )
    except Exception as e:
        logger.error(f"Error executing chat query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GenAI pipeline failure: {str(e)}"
        )

@api_router.post("/chat/stream", summary="Streaming RAG Chat")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streams response tokens using Server-Sent Events (SSE)
    """
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]

    async def event_generator():
        try:
            async for chunk in rag_pipeline.query_stream(
                question=request.question,
                chat_history=history_dicts,
                top_k=request.top_k,
                temperature=request.temperature
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: [ERROR: {str(e)}]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@api_router.post("/ingest", response_model=IngestResponse, summary="Ingest Document Text")
async def ingest_document(req: IngestDocumentRequest):
    """
    Chunks document, generates Bedrock embeddings, and persists into OpenSearch Serverless
    """
    try:
        chunks = recursive_chunk_text(
            req.content,
            chunk_size=req.chunk_size,
            chunk_overlap=req.chunk_overlap
        )
        
        indexed_chunks = []
        for idx, chunk_text in enumerate(chunks):
            embedding = bedrock_service.generate_embedding(chunk_text)
            indexed_chunks.append({
                "content": chunk_text,
                "embedding": embedding,
                "doc_id": req.doc_id,
                "source": req.source,
                "chunk_index": idx,
                "metadata": req.metadata
            })

        vector_store.index_document_chunks(indexed_chunks)

        return IngestResponse(
            doc_id=req.doc_id,
            chunks_indexed=len(indexed_chunks),
            status="SUCCESS"
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion error: {str(e)}"
        )

@api_router.post("/index/init", summary="Initialize Vector Index")
async def initialize_index():
    """
    Creates OpenSearch k-NN index with HNSW cosine distance
    """
    try:
        vector_store.create_index_if_not_exists()
        return {"status": "success", "message": f"Index {vector_store.index_name} initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
