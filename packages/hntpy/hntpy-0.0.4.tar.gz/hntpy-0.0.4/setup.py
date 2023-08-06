# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hntpy']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['hntpy = hntpy:main']}

setup_kwargs = {
    'name': 'hntpy',
    'version': '0.0.4',
    'description': "Python wrapper for Helium API to simplify interactions with the Helium blockchain.'",
    'long_description': '# hntpy\n\nPython wrapper for Helium API to simplify interaction with Helium blockchain\n\n## Install\n\nTo use the latest version of this Python package, download from PyPi:\n\n```\npip install hntpy\n```\n',
    'author': 'Haley Morgan',
    'author_email': 'haleymorgan3264@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/h-morgan/hntpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
