# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rigelcore',
 'rigelcore.clients',
 'rigelcore.loggers',
 'rigelcore.models',
 'rigelcore.simulations',
 'rigelcore.simulations.requirements']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0',
 'python-on-whales>=0.50.0,<0.51.0',
 'rich>=11.2.0,<12.0.0',
 'rigel-hpl>=0.1.0,<0.2.0',
 'roslibpy>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'rigelcore',
    'version': '0.1.20',
    'description': 'A common interface for Rigel and all its plugins.',
    'long_description': '**Rigelcore**',
    'author': 'Pedro Miguel Melo',
    'author_email': 'pedro.m.melo@inesctec.pt',
    'maintainer': 'Pedro Miguel Melo',
    'maintainer_email': 'pedro.m.melo@inesctec.pt',
    'url': 'https://github.com/rigel-ros/rigelcore',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
