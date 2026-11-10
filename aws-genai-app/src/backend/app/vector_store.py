import os
import boto3
import logging
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

logger = logging.getLogger("aws-genai-backend.vector_store")

_opensearch_client = None

def get_opensearch_client() -> OpenSearch:
    global _opensearch_client
    if _opensearch_client is None:
        host = os.getenv("OPENSEARCH_ENDPOINT", "").replace("https://", "").replace("http://", "")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        credentials = boto3.Session().get_credentials()
        # For OpenSearch Serverless service name is 'aoss'
        service = "aoss" if "aoss" in host else "es"
        auth = AWSV4SignerAuth(credentials, region, service)

        _opensearch_client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )
    return _opensearch_client

class OpenSearchVectorStore:
    def __init__(self):
        self.client = get_opensearch_client()
        self.index_name = os.getenv("OPENSEARCH_INDEX_NAME", "genai-knowledge-base")
        self.vector_field = os.getenv("OPENSEARCH_VECTOR_FIELD", "embedding")
        self.dimensions = int(os.getenv("OPENSEARCH_DIMENSION", "1024"))

    def create_index_if_not_exists(self):
        """
        Creates k-NN vector index with HNSW algorithm and cosine similarity
        """
        if not self.client.indices.exists(index=self.index_name):
            index_body = {
                "settings": {
                    "index.knn": True,
                    "index.knn.algo_param.ef_search": 512
                },
                "mappings": {
                    "properties": {
                        self.vector_field: {
                            "type": "knn_vector",
                            "dimension": self.dimensions,
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib",
                                "parameters": {
                                    "ef_construction": 512,
                                    "m": 16
                                }
                            }
                        },
                        "content": {"type": "text"},
                        "doc_id": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "chunk_index": {"type": "integer"},
                        "metadata": {"type": "object"}
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=index_body)
            logger.info(f"Created OpenSearch vector index: {self.index_name}")

    def index_document_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Batch index text chunks with embedding vectors
        """
        for chunk in chunks:
            doc = {
                self.vector_field: chunk["embedding"],
                "content": chunk["content"],
                "doc_id": chunk.get("doc_id", "unknown"),
                "source": chunk.get("source", "s3-upload"),
                "chunk_index": chunk.get("chunk_index", 0),
                "metadata": chunk.get("metadata", {})
            }
            self.client.index(index=self.index_name, body=doc, refresh=True)
        logger.info(f"Successfully indexed {len(chunks)} chunks into {self.index_name}")

    def vector_search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        k-NN approximate nearest neighbor vector search
        """
        query = {
            "size": top_k,
            "query": {
                "knn": {
                    self.vector_field: {
                        "vector": query_vector,
                        "k": top_k
                    }
                }
            }
        }

        try:
            response = self.client.search(index=self.index_name, body=query)
            hits = response["hits"]["hits"]
            results = []
            for hit in hits:
                results.append({
                    "score": hit["_score"],
                    "content": hit["_source"]["content"],
                    "source": hit["_source"].get("source"),
                    "doc_id": hit["_source"].get("doc_id"),
                    "metadata": hit["_source"].get("metadata", {})
                })
            return results
        except Exception as e:
            logger.error(f"OpenSearch vector query failed: {e}", exc_info=True)
            return []

    def hybrid_search(self, query_text: str, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid search combining BM25 keyword matching with k-NN vector search
        """
        query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "content": {
                                    "query": query_text,
                                    "boost": 0.3
                                }
                            }
                        },
                        {
                            "knn": {
                                self.vector_field: {
                                    "vector": query_vector,
                                    "k": top_k,
                                    "boost": 0.7
                                }
                            }
                        }
                    ]
                }
            }
        }
        try:
            response = self.client.search(index=self.index_name, body=query)
            return [
                {
                    "score": hit["_score"],
                    "content": hit["_source"]["content"],
                    "source": hit["_source"].get("source"),
                    "doc_id": hit["_source"].get("doc_id"),
                    "metadata": hit["_source"].get("metadata", {})
                }
                for hit in response["hits"]["hits"]
            ]
        except Exception as e:
            logger.warning(f"Hybrid search fallback to vector search: {e}")
            return self.vector_search(query_vector, top_k)
