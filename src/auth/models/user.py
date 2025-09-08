from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import BYTEA

from core.db import Base
from auth.schemas import UserRole


class User(Base):
    name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[bytes] = mapped_column(BYTEA())
    role: Mapped[UserRole] = mapped_column(String(20))
