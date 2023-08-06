"""
Convert integers to and from strings in other bases.
"""


class BaseWhat(object):
    """
    Encode/decode arbitrary-base numbers (as strings).

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
    >>> b32.from_int(11111)
    'CV9'
    >>> b32.from_int(-11111)
    '-CV9'
    >>> b32.from_int(0)
    '0'
    >>> b32.to_int('DECAFBAD')
    391186392331
    """
    def __init__(self, base=None, digits=None) -> None:
        """
        Construct an instance given either the base or an explicit set of symbols to use for digits.

        :param: base: The number base
        :param: digits: A string containing this base's digits, in order
        """
        RAW_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if not (base or digits):
            raise ValueError("Either base or digits required")
        if base and digits and base != len(digits):
            raise ValueError("Base and digits are mismatched")
        if base and not digits:
            self.base = base
            self.digits = RAW_DIGITS[:base]
        if digits:
            self.digits = digits
            self.base = len(digits)

    def from_int(self, num:int) -> str:
        result = ""
        negative = False
        if num == 0:
            result = "0"
        elif num < 0:
            num = abs(num)
            negative = True
        while num:
            digitval = num % self.base
            result = self.digits[digitval] + result
            num //= self.base
        if negative:
            result = "-" + result
        return result

    def to_int(self, encoded:str) -> int:
        if any((d not in self.digits for d in encoded)):
            raise ValueError("Not a valid base {0} number".format(self.base))
        result = 0
        for pos, digit in enumerate(encoded):
            result += self.digits.index(digit) * pow(self.base, len(encoded) - pos - 1)
        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("Tests complete.")

