# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['url_manager']

package_data = \
{'': ['*']}

install_requires = \
['validators>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'url-manager',
    'version': '1.1.0',
    'description': '',
    'long_description': None,
    'author': 'Bruno',
    'author_email': 'bruno.gluszczuk@pagar.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.10.3',
}


setup(**setup_kwargs)
