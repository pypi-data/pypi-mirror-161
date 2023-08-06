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
    'version': '0.0.1a0',
    'description': 'Python Project Template',
    'long_description': '# encode-utils-cli\n\nEncode utils collection\n',
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
