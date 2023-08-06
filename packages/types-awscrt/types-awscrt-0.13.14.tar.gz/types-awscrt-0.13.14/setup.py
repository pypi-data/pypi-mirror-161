# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awscrt-stubs']

package_data = \
{'': ['*'], 'awscrt-stubs': ['eventstream/*']}

setup_kwargs = {
    'name': 'types-awscrt',
    'version': '0.13.14',
    'description': 'Type annotations and code completion for awscrt',
    'long_description': '# types-awscrt\n\n[![PyPI - types-awscrt](https://img.shields.io/pypi/v/types-awscrt.svg?color=blue)](https://pypi.org/project/types-awscrt)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-awscrt.svg?color=blue)](https://pypi.org/project/types-awscrt)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/types-awscrt?color=blue)](https://pypistats.org/packages/types-awscrt)\n\n![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)\n\nType annotations and code completion for [awscrt](https://pypi.org/project/awscrt/) package.\nThis package is a part of [mypy_boto3_builder](https://github.com/youtype/mypy_boto3_builder) project.\n\n## Installation\n\n```bash\npython -m pip install types-awscrt\n```\n\n## Usage\n\nUse [mypy](https://github.com/python/mypy) or [pyright](https://github.com/microsoft/pyright) for type checking.\n\n### Latest changes\n\nFull changelog can be found in [Releases](https://github.com/youtype/types-awscrt/releases).\n\n## Versioning\n\n`types-awscrt` version is the same as related `awscrt` version and follows\n[PEP 440](https://www.python.org/dev/peps/pep-0440/) format.\n\n## Support and contributing\n\nPlease reports any bugs or request new features in\n[types-awscrt](https://github.com/youtype/types-awscrt/issues/) repository.\n',
    'author': 'Vlad Emelianov',
    'author_email': 'vlad.emelianov.nz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://youtype.github.io/mypy_boto3_builder/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
