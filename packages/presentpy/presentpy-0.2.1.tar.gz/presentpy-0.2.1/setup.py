# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['presentpy']

package_data = \
{'': ['*'], 'presentpy': ['templates/*']}

install_requires = \
['Pygments>=2.12.0,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'mistletoe>=0.8.2,<0.9.0',
 'nbconvert>=6.5.0,<7.0.0',
 'python-pptx>=0.6.21,<0.7.0']

entry_points = \
{'console_scripts': ['presentpy = presentpy.__main__:process']}

setup_kwargs = {
    'name': 'presentpy',
    'version': '0.2.1',
    'description': 'Create presentations from Jupyter Notebooks',
    'long_description': None,
    'author': 'Antonio Feregrino',
    'author_email': 'antonio.feregrino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
