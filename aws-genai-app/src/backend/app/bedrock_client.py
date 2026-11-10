import os
import json
import boto3
from typing import List, Dict, Any, AsyncGenerator
from botocore.config import Config
import logging

logger = logging.getLogger("aws-genai-backend.bedrock")

# Best practice: Boto3 client retry strategy and connection pooling
bedrock_config = Config(
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    retries={"max_attempts": 3, "mode": "adaptive"},
    max_pool_connections=50
)

_bedrock_runtime_client = None

def get_bedrock_client():
    global _bedrock_runtime_client
    if _bedrock_runtime_client is None:
        _bedrock_runtime_client = boto3.client("bedrock-runtime", config=bedrock_config)
    return _bedrock_runtime_client

class BedrockService:
    def __init__(self):
        self.client = get_bedrock_client()
        self.default_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.embedding_model_id = os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")

    def generate_embedding(self, text: str, dimensions: int = 1024) -> List[float]:
        """
        Generate vector embedding using Amazon Titan Embeddings v2
        """
        try:
            body = json.dumps({
                "inputText": text,
                "dimensions": dimensions,
                "normalize": True
            })
            response = self.client.invoke_model(
                modelId=self.embedding_model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            response_body = json.loads(response["body"].read())
            return response_body["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding with Bedrock: {e}", exc_info=True)
            raise

    def invoke_llm(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are an enterprise AI assistant.",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        model_id: str = None
    ) -> Dict[str, Any]:
        """
        Invoke Bedrock Converse API for structured multi-turn conversation and prompt caching
        """
        target_model = model_id or self.default_model_id
        try:
            # Transform to Converse API format
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": [{"text": msg["content"]}]
                })

            response = self.client.converse(
                modelId=target_model,
                messages=formatted_messages,
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                    "topP": 0.9
                }
            )

            output_text = response["output"]["message"]["content"][0]["text"]
            usage = response.get("usage", {})
            return {
                "text": output_text,
                "usage": usage,
                "model": target_model,
                "stop_reason": response.get("stopReason")
            }
        except Exception as e:
            logger.error(f"Bedrock LLM Converse call failed: {e}", exc_info=True)
            raise

    async def invoke_llm_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are an enterprise AI assistant.",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        model_id: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream LLM tokens using converse_stream for sub-second TTFT (Time-to-First-Token)
        """
        target_model = model_id or self.default_model_id
        formatted_messages = [
            {"role": msg["role"], "content": [{"text": msg["content"]}]}
            for msg in messages
        ]

        try:
            response = self.client.converse_stream(
                modelId=target_model,
                messages=formatted_messages,
                system=[{"text": system_prompt}],
                inferenceConfig={"temperature": temperature, "maxTokens": max_tokens}
            )

            stream = response.get("stream")
            if stream:
                for event in stream:
                    if "contentBlockDelta" in event:
                        delta = event["contentBlockDelta"]["delta"]
                        if "text" in delta:
                            yield delta["text"]
        except Exception as e:
            logger.error(f"Bedrock streaming failed: {e}", exc_info=True)
            yield f"\n[Stream Error: {str(e)}]"
