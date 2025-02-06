from fastapi import FastAPI
from offle_assistant.routes.v1 import router
import uvicorn

app = FastAPI()

app.include_router(router)


def start():
    uvicorn.run(
        "offle_assistant.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    start()
