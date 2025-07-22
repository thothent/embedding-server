#!/bin/bash

# Check if required arguments are provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <job_id>"
    exit 1
fi

JOB_ID="$1"

curl -X GET "http://localhost:8000/embedding/$JOB_ID"
