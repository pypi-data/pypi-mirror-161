# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['original_posting']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'diskcache>=5.4.0,<6.0.0',
 'wisepy2>=1.3,<2.0']

entry_points = \
{'console_scripts': ['op = original_posting.cli:main']}

setup_kwargs = {
    'name': 'original-posting',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'thautwarm',
    'author_email': 'twshere@outlook.com',
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
