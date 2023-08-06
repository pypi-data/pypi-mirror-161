# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['winter',
 'winter.core',
 'winter.core.json',
 'winter.core.utils',
 'winter.data',
 'winter.data.pagination',
 'winter.web',
 'winter.web.exceptions',
 'winter.web.pagination',
 'winter.web.query_parameters',
 'winter.web.routing',
 'winter_ddd',
 'winter_django',
 'winter_openapi',
 'winter_openapi.annotations',
 'winter_sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['Django<3.0.0',
 'SQLAlchemy>=1.3,<2.0',
 'StrEnum>=0.4.8,<0.5.0',
 'dataclasses>=0.6',
 'djangorestframework>=3.9.0',
 'docstring-parser>=0.1',
 'drf-yasg>=1.13.0',
 'furl==2.0.0',
 'injector==0.15.0',
 'python-dateutil==2.8.0',
 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'winter',
    'version': '10.0.0',
    'description': 'Web Framework inspired by Spring Framework',
    'long_description': None,
    'author': 'Alexander Egorov',
    'author_email': 'mofr@zond.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/WinterFramework/winter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
