from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema
from bson import ObjectId


class PyObjectId(ObjectId):
    """
    Custom ObjectId type for MongoDB validation in Pydantic v2

    This whole thing is honestly a bit fucked. The thing is, we need to handle
    ObjectIds here. However, Pydantic doesn't handle type checking when you put
    a custom type like this in a "List" or "Optional". So in those cases, we
    need to convert those to strings in the validators of the individual
    models... i hate it

    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return handler(str)

    @classmethod
    def validate(cls, value):
        """Ensure that ObjectId is valid, converting from string if needed."""
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError("Invalid ObjectId")

    def __str__(self):
        """Ensure ObjectId is always converted to a string when needed."""
        return str(super().__str__())
