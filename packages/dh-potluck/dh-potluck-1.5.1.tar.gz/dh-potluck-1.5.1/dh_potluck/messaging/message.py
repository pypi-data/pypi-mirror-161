from typing import Dict

from confluent_kafka.cimpl import Message as KafkaMessage


class Message(object):

    _topic: str
    _value: Dict
    _raw_message: KafkaMessage

    def __init__(self, topic: str, value: Dict, raw_message: KafkaMessage):
        """
        :param topic: The topic the message came from
        :param value: The message value
                      {'message_type': str, 'message_time': DateTime, 'payload': str}
        :param raw_message: The raw kafka message object
        """
        self._topic = topic
        self._value = value
        self._raw_message = raw_message

    def topic(self) -> str:
        return self._topic

    def value(self) -> Dict:
        return self._value

    def raw_message(self) -> KafkaMessage:
        return self._raw_message
