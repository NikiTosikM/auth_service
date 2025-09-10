from uuid import uuid4
from datetime import UTC
from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"
