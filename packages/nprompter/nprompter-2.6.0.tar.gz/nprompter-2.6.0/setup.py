# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nprompter', 'nprompter.api', 'nprompter.processing']

package_data = \
{'': ['*'], 'nprompter': ['web/assets/*', 'web/templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'python-slugify>=6.1.2,<7.0.0',
 'requests>=2.28.0,<3.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['nprompter = nprompter.__main__:app']}

setup_kwargs = {
    'name': 'nprompter',
    'version': '2.6.0',
    'description': 'A web based teleprompter that uses Notion as a storage backend',
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
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
