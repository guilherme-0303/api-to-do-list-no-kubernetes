from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TodoSchema(BaseModel):
    title: str
    description: str | None = None


class TodoResponse(TodoSchema):
    todo_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TodoPatch(BaseModel):
    title: str | None = None
    description: str | None = None
