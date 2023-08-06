# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['event_sourcery',
 'event_sourcery.dto',
 'event_sourcery.interfaces',
 'event_sourcery.types',
 'event_sourcery_pydantic',
 'event_sourcery_sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4,<2.0', 'pydantic>=1.9,<2.0']

setup_kwargs = {
    'name': 'python-event-sourcery',
    'version': '0.0.2',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
