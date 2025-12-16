"""Projection model for storing calculated baby blueprints."""
from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class Projection(BaseModel):
    """Stored projection/blueprint for a user."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(alias="userId")
    profile_id: PyObjectId = Field(alias="profileId")
    projection_data: dict[str, Any] = Field(alias="projectionData")  # The full projection result
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "alias_generator": to_camel,
    }