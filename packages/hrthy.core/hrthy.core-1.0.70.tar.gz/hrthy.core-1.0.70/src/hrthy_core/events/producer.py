from time import sleep
from typing import Callable, List

from kafka import KafkaProducer
from sqlalchemy.orm import Session

from hrthy_core.events.topic import Topic
from hrthy_core.models.event_model import BaseEventModel
from hrthy_core.repository.event.repository_abstract import BaseEventRepositoryAbstract


class BaseProducer:
    DB: Session = None
    TOPIC: Topic = None
    BROKERS: List[str] = None
    TRANSACTION_FN: Callable = None
    REPOSITORY: BaseEventRepositoryAbstract = None

    def __init__(self):
        if any([
            self.DB is None,
            self.TOPIC is None,
            self.BROKERS is None,
            self.REPOSITORY is None,
            self.TRANSACTION_FN is None
        ]):
            raise RuntimeError("Producer Wrong Configuration.")
        self.producer = KafkaProducer(
            bootstrap_servers=self.BROKERS,
        )

    def _send(self, event: BaseEventModel):
        if type(self.TOPIC) is not event.topic:
            raise RuntimeError('Invalid TOPIC. Please make sure you are using the correct Topic.')
        self.producer.send(event.topic, event.event.encode('utf-8'))
        self._flush()

    def _flush(self):
        self.producer.flush()

    def start(self):
        while True:
            sleep(0.2)
            with self.TRANSACTION_FN(self.DB):
                event: BaseEventModel = self.REPOSITORY.get_first_event_to_send()
                self._send(event)
                self.REPOSITORY.set_event_as_sent(event=event)
