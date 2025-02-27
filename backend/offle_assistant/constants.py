import os

OFFLE_ENV = os.getenv("OFFLE_ENV", "development")

__all__ = [
    "OFFLE_ENV",
]
