from abc import ABC, abstractmethod
from typing import Optional

from hrthy_core.events.events.base_event import BaseEvent
from hrthy_core.models.base_model import BaseEventModel


class BaseEventRepositoryAbstract(ABC):
    @abstractmethod
    def get_first_event_to_send(self) -> Optional[BaseEventModel]:
        raise NotImplementedError()

    @abstractmethod
    def set_event_as_sent(self, event: BaseEventModel) -> BaseEventModel:
        raise NotImplementedError()
