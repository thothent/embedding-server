#!/bin/bash

# Check if required arguments are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <job_id> <content> <type>"
    exit 1
fi

JOB_ID="$1"
CONTENT="$2"
TYPE="$3"

# Properly escape JSON strings and create BODY
BODY=$(jq -n --arg job_id "$JOB_ID" --arg content "$CONTENT" --arg type "$TYPE" \
    '{job_id: $job_id, content: $content, type: $type}')

# Make curl request with proper quoting
curl -X POST "http://localhost:8000/embedding" \
    -H "Content-Type: application/json" \
    -d "$BODY"
