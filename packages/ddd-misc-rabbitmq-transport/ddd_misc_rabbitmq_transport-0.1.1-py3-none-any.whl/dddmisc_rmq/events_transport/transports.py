import abc
import typing as t

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from dddmisc import DDDEvent, AsyncMessageBus, MessageBus
from dddmisc.messagebus.abstract import AbstractMessagebus
from dddmisc.repository.repository import AbstractRepository
from dddmisc.unit_of_work import AbstractUnitOfWork
from dddmisc.tools import ThreadLoop
from yarl import URL

from dddmisc_rmq.events_transport.consumer import EventConsumer
from dddmisc_rmq.events_transport.publisher import EventPublisher


class NullUOW(AbstractUnitOfWork):
    pass


class NullRepository(AbstractRepository):
    pass


class AbstractRMQEventTransport(abc.ABC):
    _connection: AbstractRobustConnection
    _publisher = None
    _consumer = None

    def __init__(self, messagebus: AbstractMessagebus, url: t.Union[str, URL], service_name: str, **kwargs):
        self._service_name = service_name
        self._kwargs = kwargs
        self._messagebus = messagebus
        self._messagebus.subscribe(messagebus.SignalTypes.PRE_START, self.pre_start_handler)
        self._messagebus.subscribe(messagebus.SignalTypes.POST_START, self.post_start_handler)
        self._messagebus.subscribe(messagebus.SignalTypes.PRE_STOP, self.pre_stop_handler)
        self._messagebus.subscribe(messagebus.SignalTypes.POST_STOP, self.post_stop_handler)

    @property
    def service_name(self):
        return self._service_name

    @property
    @abc.abstractmethod
    def is_ready(self) -> bool:
        ...

    def register(self, *events: t.Type[DDDEvent]):
        for event in events:
            self._messagebus.register(event, self._publisher_handler,
                                      unit_of_work=NullUOW, repository=NullRepository)

    def consume_to_service(self, service_name: str, queue_name: str = None):
        self._consume(service_name, queue_name=self._get_queue_name(queue_name))

    def consume_to_domain(self, service_name: str, domain: str, queue_name: str = None):
        self._consume(service_name, domain, queue_name=self._get_queue_name(queue_name))

    def consume_to_event(self, service_name: str, event: t.Type[DDDEvent], queue_name: str = None):
        self._consume(service_name, str(event.__domain__), event.__name__, self._get_queue_name(queue_name))

    def _get_queue_name(self, queue_name: str = None):
        if queue_name is None:
            queue_name = self._service_name
        return queue_name

    @abc.abstractmethod
    def _consume(self, service_name: str, domain: str = None, event_type: str = None, queue_name: str = None):
        ...

    @abc.abstractmethod
    def pre_start_handler(self, messagebus, signal):
        ...

    @abc.abstractmethod
    def post_start_handler(self, messagebus, signal):
        ...

    @abc.abstractmethod
    def pre_stop_handler(self, messagebus, signal, exc: BaseException = None):
        ...

    @abc.abstractmethod
    def post_stop_handler(self, messagebus, signal, exc: BaseException = None):
        ...

    @abc.abstractmethod
    def _publisher_handler(self, event: DDDEvent, uow):
        ...


class AsyncRMQEventTransport(AbstractRMQEventTransport):

    def __init__(self, messagebus: AsyncMessageBus, url: t.Union[str, URL], service_name, **kwargs):
        super(AsyncRMQEventTransport, self).__init__(messagebus, url, service_name, **kwargs)
        self._url = URL(url).with_query(
            {**URL(url).query, **{'name': f'Events transport of "{service_name}" service'}})
        self._publisher = EventPublisher(self._url.user, self.service_name)
        self._consumer = EventConsumer(self._consumer_handler, prefetch_count=kwargs.get('prefetch_count', 200))

    @property
    def is_ready(self) -> bool:
        return self._publisher.is_ready and self._consumer.is_ready

    def _consume(self, service_name: str, domain: str = None, event_type: str = None, queue_name: str = None):
        self._consumer.add_route(service_name, domain, event_type, queue_name)

    async def pre_start_handler(self, messagebus, signal):
        self._connection = await connect_robust(self._url)
        await self._publisher.start(self._connection)

    async def post_start_handler(self, messagebus, signal):
        await self._consumer.start(self._connection)

    async def pre_stop_handler(self, messagebus, signal, exc: BaseException = None):
        await self._consumer.stop(exc)

    async def post_stop_handler(self, messagebus, signal, exc: BaseException = None):
        await self._publisher.stop(exc)
        await self._connection.close(exc)

    async def _publisher_handler(self, event: DDDEvent, uow):
        if hasattr(event, '__handle_by_rmq_event_transport__'):
            return
        await self._publisher.publish(event)

    async def _consumer_handler(self, event: DDDEvent):
        coro = self._messagebus.handle(event)
        if isinstance(coro, t.Awaitable):
            await coro


class SyncRMQEventTransport(AbstractRMQEventTransport, ThreadLoop):

    def __init__(self, messagebus: MessageBus, url: t.Union[str, URL], service_name: str, **kwargs):
        AbstractRMQEventTransport.__init__(self, messagebus, url, service_name, **kwargs)

        self._transport = AsyncRMQEventTransport(messagebus, url, service_name, **kwargs)
        self._messagebus.unsubscribe(messagebus.SignalTypes.PRE_START, self._transport.pre_start_handler)
        self._messagebus.unsubscribe(messagebus.SignalTypes.POST_START, self._transport.post_start_handler)
        self._messagebus.unsubscribe(messagebus.SignalTypes.PRE_STOP, self._transport.pre_stop_handler)
        self._messagebus.unsubscribe(messagebus.SignalTypes.POST_STOP, self._transport.post_stop_handler)
        ThreadLoop.__init__(self)

    @property
    def is_ready(self) -> bool:
        return self._transport.is_ready

    def _consume(self, service_name: str, domain: str = None, event_type: str = None, queue_name: str = None):
        self._transport._consume(service_name, domain, event_type, queue_name)  # noqa

    def _publisher_handler(self, event: DDDEvent, uow):
        self.call_thread_safe(self._transport._publisher_handler, event, uow)  # noqa

    def pre_start_handler(self, messagebus, signal):
        self.start()
        self.call_thread_safe(self._transport.pre_start_handler, messagebus, signal)

    def post_start_handler(self, messagebus, signal):
        self.call_thread_safe(self._transport.post_start_handler, messagebus, signal)

    def pre_stop_handler(self, messagebus, signal, exc: BaseException = None):
        self.call_thread_safe(self._transport.pre_stop_handler, messagebus, signal, exc)

    def post_stop_handler(self, messagebus, signal, exc: BaseException = None):
        self.call_thread_safe(self._transport.post_stop_handler, messagebus, signal, exc)
        self.stop()

