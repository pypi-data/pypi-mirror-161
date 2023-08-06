# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enki_sr']

package_data = \
{'': ['*']}

install_requires = \
['blessed>=1.19.1,<2.0.0', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['enki = enki_sr.enki:main']}

setup_kwargs = {
    'name': 'enki-sr',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Marcus Orochena',
    'author_email': 'marcus.orochena@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
