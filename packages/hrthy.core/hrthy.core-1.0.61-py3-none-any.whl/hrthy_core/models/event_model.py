from pydantic import Json
from sqlalchemy import Column, String, Boolean, DateTime


class BaseEventModel:
    __tablename__ = 'hrthy_event'
    id = Column(String(length=36), primary_key=True)
    topic = Column(String(255), nullable=False, unique=False, index=True)
    event = Column(Json, nullable=False, unique=False, index=False)
    sent = Column(Boolean, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
