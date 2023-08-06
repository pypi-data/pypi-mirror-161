# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hashbox', 'hashbox.frozen', 'hashbox.mutable']

package_data = \
{'': ['*']}

install_requires = \
['cykhash>=2.0.0,<3.0.0', 'numpy>=1.14,<2.0', 'sortednp>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'hashbox',
    'version': '0.3.0',
    'description': 'Find Python objects by exact match on their attributes.',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
