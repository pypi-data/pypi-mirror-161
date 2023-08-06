# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['covid19_utpl', 'covid19_utpl.src']

package_data = \
{'': ['*'], 'covid19_utpl': ['data/*', 'img/*']}

setup_kwargs = {
    'name': 'covid19-utpl',
    'version': '1.0.1',
    'description': '',
    'long_description': '',
    'author': 'David Jimenez',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
