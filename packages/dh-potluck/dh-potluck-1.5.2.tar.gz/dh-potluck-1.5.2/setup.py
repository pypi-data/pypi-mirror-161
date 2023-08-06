# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dh_potluck',
 'dh_potluck.celery',
 'dh_potluck.email',
 'dh_potluck.messaging',
 'dh_potluck.utils']

package_data = \
{'': ['*'], 'dh_potluck': ['templates/*']}

install_requires = \
['Werkzeug>=0.15.0',
 'boltons>=20.2.1,<21.0.0',
 'boto3>=1.17.102,<2.0.0',
 'confluent-kafka>=1.6.0,<2.0.0',
 'ddtrace==1.1.1',
 'flask-limiter>=2.2.0,<3.0.0',
 'flask-smorest>=0.38.1,<0.39.0',
 'flask>=2.1.2,<3.0.0',
 'flask_sqlalchemy>=2.4.4,<3.0.0',
 'json-log-formatter>=0.3.0,<0.4.0',
 'mandrill>=1.0.60,<2.0.0',
 'marshmallow==3.17.0',
 'mixpanel>=4.9.0,<5.0.0',
 'requests>=2.22,<3.0',
 'sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'dh-potluck',
    'version': '1.5.2',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
