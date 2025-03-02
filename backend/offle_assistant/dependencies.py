from fastapi import FastAPI
from offle_assistant.mongo import MONGO_DB_NAME, client
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


def get_app() -> FastAPI:
    from offle_assistant.main import app
    return app


def get_llm_client():
    """Retrieve the immutable LLM server config from FastAPI's app state."""
    return get_app().state.llm_server


def get_vector_db():
    """Retrieve the immutable LLM server config from FastAPI's app state."""
    return get_app().state.vector_db


def get_db() -> AsyncIOMotorClient:
    """Retrieve the database instance dynamically."""
    return client[MONGO_DB_NAME]


def get_fs_bucket(db):
    """Retrieve a GridFS bucket for a specific database instance."""
    return AsyncIOMotorGridFSBucket(db)
