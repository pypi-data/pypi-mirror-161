# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['punch_api', 'punch_api.metrics']

package_data = \
{'': ['*']}

install_requires = \
['prometheus-client>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'punch-api',
    'version': '8.0.1',
    'description': 'Punch Python and PySpark Public API',
    'long_description': None,
    'author': 'Punch',
    'author_email': 'contact@punchplatform.com',
    'maintainer': 'Punch',
    'maintainer_email': 'contact@punchplatform.com',
    'url': 'https://punchplatform.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10.4,<4.0.0',
}


setup(**setup_kwargs)
