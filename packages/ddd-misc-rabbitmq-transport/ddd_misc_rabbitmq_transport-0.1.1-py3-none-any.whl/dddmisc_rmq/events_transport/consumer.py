import logging
import typing as t
from collections import defaultdict

from aio_pika import ExchangeType
from aio_pika.abc import (AbstractRobustConnection, AbstractRobustChannel,
                          AbstractIncomingMessage,
                          AbstractRobustExchange, AbstractRobustQueue)
from dddmisc import DDDEvent, get_message_class
from dddmisc.exceptions import UnregisteredMessageClass, JsonDecodeError, ValidationError

logger = logging.getLogger('dddmisc_rmq.event_transport')

Queue = Service = str
Domain = Event = t.Optional[str]


class ConsumerConfig:

    def __init__(self):
        self._config: t.Dict[Queue, t.Set[t.Tuple[Service, Domain, Event]]] = defaultdict(set)

    def add(self, service_name: str, domain: str, event_type: str, queue_name: str):
        if domain is None and event_type is None:
            new_set = {(sn, dn, et) for sn, dn, et in self._config[queue_name] if sn != service_name}
            new_set.add((service_name, None, None))
            self._config[queue_name] = new_set
        elif (event_type is None
              and (service_name, None, None) not in self._config[queue_name]):
            new_set = {(sn, dn, et) for sn, dn, et in self._config[queue_name]
                       if sn != service_name or (sn == service_name and dn != domain)}
            new_set.add((service_name, domain, None))
            self._config[queue_name] = new_set
        elif ((service_name, None, None) not in self._config[queue_name]
              and (service_name, domain, None) not in self._config[queue_name]):
            self._config[queue_name].add((service_name, domain, event_type))

    def __getitem__(self, item: str) -> t.Dict[str, t.List[str]]:
        result = defaultdict(list)
        if item in self._config:
            for exchange, domain, event_type in self._config[item]:
                result[f'{exchange}_events'].append(self._make_routing_key(domain, event_type))
            return dict(result)
        raise KeyError(item)

    def __iter__(self):
        return iter(self._config.keys())

    @staticmethod
    def _make_routing_key(domain: t.Optional[str], event_type: t.Optional[str]):
        if domain is None and event_type is None:
            return '*.*'
        elif event_type is None:
            return f'{domain}.*'
        else:
            return f'{domain}.{event_type}'


class EventConsumer:
    _channel: AbstractRobustChannel

    def __init__(self, handler: t.Callable[[DDDEvent], t.Awaitable], *, prefetch_count=200):
        self._handler = handler
        self._config = ConsumerConfig()
        self._prefetch_count = prefetch_count
        self._is_ready = False

    @property
    def is_ready(self):
        return self._is_ready

    def add_route(self, service_name: str, domain: str = None, event_type: str = None, queue_name: str = None):
        self._config.add(service_name, domain, event_type, queue_name)

    @staticmethod
    def deserialize(message: AbstractIncomingMessage) -> t.Optional[DDDEvent]:
        try:
            message_class: t.Type[DDDEvent] = get_message_class(message.routing_key)  # noqa
            if not message.type or message.type.lower() != 'event':
                logger.warning("Invalid event message type",
                               extra={'payload': repr(message.body), 'message_info': message.info()})
                return
            event = message_class.loads(message.body, message.message_id, message.timestamp)
            setattr(event, '__handle_by_rmq_event_transport__', True)
            return event
        except UnregisteredMessageClass:
            logger.warning("Event not registered in messages collection",
                           extra={'payload': repr(message.body), 'message_info': message.info()})
        except JsonDecodeError:
            logger.error("Invalid message format",
                         extra={'payload': repr(message.body), 'message_info': message.info()})
        except ValidationError as err:
            logger.error("Validation event error",
                         extra={'payload': repr(message.body), 'message_info': message.info(),
                                'exc_data': dict(err.extra)})
        except Exception as err:  # noqa
            logger.exception("Unknown event deserialization error",
                             extra={'payload': repr(message.body), 'message_info': message.info()})

    async def start(self, connection: AbstractRobustConnection):
        self._channel = await connection.channel()
        self._channel.close_callbacks.add(self._on_close_channel)
        self._channel.reopen_callbacks.add(self._on_reopen_channel)
        await self._channel.set_qos(prefetch_count=self._prefetch_count)
        for queue_name in self._config:
            queue = await self._declare_queue(self._channel, queue_name)
            for exchange, routing_keys in self._config[queue_name].items():
                exchange = await self._declare_exchange(self._channel, exchange)
                for routing_key in routing_keys:
                    await queue.bind(exchange, routing_key)
            await queue.consume(self._callback)
        self._is_ready = True

    async def stop(self, exc: BaseException = None):
        await self._channel.close(exc)
        self._is_ready = False

    @staticmethod
    async def _declare_queue(channel: AbstractRobustChannel, queue_name: str) -> AbstractRobustQueue:
        if queue_name:
            queue = await channel.declare_queue(queue_name, durable=True, exclusive=False, auto_delete=False)
        else:
            queue = await channel.declare_queue()
        return queue

    @staticmethod
    async def _declare_exchange(channel: AbstractRobustChannel, exchange_name: str) -> AbstractRobustExchange:
        exchange = await channel.declare_exchange(exchange_name,
                                                  type=ExchangeType.TOPIC, durable=True)
        return exchange

    async def _callback(self, message: AbstractIncomingMessage):
        async with message.process():
            event = self.deserialize(message)
            if event is not None:
                await self._handler(event)

    def _on_close_channel(self, *args, **kwargs):
        self._is_ready = False
        logger.debug("Event consume channel is close")

    def _on_reopen_channel(self, *args, **kwargs):
        logger.debug("Event consume channel is reopened")
        self._is_ready = True
