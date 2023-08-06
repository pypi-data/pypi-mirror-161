# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['a2wsgi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'a2wsgi',
    'version': '1.5.0',
    'description': 'Convert WSGI app to ASGI app or ASGI app to WSGI app.',
    'long_description': "# a2wsgi\n\nConvert WSGI app to ASGI app or ASGI app to WSGI app.\n\nPure Python. Only depend on the standard library.\n\nCompared with other converters, the advantage is that a2wsgi will not accumulate the requested content or response content in the memory, so you don't have to worry about the memory limit caused by a2wsgi. This problem exists in converters implemented by uvicorn/startlette or hypercorn.\n\n## Install\n\n```\npip install a2wsgi\n```\n\n## How to use\n\nConvert WSGI app to ASGI app:\n\n```python\nfrom a2wsgi import WSGIMiddleware\n\nASGI_APP = WSGIMiddleware(WSGI_APP)\n```\n\nConvert ASGI app to WSGI app:\n\n```python\nfrom a2wsgi import ASGIMiddleware\n\nWSGI_APP = ASGIMiddleware(ASGI_APP)\n```\n\n## Benchmark\n\nRun `pytest ./benchmark.py -s` to compare the performance of `a2wsgi` and `uvicorn.middleware.wsgi.WSGIMiddleware` / `asgiref.wsgi.WsgiToAsgi`.\n\n## Why a2wsgi\n\n### Convert WSGI app to ASGI app\n\nYou can convert an existing WSGI project to an ASGI project to make it easier to migrate from WSGI applications to ASGI applications.\n\n### Convert ASGI app to WSGI app\n\nThere is a lot of support for WSGI. Converting ASGI to WSGI, you will be able to use many existing services to deploy ASGI applications.\n",
    'author': 'abersheeran',
    'author_email': 'me@abersheeran.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abersheeran/a2wsgi',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
