# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wsrouter']

package_data = \
{'': ['*'], 'wsrouter': ['static/*']}

install_requires = \
['boltons>=21.0.0,<22.0.0',
 'orjson>=3.7.1,<4.0.0',
 'shortuuid>=1.0.9,<2.0.0',
 'starlette>=0.20.1,<0.21.0']

extras_require = \
{'docs': ['Sphinx>=5.1.1,<6.0.0', 'sphinx-immaterial>=0.8.1,<0.9.0']}

setup_kwargs = {
    'name': 'wsrouter',
    'version': '0.8.1',
    'description': 'Starlette Shared WebSocket Endpoint',
    'long_description': '# WebSocket Router for Starlette\n\nThis package acts as a websocket message router for [Starlette](https://github.com/encode/starlette)\n[WebSocket](https://www.starlette.io/websockets/) connections, permitting socket sharing for\nmultiple client-server connections.\n\nFor installation and usage, [see the documentation](https://selcouth.gitlab.io/wsrouter).\n',
    'author': 'David Morris',
    'author_email': 'gypsysoftware@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/selcouth/wsrouter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
