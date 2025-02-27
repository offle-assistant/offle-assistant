from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from offle_assistant.llm_client import LLMClient
from offle_assistant.vector_db import (
    VectorDB,
    QdrantDB,
)
from offle_assistant.config import (
    LLMServerConfig,
    VectorDbServerConfig
)
from offle_assistant.routes.v1 import (
    auth_router,
    users_router,
    admin_router,
    personas_router
)

app = FastAPI()


@app.get("/")  # Ensure this allows GET requests
async def root():
    return {"message": "FastAPI is running!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.103:5173",
        "http://192.168.1.249:5173",
        "http://172.23.0.1:5173",
        "http://172.24.0.1:5173",
        "http://172.18.0.1:5173",
        "http://172.21.0.1:5173",
        "http://172.25.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(personas_router, prefix="/personas", tags=["Personas"])

# Store in `app.state`
app.state.llm_server: LLMClient = LLMClient(
    LLMServerConfig(
        hostname="localhost",
        port=11435,
    ),
    model_list=["llama3.2"]
)

app.state.vector_db: VectorDB = QdrantDB(
    VectorDbServerConfig(
        hostname="localhost",
        port=6333
    )
)


@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Manually handle OPTIONS preflight requests for CORS."""
    print(f"Received OPTIONS request for: {full_path}")
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def start():
    uvicorn.run(
        "offle_assistant.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    start()
