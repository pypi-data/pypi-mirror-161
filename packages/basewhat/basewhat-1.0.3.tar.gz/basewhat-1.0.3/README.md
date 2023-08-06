basewhat
========

A Python utility for encoding/decoding arbitrary-base numbers.

**Usage:**

    >>> b16 = BaseWhat(base=16)
    >>> b16.from_int(65535)
    'FFFF'
    >>> b16.to_int('DECAFBAD')
    3737844653
    >>> b32 = BaseWhat(digits="23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
    >>> b32.from_int(32767)
    'ZZZ'
    >>> b32.from_int(9223372036854775808)
    'A222222222222'
    >>> b32.to_int('1900MIXALOT')
    Traceback (most recent call last):
    ...
    ValueError: Not a valid base 32 number

Project home page: <https://sr.ht/~paulbissex/Basewhat/>

Author: Paul Bissex <paul@bissex.net>
