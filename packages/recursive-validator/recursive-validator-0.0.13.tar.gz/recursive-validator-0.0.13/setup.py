# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['recursive_validator', 'recursive_validator.helpers']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'beartype>=0.10.4,<0.11.0', 'loguru>=0.6.0,<0.7.0']

entry_points = \
{'console_scripts': ['recursive-validator = '
                     'recursive_validator.recursive_validator:app']}

setup_kwargs = {
    'name': 'recursive-validator',
    'version': '0.0.13',
    'description': '',
    'long_description': "```shell\npython main.py \\\n--include_patterns '*.yml,*.yaml' \\\n--exclude_patterns '*/backups/*' \\\n--loaders_path ./loaders \\\n--input_directory ./my-project\n```",
    'author': 'Michael Mohamed',
    'author_email': 'michael@foundationstack.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsai-dev/fsai-cli-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
