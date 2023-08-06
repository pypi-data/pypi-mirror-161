from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text


class BaseEventModel:
    __tablename__ = 'hrthy_event'
    id = Column(String(length=36), primary_key=True)
    topic = Column(String(255), nullable=False, unique=False, index=True)
    event_type = Column(String(255), nullable=False, unique=False, index=False)
    event = Column(Text, nullable=False, unique=False, index=False)
    sent = Column(Boolean, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True, index=False)
