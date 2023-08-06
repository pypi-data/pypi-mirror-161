# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['botocore-stubs']

package_data = \
{'': ['*'], 'botocore-stubs': ['crt/*', 'retries/*']}

install_requires = \
['types-awscrt']

setup_kwargs = {
    'name': 'botocore-stubs',
    'version': '1.27.45',
    'description': 'Type annotations and code completion for botocore',
    'long_description': '# botocore-stubs\n\n[![PyPI - botocore-stubs](https://img.shields.io/pypi/v/botocore-stubs.svg?color=blue)](https://pypi.org/project/botocore-stubs)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/botocore-stubs.svg?color=blue)](https://pypi.org/project/botocore-stubs)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/botocore-stubs?color=blue)](https://pypistats.org/packages/botocore-stubs)\n\n![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)\n\nType annotations and code completion for [botocore](https://pypi.org/project/botocore/) package.\nThis package is a part of [mypy_boto3_builder](https://github.com/youtype/mypy_boto3_builder) project.\n\n## Installation\n\n```bash\npython -m pip install botocore-stubs\n```\n\n## Usage\n\nUse [mypy](https://github.com/python/mypy) or [pyright](https://github.com/microsoft/pyright) for type checking.\n\n### Latest changes\n\nFull changelog can be found in [Releases](https://github.com/youtype/botocore-stubs/releases).\n\n## Versioning\n\n`botocore-stubs` version is the same as related `botocore` version and follows\n[PEP 440](https://www.python.org/dev/peps/pep-0440/) format.\n\n## Support and contributing\n\nPlease reports any bugs or request new features in\n[botocore-stubs](https://github.com/youtype/botocore-stubs/issues/) repository.\n',
    'author': 'Vlad Emelianov',
    'author_email': 'vlad.emelianov.nz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://youtype.github.io/mypy_boto3_builder/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
