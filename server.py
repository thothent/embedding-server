import json
import uuid
from typing import List, Literal

import redis
from sentence_transformers import SentenceTransformer

MODEL = "mixedbread-ai/mxbai-embed-large-v1"

model = SentenceTransformer(MODEL)
redis_client = redis.Redis(host="localhost", port=6379, db=0)

STREAM_NAME = "embeddings_job_queue"
GROUP_NAME = "embeddings_producers_group"


class EmbeddingsBatchData:
    type: Literal["query", "passage"]
    inputs: List[str]


class EmbeddingsBatchResult:
    embeddings: List[str]


def process_batch(data: EmbeddingsBatchData) -> EmbeddingsBatchResult:
    embeddings = model.encode(
        data.inputs,
        normalize_embeddings=True,
        convert_to_numpy=True,
        output_value="sentence_embedding",
        truncate_dim=1024,
    )

    embeddings = [embedding.tolist() for embedding in embeddings]

    result = EmbeddingsBatchResult()
    result.embeddings = embeddings

    return result


def fetch_batch() -> EmbeddingsBatchData:
    entries = redis_client.xreadgroup(
        groupname=GROUP_NAME,
        consumername=str(uuid.uuid4()),
        streams={STREAM_NAME: ">"},
        count=1,
        block=0,
    )

    if not entries:
        raise RuntimeError(
            "Expected at least one entry after blocking read, but got none"
        )

    stream, messages = entries[0]
    msg_id, data = messages[0]

    redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
    redis_client.xdel(STREAM_NAME, msg_id)

    try:
        batchData = EmbeddingsBatchData()
        batchData.type = data[b"type"]
        batchData.inputs = json.loads(data[b"inputs"])
    except Exception:
        raise RuntimeError("Expected EmbeddingsBatchData but got other type")

    if not isinstance(batchData, EmbeddingsBatchData):
        raise RuntimeError("Expected EmbeddingsBatchData but got other type")

    return batchData


def main():
    try:
        redis_client.xgroup_create(
            name=STREAM_NAME, groupname=GROUP_NAME, id="0-0", mkstream=True
        )
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Group already exists.")
        else:
            raise RuntimeError("Failed to create group")

    print("Server started")
    while True:
        batch = fetch_batch()
        print(batch.inputs)
        embeddings = process_batch(batch)
        print(embeddings.embeddings)


if __name__ == "__main__":
    main()
