import logging
from typing import Any, Dict

from marshmallow import Schema

from dh_potluck.messaging import IncomingMessageRouter, MessageHandler, MessageHandlerCallback

LOG = logging.getLogger(__name__)


_HANDLERS = {}


def message_handler(topic: str, schema: Schema):
    """
    Registers this function as a message handler
    :param str topic: Topic to handle
    :param Schema schema: Schema to use to deserialize the message payload
    """

    def decorator_register_message_handler(func: MessageHandlerCallback):
        _HANDLERS[topic] = MessageHandler(schema, func)
        return func

    return decorator_register_message_handler


class MessageConsumerApp(object):

    _router: IncomingMessageRouter

    def __init__(self, consumer_group: str, config_overrides: Dict[str, Any] = None):
        """
        :param str consumer_group: The kafka consumer group to use
        :param dict config_overrides: Any kafka configuration overrides
        """
        self._router = IncomingMessageRouter(_HANDLERS, consumer_group, config_overrides)

    def run(self):
        """
        Start consuming messages. On new messages, use the registered message_handler to handle it.
        :return: None
        """
        self._router.run()
