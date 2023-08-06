# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['atomkraft',
 'atomkraft.chain',
 'atomkraft.cli',
 'atomkraft.reactor',
 'atomkraft.test',
 'atomkraft.utils']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'bip-utils>=2.3.0,<3.0.0',
 'case-converter>=1.1.0,<2.0.0',
 'copier>=6.1.0,<7.0.0',
 'hdwallet>=2.1.1,<3.0.0',
 'jsonrpcclient>=4.0.2,<5.0.0',
 'modelator>=0.5.1,<0.6.0',
 'numpy>=1.22.4,<2.0.0',
 'pytest>=7.1.2,<8.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tomlkit>=0.11.1,<0.12.0',
 'typer[all]>=0.6.1,<0.7.0',
 'websockets>=10.3,<11.0']

entry_points = \
{'console_scripts': ['atomkraft = atomkraft.cli:app'],
 'pytest11': ['atomkraft-chain = atomkraft.chain.pytest']}

setup_kwargs = {
    'name': 'atomkraft',
    'version': '0.0.4',
    'description': 'Testing for Cosmos Blockchains',
    'long_description': '# atomkraft\n\nTesting for Cosmos Blockchains\n\n### Using `pip` (inside a system or virtual env)\n\n```\npip install atomkraft\natomkraft --help\n# or\npython -m atomkraft --help\n```\n\n### Using `poetry` (inside a project)\n\n```\npoetry add atomkraft\npoerty run atomkraft --help\n# or\npoetry run python -m atomkraft --help\n```\n\n### Code Quality\n\n```\npip install black pylama[all]\nblack . --check\npylama -l pyflakes,pycodestyle,isort\n```\n',
    'author': 'Andrey Kuprianov',
    'author_email': 'andrey@informal.systems',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/informalsystems/atomkraft',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
