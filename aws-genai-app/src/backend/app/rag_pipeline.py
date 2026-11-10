import logging
from typing import Dict, Any, List, AsyncGenerator
from app.bedrock_client import BedrockService
from app.vector_store import OpenSearchVectorStore

logger = logging.getLogger("aws-genai-backend.rag")

SYSTEM_RAG_PROMPT = """You are an enterprise AI assistant backed by high-accuracy document retrieval.
Use the following retrieved context passages to answer the user's question accurately.

Guidelines:
1. Ground your answers strictly in the provided Context.
2. If the context does not contain enough information, state clearly that the knowledge base does not contain the answer. Do not hallucinate or make up facts.
3. Provide citations to the source documents whenever referring to specific information (e.g. [Source: doc_id]).
4. Maintain a professional, concise, and helpful tone.

--- CONTEXT PASSAGES ---
{context_passages}
------------------------
"""

class RAGPipeline:
    def __init__(self):
        self.bedrock = BedrockService()
        self.vector_store = OpenSearchVectorStore()

    def _build_context_string(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        if not retrieved_chunks:
            return "No relevant documents found in knowledge base."
        
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "Unknown")
            doc_id = chunk.get("doc_id", "Doc")
            content = chunk.get("content", "").strip()
            context_parts.append(f"[{i}] Document: {doc_id} | Source: {source}\nContent: {content}\n")
        return "\n".join(context_parts)

    def query(
        self,
        question: str,
        chat_history: List[Dict[str, str]] = None,
        top_k: int = 4,
        temperature: float = 0.2,
        use_hybrid: bool = True
    ) -> Dict[str, Any]:
        """
        Execute full RAG pipeline: Embedding -> OpenSearch Retrieval -> Prompt Augmentation -> Bedrock LLM
        """
        chat_history = chat_history or []
        logger.info(f"Processing RAG query: '{question}' with top_k={top_k}")

        # Step 1: Generate query vector
        query_embedding = self.bedrock.generate_embedding(question)

        # Step 2: Retrieve chunks from OpenSearch Serverless
        if use_hybrid:
            retrieved_chunks = self.vector_store.hybrid_search(
                query_text=question,
                query_vector=query_embedding,
                top_k=top_k
            )
        else:
            retrieved_chunks = self.vector_store.vector_search(
                query_vector=query_embedding,
                top_k=top_k
            )

        # Step 3: Augment Prompt
        context_str = self._build_context_string(retrieved_chunks)
        augmented_system_prompt = SYSTEM_RAG_PROMPT.format(context_passages=context_str)

        # Prepare messages
        messages = list(chat_history)
        messages.append({"role": "user", "content": question})

        # Step 4: Generate LLM Response with Amazon Bedrock
        llm_response = self.bedrock.invoke_llm(
            messages=messages,
            system_prompt=augmented_system_prompt,
            temperature=temperature
        )

        # Extract sources for attribution
        sources = [
            {
                "doc_id": c.get("doc_id"),
                "source": c.get("source"),
                "score": c.get("score"),
                "snippet": c.get("content", "")[:200] + "..."
            }
            for c in retrieved_chunks
        ]

        return {
            "answer": llm_response["text"],
            "sources": sources,
            "usage": llm_response.get("usage", {}),
            "model": llm_response.get("model")
        }

    async def query_stream(
        self,
        question: str,
        chat_history: List[Dict[str, str]] = None,
        top_k: int = 4,
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        """
        Streaming RAG pipeline for real-time frontend token rendering
        """
        chat_history = chat_history or []
        query_embedding = self.bedrock.generate_embedding(question)
        retrieved_chunks = self.vector_store.vector_search(query_vector=query_embedding, top_k=top_k)

        context_str = self._build_context_string(retrieved_chunks)
        augmented_system_prompt = SYSTEM_RAG_PROMPT.format(context_passages=context_str)

        messages = list(chat_history)
        messages.append({"role": "user", "content": question})

        async for token in self.bedrock.invoke_llm_stream(
            messages=messages,
            system_prompt=augmented_system_prompt,
            temperature=temperature
        ):
            yield token
