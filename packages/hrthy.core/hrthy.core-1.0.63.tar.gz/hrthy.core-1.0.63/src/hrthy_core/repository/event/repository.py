import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from hrthy_core.events.event import BaseEvent
from hrthy_core.models.event_model import BaseEventModel
from sqlalchemy import false
from sqlalchemy.orm import Session, Query

from hrthy_core.repository.event.repository_abstract import EventRepositoryAbstract


class EventRepository(EventRepositoryAbstract):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def get_event(self, event_id: UUID) -> Optional[BaseEventModel]:
        query: Query = self.db.query(BaseEventModel) \
            .filter(BaseEventModel.id == str(event_id)) \
            .filter(BaseEventModel.sent == false()) \
            .with_for_update()
        return query.first()

    def send_event(self, even_to_send: BaseEvent) -> BaseEventModel:
        event: BaseEventModel = BaseEventModel()
        event.id = even_to_send.payload.id
        event.event_type = even_to_send.type
        event.event = json.dumps(even_to_send)
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

