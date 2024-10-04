# app/models.py
from sqlalchemy import Column, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID, primary_key=True, index=True)
    title = Column(String, index=True)
    created_time = Column(TIMESTAMP(timezone=True))
    modified_time = Column(TIMESTAMP(timezone=True))
    is_disabled = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    default_language = Column(String)
