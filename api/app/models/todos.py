from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import mapped_as_dataclass, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import table_registry

@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    # Campos obrigatórios
    todo_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), init=False, primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(
        String(127), nullable=False
    )

    # Opcionais
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Gerados automaticamente
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), init=False
    )
