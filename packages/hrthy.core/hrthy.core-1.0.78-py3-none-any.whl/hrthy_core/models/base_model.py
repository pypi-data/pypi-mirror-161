from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean, String, Text, INTEGER


class TableDateMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(length=36), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = Column(String(length=36), nullable=False)


class TableSoftDeleteMixin:
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, default=None, nullable=True)
    deleted_by = Column(String(length=36), default=None, nullable=True)


class BaseEventModel:
    __tablename__ = 'hrthy_event'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False, unique=False, index=True)
    event_type = Column(String(255), nullable=False, unique=False, index=False)
    event = Column(Text, nullable=False, unique=False, index=False)
    sent = Column(Boolean, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True, index=False)
