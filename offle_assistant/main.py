from fastapi import FastAPI
import uvicorn

from offle_assistant.llm_client import LLMClient
from offle_assistant.vector_db import VectorDB, QdrantDB
from offle_assistant.config import LLMServerConfig
from offle_assistant.routes.v1 import router

app = FastAPI()

app.include_router(router)


# Store in `app.state`
app.state.llm_server = LLMClient(
    LLMServerConfig(hostname="localhost", port=11434)
)
app.state.vector_db = QdrantDB(host="localhost", port=6333)


def start():
    uvicorn.run(
        "offle_assistant.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    start()
