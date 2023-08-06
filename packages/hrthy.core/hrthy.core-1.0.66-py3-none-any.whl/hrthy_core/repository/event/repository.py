import json
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from hrthy_core.events.event import BaseEvent
from hrthy_core.models.event_model import BaseEventModel
from sqlalchemy import false
from sqlalchemy.orm import Session, Query

from hrthy_core.repository.event.repository_abstract import EventRepositoryAbstract


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return str(obj.value)
        return json.JSONEncoder.default(self, obj)


class EventRepository(EventRepositoryAbstract):
    model = BaseEventModel

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def get_event(self, event_id: UUID) -> Optional[BaseEventModel]:
        query: Query = self.db.query(BaseEventModel) \
            .filter(BaseEventModel.id == str(event_id)) \
            .filter(BaseEventModel.sent == false()) \
            .with_for_update()
        return query.first()

    def send_event(self, topic: str, even_to_send: BaseEvent) -> BaseEventModel:
        event = self.model()
        event.id = even_to_send.payload.id
        event.topic = topic
        event.event_type = even_to_send.type
        event.event = even_to_send.json().encode('utf-8')
        event.created_at = datetime.utcnow()
        event.sent = False
        event.sent_at = None
        self.db.add(event)
        return event

    def set_event_as_sent(self, event: BaseEventModel) -> BaseEventModel:
        event.sent = True
        event.sent_at = datetime.utcnow()
        self.db.add(event)
        return event

