import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# AWS X-Ray integration
if os.getenv("ENABLE_XRAY", "false").lower() == "true":
    from aws_xray_sdk.core import xray_recorder, patch_all
    from aws_xray_sdk.ext.fastapi.middleware import XRayMiddleware
    xray_recorder.configure(service="aws-genai-backend")
    patch_all()

from app.routes import api_router
from app.bedrock_client import get_bedrock_client
from app.vector_store import get_opensearch_client

# Structured Logging for AWS CloudWatch
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] [%(name)s] [trace_id=%(thread)d] %(message)s"
)
logger = logging.getLogger("aws-genai-backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AWS GenAI Backend services...")
    # Verify Bedrock and OpenSearch connectivity
    try:
        bedrock = get_bedrock_client()
        logger.info("Bedrock Runtime client initialized successfully.")
    except Exception as e:
        logger.warning(f"Bedrock initialization warning: {e}")

    try:
        aoss = get_opensearch_client()
        logger.info("OpenSearch Serverless client initialized successfully.")
    except Exception as e:
        logger.warning(f"OpenSearch initialization warning: {e}")

    yield

    logger.info("Shutting down AWS GenAI Backend services...")

app = FastAPI(
    title="AWS GenAI Production Service",
    description="Enterprise-grade RAG & GenAI platform powered by Amazon Bedrock, OpenSearch Serverless, and AWS EKS.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable AWS X-Ray middleware if enabled
if os.getenv("ENABLE_XRAY", "false").lower() == "true":
    app.add_middleware(XRayMiddleware, recorder=xray_recorder)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Kubernetes Liveness Probe"""
    return {"status": "healthy", "service": "aws-genai-backend", "version": "1.0.0"}

@app.get("/ready", tags=["Monitoring"])
async def readiness_check():
    """Kubernetes Readiness Probe"""
    # Check dependencies if critical
    return {
        "status": "ready",
        "bedrock_configured": bool(os.getenv("AWS_REGION")),
        "opensearch_configured": bool(os.getenv("OPENSEARCH_ENDPOINT"))
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
