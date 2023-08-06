import json
from enum import Enum
from uuid import UUID

from kafka import KafkaProducer

from hrthy_core.events.event import BaseEvent
from hrthy_core.events.topic import Topic


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return str(obj.value)
        return json.JSONEncoder.default(self, obj)



class BaseProducer:
    TOPIC: Topic = None

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=self._get_brokers(),
            value_serializer=lambda v: json.dumps(v, cls=UUIDEncoder).encode('utf-8')
        )

    def _get_topic(self) -> str:
        if type(self.TOPIC) is not Topic:
            raise Exception('Invalid TOPIC. Please make sure you have it set')
        return self.TOPIC.value

    def _get_brokers(self) -> list:
        return []

    def send(self, event: BaseEvent):
        self.producer.send(self._get_topic(), event.dict())

    def flush(self):
        self.producer.flush()

