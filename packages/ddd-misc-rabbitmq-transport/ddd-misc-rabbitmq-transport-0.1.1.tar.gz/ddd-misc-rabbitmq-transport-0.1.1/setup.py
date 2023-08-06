# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dddmisc_rmq', 'dddmisc_rmq.events_transport']

package_data = \
{'': ['*']}

install_requires = \
['aio-pika>=8.0.3,<9.0.0', 'ddd-misc==0.8.1', 'python-environ>=0.4.54,<0.5.0']

setup_kwargs = {
    'name': 'ddd-misc-rabbitmq-transport',
    'version': '0.1.1',
    'description': '',
    'long_description': "# RabbitMQ transport for Domain-driven Design Misc\n\nПакет предоставляет транспортную надстройку на `MessageBus` пакета [`ddd-misc`](https://pypi.org/project/ddd-misc/)\nдля осуществления публикации событий и RPC-вызова команд посредством брокера RabbitMQ.\n\n## Классы\n\n**Классы объектов**\n- `AsyncRMQEventTransport` - асинхронный класс транспорта выполняющий публикацию и подписку на события\n- `SyncRMQEventTransport` - синхронный класс транспорта выполняющий публикацию и подписку на события\n\n\nСигнатура инициализации классов:\n\n`AsyncRMQEventTransport(messagebus: AsyncMessageBus, url: t.Union[str, URL], service_name, **kwargs)`\n\n`SyncRMQEventTransport(messagebus: MessageBus, url: t.Union[str, URL], service_name, **kwargs)`\n\n- `messagebus` - инстанс класса шины сообщений используемой в сервисе\n- `url` - урл подключения к брокеру RabbitMQ формата `amqps://user:password@broker-host/vhost`\n- `service_name` - наименование микросервиса, используется: \n  - для формирования наименования exchange в который будет осуществляться публикация событий на основании шаблона `<service_name>_events`\n  - используется в качестве наименования очереди для подписки на события по умолчанию\n- `prefetch_count` - максимальное количество одновременно обрабатываемых событий\n- `**kwargs` - дополнительно возможные расширения параметризации класса транспорта\n\n_свойства_\n- `is_ready` - готовность класса принимать/отправлять события\n- `service_name` - наименование сервиса заданное при ининциализации\n\n_методы_\n- `def register(events: *t.Type[DDDEvent])` - регистрация событий для публикации через брокер\n  - `events` - классы событий\n- `def consume_to_service(service_name: str, queue_name: str = None)` - метод подписки на все события публикуемые заданным микросервисом\n  - `service_name` - наименование стороннего сервиса, на exchange которого будет осуществлена подписка\n  - `queue_name` - специфичное наименование очереди. При передаче пустой строки будет осуществлена посредством временной очереди\n- `def consume_to_domain(service_name: str, domain: str, queue_name: str = None)` - метод подписки на все события указанного домена, публикуемые заданным микросервисом\n  - `service_name` - наименование стороннего сервиса, на exchange которого будет осуществлена подписка\n  - `domain` - наименование домена на события которого будет осуществлена подписка\n  - `queue_name` - специфичное наименование очереди. При передаче пустой строки будет осуществлена посредством временной очереди\n- `def consume_to_event(service_name: str, event: t.Type[DDDEvent], queue_name: str = None)` - метод подписки на конкретное событие, публикуемое данным сервисом\n  - `service_name` - наименование стороннего сервиса, на exchange которого будет осуществлена подписка\n  - `event` - наименование домена на события которого будет осуществлена подписка\n  - `queue_name` - специфичное наименование очереди. При передаче пустой строки будет осуществлена посредством временной очереди\n\n_!!! Допускается подписка на события собственного сервиса при этом события полученные через брокер \nне будут повторно опубликованы в брокер сообщений_\n\n\n## Примеры использования\n\n**Пример использования для публикации событий**\n```python\nfrom sample_project.bootstap import messagebus\nfrom sample_project.domain.events import CompleteEvent, SpecificEvent\nfrom dddmisc_rmq import AsyncRMQEventTransport\n\ntransport = AsyncRMQEventTransport(messagebus, 'amqps://guest:guest@localhost/vhost', 'sample_project')\ntransport.register(CompleteEvent, SpecificEvent)\n```\n\n**Пример использования для подписки на события**\n```python\nfrom sample_project.bootstap import messagebus\nfrom other_project.events import CompleteEvent, SpecificEvent\nfrom dddmisc_rmq import AsyncRMQEventTransport\n\ntransport = AsyncRMQEventTransport(messagebus, 'amqps://guest:guest@localhost/vhost', 'sample_project')\ntransport.consume_to_event('other_project', CompleteEvent)  # Подписка на событие CompleteEvent через постоянную очередь sample_project\ntransport.consume_to_domain('other_project', 'other_domain', '')  # Экслюзивная подписка на события домена через временную очередь\ntransport.consume_to_service('other_project', 'sample-queue')  # Подписка на все события домена через постоянную очередь sample-queue\n\n```\n\n**Пример одновренменной подписки и публикации событий**\n```python\nfrom sample_project.bootstap import messagebus\nfrom sample_project.events import SuccessEvent\nfrom other_project.events import CompleteEvent, SpecificEvent\nfrom dddmisc_rmq import AsyncRMQEventTransport\n\ntransport = AsyncRMQEventTransport(messagebus, 'amqps://guest:guest@localhost/vhost', 'sample_project')\ntransport.register(SuccessEvent)\ntransport.consume_to_event('other_project', CompleteEvent)  # Подписка на событие CompleteEvent через постоянную очередь sample_project\ntransport.consume_to_domain('other_project', 'other_domain', '')  # Экслюзивная подписка на события домена через временную очередь\ntransport.consume_to_service('other_project', 'sample-queue')  # Подписка на все события домена через постоянную очередь sample-queue\n\n```\n\n## Changelog \n**0.1.1**\n\n- Change exchange type from `Fanout` to `Topic`\n\n**0.1.0**\n\n- First release\n\n\n\n\n",
    'author': 'Vladislav Vorobyov',
    'author_email': 'vladislav.vorobyov@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
