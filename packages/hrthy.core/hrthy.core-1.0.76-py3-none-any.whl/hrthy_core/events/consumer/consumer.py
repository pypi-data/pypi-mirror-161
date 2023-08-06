import json

from kafka import KafkaConsumer

from hrthy_core.events.topic import TopicGroup, Topic


class BaseConsumer:
    TOPICS: list = []
    TOPIC_GROUP: TopicGroup = None

    def _get_topics(self) -> list:
        if type(self.TOPICS) is not list:
            raise Exception('Invalid TOPICS. Please make sure you have it set')
        for topic in self.TOPICS:
            if type(topic) is not Topic:
                raise Exception('Invalid TOPIC in the list. Please make sure to use one of the available topics')
        return [t.value for t in self.TOPICS]

    def _get_topics_group(self) -> str:
        if type(self.TOPIC_GROUP) is not TopicGroup:
            raise Exception('Invalid TOPIC_GROUP. Please make sure you have it set')
        return self.TOPIC_GROUP.value

    def _get_brokers(self) -> list:
        return self.TOPICS

    def _callback(self, message) -> None:
        pass

    def start(self) -> None:
        consumer = KafkaConsumer(
            *self._get_topics(),
            group_id=self._get_topics_group(),
            value_deserializer=lambda v: json.loads(v),
            bootstrap_servers=self._get_brokers(),
            enable_auto_commit=True
        )
        for message in consumer:
            self._callback(message)
