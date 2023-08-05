# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sending', 'sending.backends']

package_data = \
{'': ['*']}

extras_require = \
{'jupyter': ['jupyter_client>=7.3.0,<8.0.0'],
 'redis': ['aioredis[hiredis]>=2.0.0,<3.0.0']}

setup_kwargs = {
    'name': 'sending',
    'version': '0.2.2',
    'description': 'Library for pub/sub usage within an async application',
    'long_description': None,
    'author': 'Nicholas Wold',
    'author_email': 'nick@nicholaswold.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
