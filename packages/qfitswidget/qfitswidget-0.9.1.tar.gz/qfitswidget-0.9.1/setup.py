# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qfitswidget', 'qfitswidget.qt']

package_data = \
{'': ['*'], 'qfitswidget.qt': ['resources/*']}

install_requires = \
['PyQt5>=5.15.7,<6.0.0',
 'astropy>=5.1,<6.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0']

setup_kwargs = {
    'name': 'qfitswidget',
    'version': '0.9.1',
    'description': 'PyQt widget for displaying FITS files',
    'long_description': None,
    'author': 'Tim-Oliver Husser',
    'author_email': 'thusser@uni-goettingen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
