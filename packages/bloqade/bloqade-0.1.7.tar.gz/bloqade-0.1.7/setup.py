# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bloqade']

package_data = \
{'': ['*']}

install_requires = \
['juliacall>=0.9.3,<0.10.0', 'juliapkg>=0.1.5,<0.2.0', 'matplotlib==3.5.1']

setup_kwargs = {
    'name': 'bloqade',
    'version': '0.1.7',
    'description': 'The Python wrapper for Bloqade.jl',
    'long_description': '',
    'author': 'Roger-luo',
    'author_email': 'rogerluo.rl18@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
