# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['msgapp', 'msgapp.parsers', 'msgapp.producers']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.6.1,<4.0.0']

extras_require = \
{'dev': ['pydantic>=1.9.1,<2.0.0',
         'google-cloud-pubsub>=2.13.4,<3.0.0',
         'aiobotocore>=2.3.4,<3.0.0'],
 'json': ['pydantic>=1.9.1,<2.0.0'],
 'pubsub': ['google-cloud-pubsub>=2.13.4,<3.0.0'],
 'sqs': ['aiobotocore>=2.3.4,<3.0.0']}

setup_kwargs = {
    'name': 'msgapp',
    'version': '0.1.0',
    'description': 'Declarative message processing applications',
    'long_description': None,
    'author': 'Adrian Garcia Badaracco',
    'author_email': 'dev@adriangb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
