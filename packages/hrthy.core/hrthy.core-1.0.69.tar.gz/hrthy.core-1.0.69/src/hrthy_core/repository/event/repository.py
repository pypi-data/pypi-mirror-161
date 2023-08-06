from datetime import datetime
from typing import Optional

from sqlalchemy import false
from sqlalchemy.orm import Session, Query

from hrthy_core.events.event import BaseEvent
from hrthy_core.models.event_model import BaseEventModel
from hrthy_core.repository.event.repository_abstract import BaseEventRepositoryAbstract


class BaseEventRepository(BaseEventRepositoryAbstract):
    model = BaseEventModel

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def get_first_event_to_send(self) -> Optional[BaseEventModel]:
        query: Query = self.db.query(self.model) \
            .filter(self.model.sent == false()) \
            .order_by(self.model.created_at) \
            .with_for_update()
        return query.first()

    def send_event(self, topic: str, even_to_send: BaseEvent) -> BaseEventModel:
        event = self.model()
        event.id = even_to_send.payload.id
        event.topic = topic
        event.event_type = even_to_send.type
        event.event = even_to_send.json()
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
