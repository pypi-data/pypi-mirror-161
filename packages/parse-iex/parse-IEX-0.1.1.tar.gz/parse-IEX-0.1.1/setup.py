# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parse_iex']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'parse-iex',
    'version': '0.1.1',
    'description': 'Parse IEX market data streams',
    'long_description': "# parse-IEX\nA collection of parsers for [IEX](https://exchange.iex.io/).\n\nUse the parsers to gather relevant quotes and trades information. \n\nCurrently, only TOPS parsing is supported.\n\n## TOPS Parsing Example\n\n```py\nfrom parse_iex import tops\n\nmessage = b'\\x51\\x00\\xac\\x63\\xc0\\x20\\x96\\x86\\x6d\\x14\\x5a\\x49\\x45\\x58\\x54\\x20\\x20\\x20\\xe4\\x25\\x00\\x00\\x24\\x1d\\x0f\\x00\\x00\\x00\\x00\\x00\\xec\\x1d\\x0f\\x00\\x00\\x00\\x00\\x00\\xe8\\x03\\x00\\x00'\n    \nprint(tops.decode_message(message))\n```\n\n```\nbest bid: 9700 ZIEXT shares for 99.05 USD; best ask: 1000 ZIEXT shares for 99.07 USD @ 2016-08-23 19:30:32.572716\n```\n\n## TODO\n\n- [x] Make a basic parser\n- [x] Write documentation\n- [ ] Report errors\n- [ ] Add a DEEP parser\n- [ ] Parse trading breaks\n",
    'author': 'Amit Goren',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mmatamm/parse-IEX',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
