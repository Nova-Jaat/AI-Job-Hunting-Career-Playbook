import os
import json
import urllib.parse
import boto3
import logging
from typing import List, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from pypdf import PdfReader
import io

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
bedrock_client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))

OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "").replace("https://", "")
INDEX_NAME = os.getenv("OPENSEARCH_INDEX_NAME", "genai-knowledge-base")
EMBEDDING_MODEL_ID = os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")

def get_aoss_client():
    region = os.getenv("AWS_REGION", "us-east-1")
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, "aoss")
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_ENDPOINT, "port": 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30
    )

def extract_text_from_s3(bucket: str, key: str) -> str:
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()

    if key.lower().endswith(".pdf"):
        pdf_stream = io.BytesIO(body)
        reader = PdfReader(pdf_stream)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text
    else:
        # Default assume UTF-8 text / markdown / html
        return body.decode("utf-8", errors="ignore")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def generate_bedrock_embedding(text: str) -> List[float]:
    response = bedrock_client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text, "dimensions": 1024, "normalize": True})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

def lambda_handler(event, context):
    """
    S3 Event Trigger:
    Triggered when new PDF/documents are uploaded to S3 bucket.
    """
    logger.info(f"Received S3 event: {json.dumps(event)}")
    aoss_client = get_aoss_client()

    processed_count = 0

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        logger.info(f"Processing object s3://{bucket}/{key}")

        try:
            raw_text = extract_text_from_s3(bucket, key)
            if not raw_text.strip():
                logger.warning(f"Empty content extracted from {key}")
                continue

            chunks = chunk_text(raw_text)
            logger.info(f"Extracted {len(chunks)} chunks from {key}")

            for idx, chunk in enumerate(chunks):
                vector = generate_bedrock_embedding(chunk)
                doc = {
                    "embedding": vector,
                    "content": chunk,
                    "doc_id": key,
                    "source": f"s3://{bucket}/{key}",
                    "chunk_index": idx,
                    "metadata": {
                        "size": record["s3"]["object"].get("size", 0),
                        "etag": record["s3"]["object"].get("eTag", "")
                    }
                }
                aoss_client.index(index=INDEX_NAME, body=doc)

            processed_count += 1
            logger.info(f"Successfully indexed document {key} into {INDEX_NAME}")

        except Exception as e:
            logger.error(f"Error processing {key}: {str(e)}", exc_info=True)
            raise e

    return {
        "statusCode": 200,
        "body": json.dumps({"processed_documents": processed_count})
    }
