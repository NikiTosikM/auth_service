import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import BYTEA, UUID

from core.db import Base
from auth.schemas import UserRole


class User(Base):
    __tablename__ = "User"

    id: Mapped[UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150))
    password: Mapped[bytes] = mapped_column(BYTEA())
    role: Mapped[UserRole]
