# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['encode_utils_cli', 'encode_utils_cli.util']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.2,<9.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'schema>=0.7.5,<0.8.0',
 'tomli>=2.0.1,<3.0.0',
 'vapoursynth>=59,<60']

extras_require = \
{'vapoursynth-portable': ['vapoursynth-portable>=59,<60']}

entry_points = \
{'console_scripts': ['encode-utils-cli = encode_utils_cli.cli:cli']}

setup_kwargs = {
    'name': 'encode-utils-cli',
    'version': '0.0.1',
    'description': 'Encode utils collection',
    'long_description': '# encode-utils-cli\n\n> Encode utils collection\n\n[![PyPI version](https://img.shields.io/pypi/v/encode-utils-cli)](https://pypi.org/project/encode-utils-cli)\n[![CI/CD](https://github.com/DeadNews/encode-utils-cli/actions/workflows/python-vs-app.yml/badge.svg)](https://github.com/DeadNews/encode-utils-cli/actions/workflows/python-vs-app.yml)\n[![pre-commit.ci](https://results.pre-commit.ci/badge/github/DeadNews/encode-utils-cli/main.svg)](https://results.pre-commit.ci/latest/github/DeadNews/encode-utils-cli/main)\n[![codecov](https://codecov.io/gh/DeadNews/encode-utils-cli/branch/main/graph/badge.svg?token=OCZDZIYPMC)](https://codecov.io/gh/DeadNews/encode-utils-cli)\n\n## Installation\n\n```sh\npip install encode-utils-cli\n```\n',
    'author': 'DeadNews',
    'author_email': 'uhjnnn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeadNews/encode-utils-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
