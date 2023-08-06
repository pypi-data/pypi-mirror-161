# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reqpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'reqpy',
    'version': '0.1.0',
    'description': 'Determine the minimal required Python version of a package',
    'long_description': None,
    'author': 'Stijn de Gooijer',
    'author_email': 'stijn@degooijer.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stinodego/reqpy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
