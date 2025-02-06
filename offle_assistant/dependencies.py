from fastapi import FastAPI


def get_app() -> FastAPI:
    from offle_assistant.main import app
    return app


def get_llm_client():
    """Retrieve the immutable LLM server config from FastAPI's app state."""
    return get_app().state.llm_server


def get_vector_db():
    """Retrieve the immutable LLM server config from FastAPI's app state."""
    return get_app().state.vector_db
