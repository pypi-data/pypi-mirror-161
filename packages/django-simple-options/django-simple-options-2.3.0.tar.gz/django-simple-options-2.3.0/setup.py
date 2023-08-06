# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['options',
 'options.management',
 'options.management.commands',
 'options.migrations',
 'options.rest_framework']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.0.0', 'djangorestframework>=3.11.0']

setup_kwargs = {
    'name': 'django-simple-options',
    'version': '2.3.0',
    'description': 'Simple app to add configuration options to a Django project.',
    'long_description': '=====================\nDjango Simple Options\n=====================\n\n.. image:: https://travis-ci.org/marcosgabarda/django-simple-options.svg?branch=master\n    :target: https://travis-ci.org/marcosgabarda/django-simple-options\n\n.. image:: https://coveralls.io/repos/github/marcosgabarda/django-simple-options/badge.svg?branch=master\n    :target: https://coveralls.io/github/marcosgabarda/django-simple-options?branch=master\n\n\nSimple app to add configuration options to a Django project.\n\nQuick start\n-----------\n\n**1** Install using pip::\n\n    $ pip install django-simple-options\n\n**2** Add "options" to your INSTALLED_APPS settings like this::\n\n    INSTALLED_APPS += (\'options\',)\n\n\nSettings options\n----------------\n\nUse ``SIMPLE_OPTIONS_CONFIGURATION_DEFAULT`` to set the default options::\n\n    SIMPLE_OPTIONS_CONFIGURATION_DEFAULT = {\n        "sold_out": {\n            "value": 0,\n            "type": INT,\n            "public_name": "Sets tickets as sold out"\n        },\n    }\n\n',
    'author': 'Marcos Gabarda',
    'author_email': 'hey@marcosgabarda.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marcosgabarda/django-simple-options',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
