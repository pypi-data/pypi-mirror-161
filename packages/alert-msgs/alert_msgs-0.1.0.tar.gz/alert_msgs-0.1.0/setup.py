# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alert_msgs']

package_data = \
{'': ['*'], 'alert_msgs': ['styles/*']}

install_requires = \
['dominate>=2.6.0,<3.0.0',
 'premailer>=3.10.0,<4.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'ready-logger>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'alert-msgs',
    'version': '0.1.0',
    'description': 'Utilities for creating HTML and Markdown alert messages.',
    'long_description': None,
    'author': 'Dan Kelleher',
    'author_email': 'kelleherjdan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
