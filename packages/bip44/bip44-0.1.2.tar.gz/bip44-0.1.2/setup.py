# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bip44']

package_data = \
{'': ['*']}

install_requires = \
['bip32>=3.1,<4.0', 'mnemonic>=0.20,<0.21', 'pycryptodome>=3.15.0,<4.0.0']

setup_kwargs = {
    'name': 'bip44',
    'version': '0.1.2',
    'description': 'Simple Python bip44 implementation. Mnemonic + bip32.',
    'long_description': '# python-bip44\n\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4e4aa71f4a234dca809d014b0b214220)](https://www.codacy.com/manual/kigawas/python-bip44)\n[![CI](https://img.shields.io/github/workflow/status/kigawas/python-bip44/Build)](https://github.com/kigawas/python-bip44/actions)\n[![Codecov](https://img.shields.io/codecov/c/github/kigawas/python-bip44.svg)](https://codecov.io/gh/kigawas/python-bip44)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bip44.svg)](https://pypi.org/project/bip44/)\n[![PyPI](https://img.shields.io/pypi/v/bip44.svg)](https://pypi.org/project/bip44/)\n[![License](https://img.shields.io/github/license/kigawas/python-bip44.svg)](https://github.com/kigawas/python-bip44)\n\nSimple Python [bip44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) implementation. [Mnemonic](https://github.com/trezor/python-mnemonic) + [bip32](https://github.com/darosior/python-bip32).\n\n## Install\n\n`pip install bip44`\n\n## Quick Start\n\n```python\n>>> from coincurve import PrivateKey\n>>> from bip44 import Wallet\n>>> from bip44.utils import get_eth_addr\n>>> mnemonic = "purity tunnel grid error scout long fruit false embody caught skin gate"\n>>> w = Wallet(mnemonic)\n>>> sk, pk = w.derive_account("eth", account=0)\n>>> sk = PrivateKey(sk)\n>>> sk.public_key.format() == pk\nTrue\n>>> get_eth_addr(pk)\n\'0x7aD23D6eD9a1D98E240988BED0d78e8C81Ec296C\'\n```\n\n## Release Notes\n\n### 0.1.1 ~ 0.1.2\n\n- Support Python 3.10, 3.11\n- Bump dependencies\n- Drop Python 3.6\n\n### 0.1.0\n\n- First beta release\n- Bump dependencies\n\n### 0.0.1 ~ 0.0.7\n\n- Alpha releases\n',
    'author': 'Weiliang Li',
    'author_email': 'to.be.impressive@gmail.com',
    'maintainer': 'Weiliang Li',
    'maintainer_email': 'to.be.impressive@gmail.com',
    'url': 'https://github.com/kigawas/python-bip44',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
