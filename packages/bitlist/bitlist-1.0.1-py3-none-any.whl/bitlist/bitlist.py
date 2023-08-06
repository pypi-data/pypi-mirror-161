"""
Pure-Python library for working with bit vectors.
"""
from __future__ import annotations
from typing import Union, Optional, Set, Sequence, Iterable
import doctest
import collections.abc
from parts import parts

class bitlist:
    """
    Data structure for representing bit vectors. The constructor accepts a
    variety of input types (including integers, bytes-like objects, strings
    of binary digits, iterables of binary digits, and other :obj:`bitlist`
    instances) and parses them in an appropriate manner to build a bit vector.
    Integer arguments are converted into a big-endian binary representation.

    >>> bitlist(1)
    bitlist('1')
    >>> bitlist(123)
    bitlist('1111011')
    >>> bitlist('1111011')
    bitlist('1111011')
    >>> bitlist(bytes([255, 254]))
    bitlist('1111111111111110')
    >>> bitlist([1, 0, 1, 1])
    bitlist('1011')
    >>> bitlist(bitlist('1010'))
    bitlist('1010')

    The :obj:`fromhex` method can be used to convert a hexadecimal string
    into an instance. This is equivalent to converting the hexadecimal string
    into a bytes-like object and then creating a bit vector from that object.

    >>> bitlist.fromhex('abcd')
    bitlist('1010101111001101')
    >>> bitlist(bytes.fromhex('abcd'))
    bitlist('1010101111001101')

    A :obj:`bitlist` instance can be converted into an integer using the
    built-in :obj:`int` function. By default, a big-endian representation of
    integers is used. The recommended approach for switching to a
    little-endian representation is to reverse the bit vector.

    >>> b = bitlist('1111011')
    >>> int(b)
    123
    >>> int(bitlist(list(reversed(b))))
    111

    An instance can be converted into a string of binary characters using
    the :obj:`bin` method and into a hexadecimal string using the :obj:`hex`
    method. Conversion to a bytes-like object is possible via the built-in
    :obj:`to_bytes` method.

    >>> b.bin()
    '1111011'
    >>> b.hex()
    '7b'
    >>> b.to_bytes().hex()
    '7b'
    >>> list(b.to_bytes())
    [123]

    An instance is itself a :obj:`~collections.abc.Sequence` and is iterable.
    Iterating over an instance yields the sequence of bits (*i.e.*, integers
    that are ``0`` or ``1``).

    >>> [bit for bit in bitlist('10010011')]
    [1, 0, 0, 1, 0, 0, 1, 1]

    An individual bit can be retrieved (and assigned a new value) via its index.
    Slice notation is also supported.

    >>> b = bitlist('0101')
    >>> b[3]
    1
    >>> b[3] = 0
    >>> b
    bitlist('0100')
    >>> b[1:-1]
    bitlist('10')

    Instances are mutable. Conversion to an integer, binary string, or tuple is
    recommended if a corresponding immutable object is required.

    >>> tuple(bitlist('1010'))
    (1, 0, 1, 0)

    When the constructor is supplied a :obj:`bitlist` instance, a distinct copy
    of the supplied instance is created.

    >>> b = bitlist(123, 8)
    >>> c = bitlist(b)
    >>> c[0] = 1
    >>> b
    bitlist('01111011')
    >>> c
    bitlist('11111011')

    When the constructor is applied to a bytes-like object, the leading zero
    digits (*i.e.*, those on the left-hand side) **are retained** (up to the
    least multiple of eight larger than the minimum number of binary digits
    required).

    >>> bitlist(bytes([123]))
    bitlist('01111011')
    >>> bitlist(bytearray([123, 123]))
    bitlist('0111101101111011')

    When the constructor is applied to a string (consisting only of characters
    that correspond to binary digits), leading zero digits are also retained.

    >>> bitlist('01111011')
    bitlist('01111011')

    However, when the constructor is applied to an integer argument, the
    created bit vector has no leading (*i.e.*, left-hand) zeros and contains
    the minimum number of bits necessary to represent the supplied argument
    (using a big-endian representation).

    >>> bitlist(2)
    bitlist('10')
    >>> bitlist(16)
    bitlist('10000')

    The above implies that the empty bit vector represents (and is equivalent
    to) the numerical value of zero.

    >>> bitlist() == bitlist(0)
    True
    >>> bitlist() == bitlist('0') == bitlist('00') == bitlist('000')
    True
    >>> bitlist() == bitlist('')
    True
    >>> bitlist() == bitlist([])
    True

    While the equality method :obj:`__eq__` determines equality between two bit
    vectors based on the integer values they represent, the fact that leading
    zero digits are retained in some cases means that two equivalent bit vectors
    *may have different lengths*.

    >>> bitlist('0') == bitlist('000')
    True
    >>> len(bitlist('0')) == len(bitlist('000'))
    False

    For all other (non-integer) input types, the length of the vector (and
    consequently the number of leading zeos) is preserved.

    >>> bitlist('0000')
    bitlist('0000')
    >>> bitlist([0, 1, 1])
    bitlist('011')
    >>> bitlist([0, 0, 1, 1])
    bitlist('0011')
    >>> bitlist(bitlist('00010'))
    bitlist('00010')

    Only strings that consist of characters corresponding to binary digits
    are accepted by the constructor.

    >>> bitlist('abcd')
    Traceback (most recent call last):
      ...
    ValueError: each character in string must be '0' or '1'

    To convert the underlying binary representation of a string into a bit
    vector, it is necessary to encode the string as a bytes-like object.

    >>> bitlist('abcd'.encode('utf8'))
    bitlist('01100001011000100110001101100100')

    The ``length`` parameter can be used to specify the length of the bit
    vector, overriding the default behaviors. If the length parameter has a
    value that is greater than the number of bits that would be included
    according to a default behavior, the bit vector is padded with zero bits
    *on the left-hand side* to match the specified length.

    >>> bitlist(bytes([123]), 16)
    bitlist('0000000001111011')
    >>> bitlist(16, 64)
    bitlist('0000000000000000000000000000000000000000000000000000000000010000')
    >>> bitlist(bitlist(123), 8)
    bitlist('01111011')

    If the ``length`` parameter has a value that is less than the minimum
    number of bits that would be included according to a default behavior, the
    bit vector is truncated *on the left-hand side* to match the specified
    length.

    >>> bitlist(bytes([123]), 7)
    bitlist('1111011')
    >>> bitlist(bytes([123]), 4)
    bitlist('1011')
    >>> bitlist(bytes([123]), 2)
    bitlist('11')
    >>> bitlist(bytes([123]), 0)
    bitlist()
    >>> bitlist(123, 0)
    bitlist()
    >>> bitlist([1, 1, 1], 0)
    bitlist()

    Any attempt to construct an instance using unsupported arguments raises an
    exception.

    >>> bitlist([1.1, 2.2, 3.3])
    Traceback (most recent call last):
      ...
    TypeError: items in iterable must be integers
    >>> bitlist([2, 3, 4, 5])
    Traceback (most recent call last):
      ...
    ValueError: each integer in iterable must be 0 or 1
    >>> bitlist(float(1))
    Traceback (most recent call last):
      ...
    TypeError: bitlist constructor received unsupported argument
    """
    def __init__(
            self: bitlist,
            argument: Union[int, str, bytes, bytearray, bitlist, Iterable[int], None] = None,
            length: Optional[int] = None
        ):
        """
        Parse argument depending on its type and build a bit vector instance.
        """
        # pylint: disable=too-many-branches
        if argument is None:
            # By default, always return the bit vector representing zero.
            self.bits = bytearray([0])

        elif isinstance(argument, int):
            # Convert any integer into its bit representation,
            # starting with the first non-zero digit.
            self.bits = bytearray(reversed([int(b) for b in f'{argument:b}']))

        elif isinstance(argument, str):
            if not all(c in ('0', '1') for c in argument):
                raise ValueError("each character in string must be '0' or '1'")

            # Convert string of binary digit characters.
            self.bits = bytearray(reversed([int(b) for b in argument]))

        elif isinstance(argument, (bytes, bytearray)):
            # Convert bytes-like object into its constituent bits,
            # with exactly eight bits per byte (i.e., leading zeros
            # are included).
            self.bits = \
                bytearray([
                    b
                    for byte in reversed(argument)
                    for b in [(byte >> i) % 2 for i in range(0, 8)]
                ])

        elif isinstance(argument, bitlist):
            # Make constructor idempotent (but have it iterate
            # to reflect the behavior of the :obj:`list` function).
            self.bits = bytearray(list(argument.bits))

        elif isinstance(argument, collections.abc.Iterable):
            items = list(argument)

            if not all(isinstance(item, int) for item in items):
                raise TypeError('items in iterable must be integers')

            if not all(item in (0, 1) for item in items):
                raise ValueError('each integer in iterable must be 0 or 1')

            # Convert list of binary digits represented as integers.
            self.bits = bytearray(reversed(items)) if len(items) > 0 else bytearray([0])

        else:
            raise TypeError('bitlist constructor received unsupported argument')

        if length is not None:
            # Pad or truncate the bit vector to ensure the specified length.
            if length > len(self.bits):
                self.bits = self.bits + bytes([0] * (length - len(self.bits)))
            elif length < len(self.bits):
                self.bits = self.bits[0:length]

    @staticmethod
    def fromhex(s: str) -> bitlist:
        """
        Build an instance from a hexadecimal string.

        >>> bitlist.fromhex('abcd')
        bitlist('1010101111001101')
        """
        return bitlist(bytes.fromhex(s))

    def __str__(self: bitlist) -> str:
        """
        Return a string representation (that can also be evaluated
        as a valid Python expression if the class is in the namespace).

        >>> bitlist('01')
        bitlist('01')
        """
        return \
            'bitlist(' + \
            (("'" + self.bin() + "'") if len(self.bits) > 0 else '') + \
            ')'

    def __repr__(self: bitlist) -> str:
        """
        Return a string representation (that can also be evaluated
        as a valid Python expression if the class is in the namespace).
        """
        return str(self)

    def __int__(self: bitlist) -> int:
        """
        Interpret the bit vector as a big-endian representation
        of an integer and return that integer.

        >>> int(bitlist(bytes([128, 129]))) == int.from_bytes(bytes([128, 129]), 'big')
        True
        """
        return sum(b*(2**i) for (i, b) in enumerate(self.bits))

    def to_bytes(self: bitlist) -> bytes:
        """
        Return a bytes-like object representation. Note that the
        number of bits will be padded (on the left) to a multiple
        of eight.

        >>> int.from_bytes(bitlist('10000000').to_bytes(), 'big')
        128
        >>> int.from_bytes(bitlist('1000000010000011').to_bytes(), 'big')
        32899
        >>> int.from_bytes(bitlist('110000000').to_bytes(), 'big')
        384
        >>> bitlist(129 + 128*256).to_bytes().hex()
        '8081'
        >>> bitlist('11').to_bytes().hex()
        '03'
        """
        return bytes(reversed([
            int(bitlist(list(reversed(bs))))
            for bs in parts(self.bits, length=8)
        ]))

    def bin(self: bitlist) -> str:
        """
        Return a binary string representation. This matches the string emitted
        as part of the output of the default string conversion method.

        >>> bitlist('010011').bin()
        '010011'
        """
        return ''.join(list(reversed([str(b) for b in self.bits])))

    def hex(self: bitlist) -> str:
        """
        Return a hexadecimal string representation. Note that the number
        of bits will be padded (on the left) to a multiple of eight.

        >>> bitlist(bytes([123])).hex()
        '7b'
        """
        return self.to_bytes().hex()

    def __len__(self: bitlist) -> int:
        """
        Return length of bit vector (defined to be the number of bits
        it contains).

        >>> bitlist('11') + bitlist('10')
        bitlist('1110')
        """
        return len(self.bits)

    def __add__(self: bitlist, other: bitlist) -> bitlist:
        """
        The addition operator can be used for concatenation, as with
        other objects that have sequence types.

        >>> bitlist('11') + bitlist('10')
        bitlist('1110')
        """
        return bitlist(list(reversed(list(other.bits)+list(self.bits))))

    def __mul__(self: bitlist, other: int) -> bitlist:
        """
        The multiplication operator can be used for repetition, as with
        other objects that have sequence types.

        >>> bitlist(256)*2
        bitlist('100000000100000000')
        >>> bitlist(256)*'a'
        Traceback (most recent call last):
          ...
        ValueError: repetition parameter must be an integer
        """
        if isinstance(other, int):
            return bitlist(list(reversed(list(self.bits)))*other)

        raise ValueError('repetition parameter must be an integer')

    def __truediv__(
        self: bitlist, other: Union[int, Set[int], Sequence[int]]
    ) -> Sequence[bitlist]:
        """
        The division operator can be used to partition a bit vector into the
        specified number of parts, into parts of a specified length, or into
        a sequence of parts in which each part's length is specified in a
        sequence of integers (leveraging and mirroring the capabilities of the
        :obj:`~parts.parts.parts` function).

        >>> bitlist('11010001') / 2
        [bitlist('1101'), bitlist('0001')]
        >>> bitlist('11010001') / [2, 6]
        [bitlist('11'), bitlist('010001')]
        >>> bitlist('11010001') / {4}
        [bitlist('1101'), bitlist('0001')]
        >>> bitlist('11010001') / 3
        [bitlist('110'), bitlist('100'), bitlist('01')]
        """
        if isinstance(other, set) and len(other) == 1 and isinstance(list(other)[0], int):
            ps = parts(self.bits, length=list(other)[0])
        elif isinstance(other, list):
            ps = parts(self.bits, length=list(reversed(other)))
        else:
            ps = parts(self.bits, other)
        return list(reversed([bitlist(list(reversed(p))) for p in ps]))

    def __getitem__(self: bitlist, key: Union[int, slice]) -> Union[int, bitlist]:
        """
        Retrieve the bit at the specified index, or construct a slice
        of the bit vector.

        >>> bitlist('1111011')[2]
        1
        >>> bitlist('0111011')[0]
        0
        >>> bitlist('10101000')[0:5]
        bitlist('10101')
        >>> bitlist('10101000101010001010100010101000')[0:16]
        bitlist('1010100010101000')
        >>> bitlist('101')[4]
        Traceback (most recent call last):
          ...
        IndexError: bitlist index out of range
        >>> bitlist('101')['a']
        Traceback (most recent call last):
          ...
        TypeError: bitlist indices must be integers or slices
        """
        if isinstance(key, int):
            if key < 0: # Support big-endian interface using negative indices.
                return self.bits[abs(key) - 1] if abs(key) <= len(self.bits) else 0

            if key < len(self.bits):
                return self.bits[len(self.bits) - 1 - key]

            raise IndexError('bitlist index out of range')

        if isinstance(key, slice):
            return bitlist(list(reversed(self.bits))[key])

        raise TypeError('bitlist indices must be integers or slices')

    def __setitem__(self: bitlist, i: int, b: int):
        """
        Set the bit at the specified index to the supplied value.

        >>> x = bitlist('1111011')
        >>> x[2] = 0
        >>> x
        bitlist('1101011')
        >>> x[7] = 0
        Traceback (most recent call last):
          ...
        IndexError: bitlist index out of range
        """
        if i < 0: # Support big-endian interface using negative indices.
            self.bits = \
                bytearray([
                    (self[j] if j != i else b)
                    for j in range(-1, min(-len(self.bits), -abs(i)) - 1, -1)
                ])
        elif i < len(self.bits):
            i = len(self.bits) - 1 - i
            self.bits = \
                bytearray([
                    (self.bits[j] if j != i else b)
                    for j in range(0, len(self.bits))
                ])
        else:
            raise IndexError('bitlist index out of range')

    def __lshift__(self: bitlist, n: Union[int, Set[int]]) -> bitlist:
        """
        The left shift operator can be used for both performing a bit shift
        in the traditional manner (increasing the length of the bit vector)
        or for bit rotation (if the second parameter is a set).

        >>> bitlist('11') << 2
        bitlist('1100')
        >>> bitlist('11011') << {0}
        bitlist('11011')
        >>> bitlist('11011') << {1}
        bitlist('10111')
        >>> bitlist('11011') << {2}
        bitlist('01111')
        >>> bitlist('11011') << {3}
        bitlist('11110')
        >>> bitlist('11011') << {13}
        bitlist('11110')
        >>> bitlist('1') << {13}
        bitlist('1')
        """
        if isinstance(n, set) and len(n) == 1 and isinstance(list(n)[0], int):
            n = list(n)[0] % len(self) # Allow rotations to wrap around.
            return bitlist(list(self.bits[n:]) + list(self.bits[:n]))

        return bitlist(list(reversed(list([0] * n) + list(self.bits))))

    def __rshift__(self: bitlist, n: Union[int, Set[int]]) -> bitlist:
        """
        The right shift operator can be used for both performing a bit shift
        in the traditional manner (truncating bits on the right-hand side as
        necessary) or for bit rotation (if the second parameter is a set).

        >>> bitlist('1111') >> 2
        bitlist('11')
        >>> bitlist('11011') >> {0}
        bitlist('11011')
        >>> bitlist('11011') >> {1}
        bitlist('11101')
        >>> bitlist('11011') >> {2}
        bitlist('11110')
        >>> bitlist('11011') >> {3}
        bitlist('01111')
        >>> bitlist('11011') >> {13}
        bitlist('01111')
        >>> bitlist('1') >> {13}
        bitlist('1')
        """
        if isinstance(n, set) and len(n) == 1 and isinstance(list(n)[0], int):
            n = list(n)[0] % len(self) # Allow rotations to wrap around.
            return bitlist(list(self.bits[-n:]) + list(self.bits[:-n]))

        return bitlist(list(reversed(self.bits[n:])))

    def __and__(self: bitlist, other: bitlist) -> bitlist:
        """
        Logical operators are applied bitwise without changing the length.

        >>> bitlist('0100') & bitlist('1100')
        bitlist('0100')
        >>> bitlist('010') & bitlist('11')
        Traceback (most recent call last):
          ...
        ValueError: arguments to logical operations must have equal lengths
        """
        if len(self) != len(other):
            raise ValueError(
                'arguments to logical operations must have equal lengths'
            )

        return bitlist(list(reversed(
            [a & b for (a, b) in zip(self.bits, other.bits)]
        )))

    def __or__(self: bitlist, other: bitlist) -> bitlist:
        """
        Logical operators are applied bitwise without changing the length.

        >>> bitlist('0100') | bitlist('1100')
        bitlist('1100')
        >>> bitlist('010') | bitlist('11')
        Traceback (most recent call last):
          ...
        ValueError: arguments to logical operations must have equal lengths
        """
        if len(self) != len(other):
            raise ValueError(
                'arguments to logical operations must have equal lengths'
            )
        return bitlist(list(reversed(
            [a | b for (a, b) in zip(self.bits, other.bits)]
        )))

    def __xor__(self: bitlist, other: bitlist) -> bitlist:
        """
        Logical operators are applied bitwise without changing the length.

        >>> bitlist('0100') ^ bitlist('1101')
        bitlist('1001')
        >>> bitlist('010') ^ bitlist('11')
        Traceback (most recent call last):
          ...
        ValueError: arguments to logical operations must have equal lengths
        """
        if len(self) != len(other):
            raise ValueError(
                'arguments to logical operations must have equal lengths'
            )
        return bitlist(list(reversed(
            [a ^ b for (a, b) in zip(self.bits, other.bits)]
        )))

    def __invert__(self: bitlist) -> bitlist:
        """
        Logical operators are applied bitwise without changing the length.
        Inversion flips all bits and corresponds to bitwise logical negation.

        >>> ~bitlist('0100')
        bitlist('1011')
        """
        return bitlist(list(reversed([1-b for b in self.bits])))

    def __bool__(self: bitlist) -> bool:
        """
        Any non-zero instance is interpreted as ``True``.

        >>> bool(bitlist('0100'))
        True
        >>> bool(bitlist('0000'))
        False
        """
        return 1 in self.bits

    def __eq__(self: bitlist, other: bitlist) -> bool:
        """
        Instances are interpreted as integers when relational
        operators are applied.

        >>> bitlist('111') == bitlist(7)
        True
        >>> bitlist(123) == bitlist(0)
        False
        >>> bitlist(123) == bitlist('0001111011')
        True
        >>> bitlist('001') == bitlist('1')
        True
        """
        # Ignores leading zeros in representation.
        return int(self) == int(other)

    def __ne__(self: bitlist, other: bitlist) -> bool:
        """
        Instances are interpreted as integers when relational
        operators are applied.

        >>> bitlist('111') != bitlist(7)
        False
        >>> bitlist(123) != bitlist(0)
        True
        >>> bitlist('001') != bitlist('1')
        False
        """
        # Ignores leading zeros in representation.
        return int(self) != int(other)

    def __lt__(self: bitlist, other: bitlist) -> bool:
        """
        Instances are interpreted as integers when relational
        operators are applied.

        >>> bitlist(123) < bitlist(0)
        False
        >>> bitlist(123) < bitlist(123)
        False
        >>> bitlist(12) < bitlist(23)
        True
        """
        return int(self) < int(other)

    def __le__(self: bitlist, other: bitlist) -> bool:
        """
        Instances are interpreted as integers when relational
        operators are applied.

        >>> bitlist(123) <= bitlist(0)
        False
        >>> bitlist(123) <= bitlist(123)
        True
        >>> bitlist(12) <= bitlist(23)
        True
        """
        return int(self) <= int(other)

    def __gt__(self: bitlist, other: bitlist) -> bool:
        """
        Instances are interpreted as integers when relational
        operators are applied.

        >>> bitlist(123) > bitlist(0)
        True
        >>> bitlist(123) > bitlist(123)
        False
        >>> bitlist(12) > bitlist(23)
        False
        """
        return int(self) > int(other)

    def __ge__(self: bitlist, other: bitlist) -> bool:
        """
        Instances are interpreted as integers when relational
        operators are applied.

        >>> bitlist(123) >= bitlist(0)
        True
        >>> bitlist(123) >= bitlist(123)
        True
        >>> bitlist(12) >= bitlist(23)
        False
        """
        return int(self) >= int(other)

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
