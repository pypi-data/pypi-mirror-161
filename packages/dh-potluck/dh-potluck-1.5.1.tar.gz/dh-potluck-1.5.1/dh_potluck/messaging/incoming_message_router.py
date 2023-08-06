from typing import Any, Dict, Protocol

from ddtrace import tracer
from marshmallow import Schema

from dh_potluck.messaging import Message, MessageConsumer


class MessageHandlerCallback(Protocol):
    def __call__(self, message_type: str, payload: Dict) -> bool:
        pass


class MessageHandler(object):
    _schema: Schema
    _handler: MessageHandlerCallback

    def __init__(self, schema: Schema, handler: MessageHandlerCallback):
        """
        :param Schema schema: marshmallow schema to use when deserializing the message
        :param MessageHandlerCallback handler: Function to handle each message. Return True to
                                               commit the message, False to continue without
                                               committing. Raise an error if you are unable to
                                               handle the message.
        """
        self._schema = schema
        self._handler = handler

    def deserialize_message(self, message: Message) -> Dict:
        return self._schema.loads(message.value()['payload'])

    def handle(self, message_type: str, payload: Dict) -> bool:
        should_commit = self._handler(message_type, payload)
        if should_commit is None:
            return True
        return should_commit


class NoHandlerException(Exception):
    def __init__(self, topic):
        self.topic = topic
        self.message = f'No handler for topic: {topic}'
        super().__init__(self.message)


class IncomingMessageRouter(object):
    _handlers: Dict[str, MessageHandler]
    _consumer: MessageConsumer

    def __init__(
        self,
        handlers: Dict[str, MessageHandler],
        consumer_group: str,
        config_overrides: Dict[str, Any] = None,
    ):
        """
        :param dict handlers: Dictionary of topic -> MessageHandler
        :param str consumer_group: The kafka consumer group to use
        :param dict config_overrides: Any kafka configuration overrides
        """
        self._consumer = MessageConsumer(consumer_group, config_overrides)
        self._handlers = handlers

    def run(self) -> None:
        """
        Start consuming messages. On new messages, check the handlers map, if the message's topic
        matches a handler key, use it to serialize the message, and handle it.
        :return: None
        """
        self._consumer.subscribe(list(self._handlers.keys()))
        try:
            for message in self._consumer.get_messages():
                self._handle_message(message)
        finally:
            self._consumer.shutdown()

    def _handle_message(self, message: Message) -> None:
        topic = message.topic()
        handler = self._handlers.get(topic)
        if not handler:
            raise NoHandlerException(topic)
        payload = handler.deserialize_message(message)
        message_type = message.value()['message_type']
        with tracer.trace('kafka.consume', resource=f'{topic} {message_type}'):
            should_commit = handler.handle(message_type, payload)
        if should_commit:
            self._consumer.commit(message)
