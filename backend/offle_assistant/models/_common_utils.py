from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema
from bson import ObjectId


class PyObjectId(ObjectId):
    """
    Custom ObjectId type for MongoDB validation in Pydantic v2
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return handler(str)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
