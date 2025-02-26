from sqlalchemy import Boolean, Column, Integer, String
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_admin = Column(Boolean, default=False)  # Добавляем это поле
    disabled = Column(Boolean, default=False)