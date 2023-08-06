# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zo']

package_data = \
{'': ['*']}

install_requires = \
['anchorpy>=0.9.3,<0.10.0', 'solana>=0.25.0,<0.26.0']

setup_kwargs = {
    'name': 'zo-sdk',
    'version': '0.1.4.post1',
    'description': '01.xyz Python SDK',
    'long_description': '# 01.xyz Python SDK\n\n<p align="center">\n<b><a href="https://01protocol.github.io/zo-sdk-py/">Documentation</a></b>\n|\n<b><a href="https://pypi.org/project/zo-sdk/">PyPi</a></b>\n</p>\n\nPython SDK to interface with the 01 Solana program.\n\n## Installation\n\n```\n$ pip install zo-sdk\n```\n\n## General Usage\n\n```python\nfrom zo import Zo\n\n# Create the client. By default, this loads the local payer\n# and initializes a margin account for the payer if there\n# isn\'t already one.\nzo = await Zo.new(cluster=\'devnet\')\n\n# View market and collateral info.\nprint(zo.collaterals["BTC"])\nprint(zo.markets["BTC-PERP"])\n\n# Deposit and withdraw collateral.\nawait zo.deposit(1, mint=zo.collaterals["SOL"].mint)\nawait zo.withdraw(1, mint=zo.collaterals["SOL"].mint)\n\n# Place and cancel orders.\nawait zo.place_order(1., 100., \'bid\',\n    symbol="SOL-PERP", order_type="limit", client_id=1)\nawait zo.cancel_order_by_client_id(1, symbol="SOL-PERP")\n\n# Refresh loaded accounts to see updates,\n# such as change in collateral after deposits.\nawait zo.refresh()\n\n# View own balance, positions and orders.\nprint(zo.balance["BTC"])\nprint(zo.position["BTC-PERP"])\nprint(zo.orders["BTC-PERP"])\n\n# Dispatch multiple instructions in a single transaction,\n# using the `_ix` variant.\nawait zo.send(\n    zo.cancel_order_by_client_id_ix(1, symbol="SOL-PERP"),\n    zo.place_order_ix(1., 100., \'bid\',\n        symbol="SOL-PERP", order_type="limit", client_id=1),\n)\n```\n',
    'author': 'Sheheryar Parvaz',
    'author_email': 'me@cherryman.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/01protocol/zo-sdk-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
