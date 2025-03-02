import os

from motor.motor_asyncio import AsyncIOMotorClient
from offle_assistant.constants import OFFLE_ENV

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

MONGO_URI = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@localhost:27017"
)

# Set the database name depending on the environment
if OFFLE_ENV == "test":
    MONGO_DB_NAME = "offle_assistant_test"
elif OFFLE_ENV == "dev":
    MONGO_DB_NAME = "offle_assistant_dev"
else:
    MONGO_DB_NAME = "offle_assistant"

client = AsyncIOMotorClient(MONGO_URI)
# db = client[MONGO_DB_NAME]
# db.groups.create_index([("name", 1)], unique=True)

# personas_collection = db["personas"]
# users_collection = db["users"]
# message_history_collection = db["message_history"]
# fs_bucket = AsyncIOMotorGridFSBucket(db)
