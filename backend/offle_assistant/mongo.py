import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = (
    f"mongodb://{os.environ.get('MONGO_USER')}"
    f":{os.environ.get('MONGO_PASSWORD')}@localhost:27017"
)

client = AsyncIOMotorClient(MONGO_URI)
db = client["offle_assistant"]
personas_collection = db["personas"]
users_collection = db["users"]
message_history_collection = db["message_history"]
