from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from hrthy_core.events.event import BaseEvent
from hrthy_core.models.event_model import BaseEventModel


class BaseEventRepositoryAbstract(ABC):
    @abstractmethod
    def get_event(self, event_id: UUID) -> Optional[BaseEventModel]:
        raise NotImplementedError()

    @abstractmethod
    def send_event(self, topic: str, even_to_send: BaseEvent) -> BaseEventModel:
        raise NotImplementedError()

    @abstractmethod
    def set_event_as_sent(self, event: BaseEventModel) -> BaseEventModel:
        raise NotImplementedError()
