from typing import List, Literal

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class PostEmbeddingRequest(BaseModel):
    job_id: str
    type: Literal["query", "passage"]
    content: str


class PostEmbeddingResponse(BaseModel):
    job_id: str


@app.post("/embedding")
def queueEmbedding(request: PostEmbeddingRequest) -> PostEmbeddingResponse:
    return {"job_id": request.job_id}


class GetEmbeddingRequest(BaseModel):
    job_id: str


class GetEmbeddingResponse(BaseModel):
    job_id: str
    status: Literal["pending", "finished"]
    embedding: List[float]
    model: str


@app.get("/embedding/{job_id}")
def getEmbedding(job_id: str) -> GetEmbeddingResponse:
    return {"job_id": job_id, "status": "pending", "embedding": [], "model": ""}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
