from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UUID, Uuid

from core.db import Base
from auth.schemas import UserRole


class User(Base):
    __tablename__ = "User"
    
    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150))
    password: Mapped[str]
    role: Mapped[UserRole]