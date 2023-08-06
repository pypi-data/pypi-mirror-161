import logging

from aio_pika import ExchangeType, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection, AbstractExchange, AbstractRobustChannel, AbstractMessage
from aio_pika.message import ReturnedMessage
from dddmisc import DDDEvent

logger = logging.getLogger('dddmisc_rmq.event_transport')


class EventPublisher:
    _channel: AbstractRobustChannel
    _exchange: AbstractExchange

    def __init__(self, user_id: str, service_name: str):
        self._service_name = service_name
        self._user_id = user_id
        self._is_ready = False

    @property
    def is_ready(self):
        return self._is_ready

    async def start(self, connection: AbstractRobustConnection):
        self._channel = await connection.channel(publisher_confirms=True)
        self._channel.return_callbacks.add(self._on_message_returned)
        self._channel.close_callbacks.add(self._on_close_channel)
        self._channel.reopen_callbacks.add(self._on_reopen_channel)
        self._exchange = await self._channel.declare_exchange(f'{self._service_name}_events',
                                                              type=ExchangeType.TOPIC, durable=True)
        self._is_ready = True

    async def stop(self, exc: BaseException = None):
        await self._channel.close(exc)
        self._is_ready = False

    async def publish(self, event: DDDEvent):
        if not self.is_ready:
            raise RuntimeError(f'Publisher "{self._service_name}" is not ready.')
        message = self.serialize(event)
        routing_key = f'{event.__domain__}.{type(event).__name__}'
        result = await self._exchange.publish(message, routing_key)
        return result

    def serialize(self, event: DDDEvent) -> AbstractMessage:
        return Message(
            event.dumps().encode(),
            timestamp=event.__timestamp__,
            content_type='application/json',
            delivery_mode=DeliveryMode.PERSISTENT,
            message_id=str(event.__reference__),
            type='Event',
            user_id=self._user_id,
        )

    @staticmethod
    def _on_message_returned(channel: AbstractRobustChannel, message: ReturnedMessage):
        logger.info("Message has been returned", extra={'payload': repr(message.body),
                                                        'message_info': message.info()})

    def _on_close_channel(self, *args, **kwargs):
        self._is_ready = False
        logger.debug("Event publisher channel is close")

    def _on_reopen_channel(self, *args, **kwargs):
        logger.debug("Event publisher channel is reopened")
        self._is_ready = True
