# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['th2_common_utils', 'th2_common_utils.converters', 'th2_common_utils.util']

package_data = \
{'': ['*']}

install_requires = \
['sortedcollections>=2.0.0,<3.0.0', 'th2-grpc-common>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'th2-common-utils',
    'version': '1.4.2.dev2782955822',
    'description': 'Python library with useful functions for developers and QA needs',
    'long_description': '# th2-common-utils-py (1.4.2)\nPython library with useful functions for **developers and QA needs**. Check the [Wiki](https://github.com/th2-net/th2-common-utils-py/wiki) for instructions and examples.\n\n## Installation\n```\npip install th2-common-utils\n```\n\n## Release notes\n\n### 1.4.2\n\n* Fix conversion of `Direction` field of `message_metadata`.\n\n### 1.4.1\n\n* Changed `metadata` conversion in `message_to_dict` function.\n\n### 1.4.0\n\n* Added `json_to_message` function.\n\n\n### 1.3.0\n\n* Changed structure of `message_filter` and `metadata_filter` fields in `dict_to_root_message_filter` function.\n',
    'author': 'TH2-devs',
    'author_email': 'th2-devs@exactprosystems.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/th2-net/th2-common-utils-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
