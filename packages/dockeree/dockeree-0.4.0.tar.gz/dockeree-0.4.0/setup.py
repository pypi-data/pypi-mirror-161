# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dockeree']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0',
 'docker>=4.4.0',
 'loguru>=0.6.0',
 'networkx>=2.5',
 'pandas>=1.2.0',
 'pygit2>=1.9.1',
 'pytest>=3.0',
 'requests>=2.20.0']

setup_kwargs = {
    'name': 'dockeree',
    'version': '0.4.0',
    'description': 'Make it easy to build and manager Docker images.',
    'long_description': '# [dockeree](https://github.com/dclong/dockeree)\n\nMake it easy to build and manager Docker images.\n    \n## Supported Operating Systems and Python Versions\n\n| OS      | Python 3.7 | Python 3.8 | Python 3.9 | Python 3.10 |\n|---------|------------|------------|------------|-------------|\n| Linux   | Y          | Y          | Y          | Y           |\n| macOS   | Y          | Y          | Y          | Y           |\n| Windows | Y          | Y          | Y          | Y           |\n\n## Installation\n\nYou can download a copy of the latest release and install it using pip.\n```bash\npip3 install dockeree\n```\n',
    'author': 'Benjamin Du',
    'author_email': 'longendu@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/legendu-net/dockeree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
