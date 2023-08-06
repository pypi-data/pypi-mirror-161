# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycellslib',
 'pycellslib.onedimensional',
 'pycellslib.twodimensional',
 'pycellslib.visualizers']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pygame>=2.1.2,<3.0.0',
 'scipy>=1.8,<2.0']

setup_kwargs = {
    'name': 'pycellslib',
    'version': '0.1.0',
    'description': 'Library for simulation and visualization of any cellular automata',
    'long_description': None,
    'author': 'Luis Papiernik',
    'author_email': 'lpapiernik24@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
