import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str]
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[Optional[str]] = mapped_column(nullable=True)
    verification_token: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default=lambda: str(uuid.uuid4())
    )
    reset_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")

    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="user")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str]
    phone: Mapped[str]
    birthday: Mapped[datetime]
    additional_data: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="contacts")
