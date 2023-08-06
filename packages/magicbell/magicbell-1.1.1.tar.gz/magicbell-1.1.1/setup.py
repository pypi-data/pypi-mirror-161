# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magicbell', 'magicbell.api', 'magicbell.model']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'orjson>=3.7.6,<4.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'magicbell',
    'version': '1.1.1',
    'description': 'Unofficial Python SDK for MagicBell',
    'long_description': '# MagicBell-Python SDK\n\n<p align="center"><img src="https://assets.noteable.io/github/2022-07-29/MB_logo_Purple_2800x660.png" width="50%" alt="magicbell logo purple"></p>\n<p align="center">\nThis SDK provides convenient access to the <a href="https://magicbell.com/docs/rest-api/overview">MagicBell REST API</a> from applications written in Python. \nIt includes helpers for creating notifications, managing users, managing projects, and executing GraphQL.\n</p>\n<p align="center">\n<a href="https://github.com/noteable-io/magicbell-python-sdk/actions/workflows/ci.yaml">\n    <img src="https://github.com/noteable-io/magicbell-python-sdk/actions/workflows/ci.yaml/badge.svg" alt="CI" />\n</a>\n<a href="https://codecov.io/gh/noteable-io/magicbell-python-sdk" > \n <img src="https://codecov.io/gh/noteable-io/magicbell-python-sdk/branch/main/graph/badge.svg?token=RGNWOIPWC0" alt="codecov code coverage"/> \n </a>\n<img alt="PyPI - License" src="https://img.shields.io/pypi/l/magicbell" />\n<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/magicbell" />\n<img alt="PyPI" src="https://img.shields.io/pypi/v/magicbell">\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\n---------\n\nThis is an unofficial Python SDK for [MagicBell](https://magicbell.com) open sourced with ❤️ by <a href="https://noteable.io">Noteable</a>, a collaborative notebook platform that enables teams to use and visualize data, together.\n\n[Install](#installation) | [Getting Started](#getting-started) | [Examples](./examples) | [License](./LICENSE) | [Code of Conduct](./CODE_OF_CONDUCT.md) | [Contributing](./CONTRIBUTING.md)\n\n\n## Requirements\n\nPython 3.8+\n\n## Installation\n\n### Poetry\n\n```shell\npoetry add magicbell\n```\n\nThen import the package:\n\n```python\nimport magicbell\n```\n\n### Pip\n```shell\npip install magicbell\n```\n\nThen import the package:\n\n```python\nimport magicbell\n```\n\n## Getting Started\n\n```python\nimport magicbell\nfrom magicbell.configuration import Configuration\n\nconfig = Configuration(\n    api_key="YOUR_API_KEY",\n    api_secret="YOUR_API_SECRET",\n)\nasync with magicbell.MagicBell(config) as mb:\n    # Send a notification\n    await mb.realtime.create_notification(\n        magicbell.WrappedNotification(\n            notification=magicbell.Notification(\n                title="My first notification from python!",\n                recipients=[magicbell.Recipient(email="dan@example.com")],\n            )\n        )\n    )\n```\n\n### Authentication\n\nMost API calls require your MagicBell project API Key and API Secret.\nSome API calls (i.e. projects) require your MagicBell user JWT (enterprise only).\n\nSee the [MagicBell API documentation](https://www.magicbell.com/docs/rest-api/reference#authentication) for more information.\n\n### Configuration\n\nConfiguration can be done explicitly using the `magicbell.Configuration` class,\nor implicitly by setting environment variables with the `MAGICBELL_` prefix.\n\n#### Explicit Configuration\n\n```python\nfrom magicbell.configuration import Configuration\n\n\n# Create a configuration object with the required parameters\nconfig = Configuration(\n    api_key="YOUR_API_KEY",\n    api_secret="YOUR_API_SECRET",\n)\n```\n\n#### Implicit Configuration\n\n```shell\nexport MAGICBELL_API_KEY="YOUR_API_KEY"\nexport MAGICBELL_API_SECRET="YOUR_API_SECRET"\n```\n\n```python\nfrom magicbell.configuration import Configuration\n\n\nconfig = Configuration()\n```\n\n### Examples\n\nFor more examples see the [`examples` directory](./examples).\n\n## Contributing\n\nSee [CONTRIBUTING.md](./CONTRIBUTING.md).\n\n-------\n\n<p align="center">Open sourced with ❤️ by <a href="https://noteable.io">Noteable</a> for the community.</p>\n\n<img href="https://pages.noteable.io/private-beta-access" src="https://assets.noteable.io/github/2022-07-29/noteable.png" alt="Boost Data Collaboration with Notebooks">\n\n',
    'author': 'Elijah Wilson',
    'author_email': 'eli@noteable.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/noteable-io/magicbell-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
