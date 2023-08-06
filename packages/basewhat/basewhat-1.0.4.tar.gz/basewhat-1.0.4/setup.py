# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basewhat']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'basewhat',
    'version': '1.0.4',
    'description': 'A Python utility for encoding/decoding arbitrary-base numbers.',
    'long_description': '\ufeffbasewhat\n========\n\nA Python utility for encoding/decoding arbitrary-base numbers.\n\n**Usage:**\n\n    >>> b16 = BaseWhat(base=16)\n    >>> b16.from_int(65535)\n    \'FFFF\'\n    >>> b16.to_int(\'DECAFBAD\')\n    3737844653\n    >>> b32 = BaseWhat(digits="23456789ABCDEFGHJKLMNPQRSTUVWXYZ")\n    >>> b32.from_int(32767)\n    \'ZZZ\'\n    >>> b32.from_int(9223372036854775808)\n    \'A222222222222\'\n    >>> b32.to_int(\'1900MIXALOT\')\n    Traceback (most recent call last):\n    ...\n    ValueError: Not a valid base 32 number\n\nProject home page: <https://sr.ht/~paulbissex/Basewhat/>\n\nAuthor: Paul Bissex <paul@bissex.net>\n',
    'author': 'Paul Bissex',
    'author_email': 'paul@bissex.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sr.ht/~paulbissex/Basewhat/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
