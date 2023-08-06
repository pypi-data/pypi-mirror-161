from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean, String


class TableDateMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(length=36), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = Column(String(length=36), nullable=False)


class TableSoftDeleteMixin:
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, default=None, nullable=True)
    deleted_by = Column(String(length=36), default=None, nullable=True)
