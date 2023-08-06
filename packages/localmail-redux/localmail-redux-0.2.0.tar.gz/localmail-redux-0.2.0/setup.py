# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['localmail']

package_data = \
{'': ['*'], 'localmail': ['templates/*']}

install_requires = \
['Jinja2>=2',
 'Twisted>=22.4.0,<23.0.0',
 'crochet>=2.0.0,<3.0.0',
 'zope.interface>=5.4.0,<6.0.0']

setup_kwargs = {
    'name': 'localmail-redux',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Robert Hales',
    'author_email': 'rob.hales@xelix.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.7',
}


setup(**setup_kwargs)
