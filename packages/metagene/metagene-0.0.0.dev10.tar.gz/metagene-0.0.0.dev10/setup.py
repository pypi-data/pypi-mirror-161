# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metagene']

package_data = \
{'': ['*'], 'metagene': ['data/*']}

install_requires = \
['Click>=8.0.0,<9.0.0',
 'matplotlib>=3.0.0,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pyranges>=0.0.117,<0.0.118',
 'ray>=1.13.0,<2.0.0']

entry_points = \
{'console_scripts': ['metagene = metagene.cli:cli']}

setup_kwargs = {
    'name': 'metagene',
    'version': '0.0.0.dev10',
    'description': 'Metagene Profiling Analysis and Visualization',
    'long_description': '# Metagene\n\n[![Readthedocs](https://readthedocs.org/projects/metagene/badge/?version=latest)](https://metagene.readthedocs.io/en/latest/?badge=latest)\n[![Build Status](https://img.shields.io/travis/y9c/metagene.svg)](https://travis-ci.com/y9c/metagene)\n[![Pypi Releases](https://img.shields.io/pypi/v/metagene.svg)](https://pypi.python.org/pypi/metagene)\n[![Downloads](https://pepy.tech/badge/metagene)](https://pepy.tech/project/metagene)\n\n**Metagene Profiling Analysis and Visualization**\n\n(WIP)\n\n## Demo\n',
    'author': 'Ye Chang',
    'author_email': 'yech1990@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/y9c/metagene',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
