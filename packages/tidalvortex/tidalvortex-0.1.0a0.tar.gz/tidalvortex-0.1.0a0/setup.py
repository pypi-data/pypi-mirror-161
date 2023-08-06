# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vortex']

package_data = \
{'': ['*']}

install_requires = \
['LinkPython>=0.1.1,<0.2.0',
 'PyQt5>=5.15.7,<6.0.0',
 'QScintilla>=2.13.3,<3.0.0',
 'ipython>=8.4.0,<9.0.0',
 'parsy>=1.4.0,<2.0.0',
 'pyliblo3>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['vortex = vortex.cli:run']}

setup_kwargs = {
    'name': 'tidalvortex',
    'version': '0.1.0a0',
    'description': 'Python port of TidalCycles',
    'long_description': None,
    'author': 'Tidal Cyclists',
    'author_email': 'vortex@tidalcycles.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tidalcycles/vortex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
