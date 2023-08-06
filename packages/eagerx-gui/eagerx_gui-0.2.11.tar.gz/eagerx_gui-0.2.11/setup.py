# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagerx_gui']

package_data = \
{'': ['*']}

install_requires = \
['PyQt6>=6.2.3,<7.0.0',
 'PyVirtualDisplay>=3.0,<4.0',
 'eagerx>=0.1.30,<0.2.0',
 'opencv-python>=4.5,<5.0',
 'pyqtgraph>=0.12.4,<0.13.0']

setup_kwargs = {
    'name': 'eagerx-gui',
    'version': '0.2.11',
    'description': 'GUI to visualise graphs in EAGERx.',
    'long_description': None,
    'author': 'Jelle Luijkx',
    'author_email': 'j.d.luijkx@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eager-dev/eagerx_gui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
