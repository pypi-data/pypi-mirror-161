from time import sleep
from typing import List

from kafka import KafkaProducer
from sqlalchemy.orm import Session

from hrthy_core.events.topic import Topic
from hrthy_core.models.base_model import BaseEventModel
from hrthy_core.models.transaction import transaction
from hrthy_core.repository.event.repository_abstract import BaseEventRepositoryAbstract
from hrthy_core.utils.utils import logger


class BaseProducer:
    DB: Session = None
    BROKERS: List[str] = None
    REPOSITORY: BaseEventRepositoryAbstract = None

    _event_found = False

    def __init__(self):
        if any([
            self.DB is None,
            self.BROKERS is None,
            self.REPOSITORY is None
        ]):
            raise RuntimeError("Producer Wrong Configuration.")
        self.producer = KafkaProducer(
            bootstrap_servers=self.BROKERS,
        )

    def _send(self, event: BaseEventModel):
        self.producer.send(event.topic, event.event.encode('utf-8'))
        self._flush()

    def _flush(self):
        self.producer.flush()

    def start(self):
        while True:
            try:
                sleep(0.3 if not self._event_found else 0)
                with transaction(self.DB):
                    event: BaseEventModel = self.REPOSITORY.get_first_event_to_send()
                    if not event:
                        self._event_found = False
                        continue
                    self._event_found = True
                    self._send(event)
                    self.REPOSITORY.set_event_as_sent(event=event)
            except Exception as ex:
                logger.exception(ex)
