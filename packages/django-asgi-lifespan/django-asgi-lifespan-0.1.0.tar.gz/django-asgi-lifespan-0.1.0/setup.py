# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_asgi_lifespan',
 'tests',
 'tests.django_test_application',
 'tests.django_test_application.test_app']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4,<5']

setup_kwargs = {
    'name': 'django-asgi-lifespan',
    'version': '0.1.0',
    'description': 'Django ASGI handler with Lifespan Protocol support.',
    'long_description': '# Django ASGI Handler with Lifespan protocol support\n\n[![pypi](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pypi](https://img.shields.io/pypi/v/django-asgi-lifespan.svg)](https://pypi.org/project/django-asgi-lifespan/)\n[![python](https://img.shields.io/pypi/pyversions/django-asgi-lifespan.svg)](https://pypi.org/project/django-asgi-lifespan/)\n[![Build Status](https://github.com/illagrenan/django-asgi-lifespan/actions/workflows/development.yml/badge.svg)](https://github.com/illagrenan/django-asgi-lifespan/actions/workflows/development.yml)\n[![codecov](https://codecov.io/gh/illagrenan/django-asgi-lifespan/branch/main/graphs/badge.svg)](https://codecov.io/github/illagrenan/django-asgi-lifespan)\n\n* Documentation: <https://illagrenan.github.io/django-asgi-lifespan>\n* PyPI: <https://pypi.org/project/django-asgi-lifespan/>\n* License: MIT\n    \n## Features\n\n* This package contains a subclass of the standard Django `ASGIHandler` that can\n  handle [ASGI Lifespan Protocol](https://asgi.readthedocs.io/en/latest/specs/lifespan.html). (Note: there is no change in handling HTTP requests.)\n* [Startup](https://asgi.readthedocs.io/en/latest/specs/lifespan.html#startup-receive-event)\n  and [Shutdown](https://asgi.readthedocs.io/en/latest/specs/lifespan.html#shutdown-receive-event) Lifespan events are\n  converted to [Django signals](https://docs.djangoproject.com/en/4.0/topics/signals/).\n* Signal **receivers can be awaited**. This way it is possible for example to\n  create [aiohttp ClientSession](https://docs.aiohttp.org/en/stable/client_reference.html)\n  /[httpx client](https://www.python-httpx.org/async/) when the application starts and close these resources safely when\n  the application shuts down. This concept is similar to events in\n  FastAPI (<https://fastapi.tiangolo.com/advanced/events/>).\n\n## Quickstart\n\n**:warning: This package is experimental. Lifespan signals work correctly only under uvicorn.**\n\n1. Install the package. Only Python 3.10 and Django 4 are supported. \n\n    ``` console\n    $ pip install --upgrade django-asgi-lifespan\n    ```\n\n2. Modify `asgi.py` to use a ASGI Lifespan compatible handler.\n\n    ``` py title="asgi.py"\n    from django_asgi_lifespan.asgi import get_asgi_application\n    \n    django_application = get_asgi_application()\n    \n    \n    async def application(scope, receive, send):\n        if scope["type"] in {"http", "lifespan"}:\n            await django_application(scope, receive, send)\n        else:\n            raise NotImplementedError(f"Unknown scope type {scope[\'type\']}")\n    ```\n\n3. Subscribe your (async) code to the `asgi_startup` and `asgi_shutdown` Django signals that are sent when the server starts/shuts down. [See usage](https://illagrenan.github.io/django-asgi-lifespan/usage/) for a more advanced code sample.\n\n    ``` py title="handlers.py" \n    import asyncio\n    \n    import httpx\n    \n    HTTPX_CLIENT = None\n    _signal_lock = asyncio.Lock()\n    \n    \n    async def create_httpx_client():\n        global HTTPX_CLIENT\n    \n        async with _signal_lock:\n            if not HTTPX_CLIENT:\n                HTTPX_CLIENT = httpx.AsyncClient()\n    \n    \n    async def close_httpx_client():\n        if isinstance(HTTPX_CLIENT, httpx.AsyncClient):\n            await asyncio.wait_for(asyncio.create_task(HTTPX_CLIENT.aclose()), timeout=5.0)\n \n    ```\n\n    ``` py title="apps.py" \n    from django.apps import AppConfig\n\n    from django_asgi_lifespan.signals import asgi_shutdown, asgi_startup\n    from .handlers_quickstart import close_httpx_client, create_httpx_client\n    \n    \n    class ExampleAppConfig(AppConfig):\n        def ready(self):\n            asgi_startup.connect(create_httpx_client)\n            asgi_shutdown.connect(close_httpx_client)\n    ```\n\n4. Use some resource (in this case the HTTPX client) e.g. in views.\n\n    ``` py title="views.py" \n    from django.http import HttpResponse\n\n    from . import handlers\n    \n    \n    async def my_library_view(*_) -> HttpResponse:\n        external_api_response = await handlers_quickstart.HTTPX_CLIENT.get("https://www.example.com/")\n    \n        return HttpResponse(f"{external_api_response.text[:42]}", content_type="text/plain")\n\n    ```\n\n5. Run uvicorn:\n\n   :warning: Lifespan protocol is not supported if you run uvicorn via gunicorn using [`worker_class`](https://docs.gunicorn.org/en/stable/settings.html#worker-class): `gunicorn -k uvicorn.workers.UvicornWorker`. See\n   other [limitations](https://illagrenan.github.io/django-asgi-lifespan/limitations/) in the documentation.\n\n    ``` console \n    uvicorn asgi:application --lifespan=on --port=8080\n    ```\n',
    'author': 'Václav Dohnal',
    'author_email': 'vaclav.dohnal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/illagrenan/django-asgi-lifespan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
