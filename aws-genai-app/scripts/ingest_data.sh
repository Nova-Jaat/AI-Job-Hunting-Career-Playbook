#!/usr/bin/env bash
set -euo pipefail

BUCKET_NAME=${1:-"genai-knowledge-docs-prod"}
SOURCE_DIR=${2:-"./data/documents"}

echo "📂 Uploading knowledge documents from $SOURCE_DIR to s3://$BUCKET_NAME..."

if [ ! -d "$SOURCE_DIR" ]; then
  mkdir -p "$SOURCE_DIR"
  echo "Sample enterprise document for RAG ingestion test." > "$SOURCE_DIR/sample_architecture.txt"
fi

aws s3 sync "$SOURCE_DIR" "s3://$BUCKET_NAME/" --sse AES256

echo "✅ Documents uploaded. S3 Event will trigger Lambda ingestion pipeline automatically!"
