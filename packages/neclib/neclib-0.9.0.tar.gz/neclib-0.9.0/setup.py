# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neclib',
 'neclib.controllers',
 'neclib.interfaces',
 'neclib.parameters',
 'neclib.parameters.parser',
 'neclib.simulators',
 'neclib.utils']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.0.4,<6.0.0',
 'n-const>=1.1.0,<2.0.0',
 'numpy>=1.22,<2.0',
 'ogameasure>=0.5,<0.6']

extras_require = \
{':sys_platform == "linux"': ['pyinterface>=1.6,<2.0']}

setup_kwargs = {
    'name': 'neclib',
    'version': '0.9.0',
    'description': 'Pure Python tools for NECST.',
    'long_description': '# neclib\n\n[![PyPI](https://img.shields.io/pypi/v/neclib.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/neclib/)\n[![Python](https://img.shields.io/pypi/pyversions/neclib.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/neclib/)\n[![Test](https://img.shields.io/github/workflow/status/necst-telescope/neclib/Test?logo=github&label=Test&style=flat-square)](https://github.com/necst-telescope/neclib/actions)\n[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](LICENSE)\n\nPure Python tools for NECST.\n\n## Features\n\nThis library provides:\n\n- Miscellaneous tools for NECST system.\n\n## Installation\n\n```shell\npip install neclib\n```\n\n## Usage\n\nSee the [API reference](https://necst-telescope.github.io/neclib/_source/neclib.html).\n\n---\n\nThis library is using [Semantic Versioning](https://semver.org).\n',
    'author': 'KaoruNishikawa',
    'author_email': 'k.nishikawa@a.phys.nagoya-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://necst-telescope.github.io/neclib/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
