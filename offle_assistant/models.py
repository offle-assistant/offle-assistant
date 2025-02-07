from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    func,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship
from offle_assistant.database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Persona(Base):
    __tablename__ = "personas"
    persona_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    persona_name = Column(String(255), nullable=False)
    persona_config = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="personas")
