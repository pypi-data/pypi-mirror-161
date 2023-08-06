# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rungunicorn', 'rungunicorn.management', 'rungunicorn.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['Django==4.0', 'gunicorn>=20.1.0,<21.0.0']

setup_kwargs = {
    'name': 'rungunicorn',
    'version': '0.1.0',
    'description': 'Django management command starting gunicorn web server.',
    'long_description': None,
    'author': 'Jarosław Wygoda',
    'author_email': 'jaroslaw@wygoda.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jwygoda/django-rungunicorn',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
