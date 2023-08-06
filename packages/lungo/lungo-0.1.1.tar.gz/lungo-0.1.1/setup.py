# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lungo']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.12.0,<3.0.0', 'prompt-toolkit>=3.0.30,<4.0.0']

entry_points = \
{'console_scripts': ['lungo = lungo.interpreter:main']}

setup_kwargs = {
    'name': 'lungo',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Stepan Anokhin',
    'author_email': 'stepan.anokhin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
