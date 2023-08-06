"""
Test suite containing examples and functional unit tests (based on bit vector
implementations of common arithmetic operations) that demonstrate how this
library's features can be used.

To view the source code of an example function, click its **[source]** link.
"""
from __future__ import annotations
import doctest
from unittest import TestCase

try:
    from bitlist import bitlist
except: # pylint: disable=bare-except
    # Support validation of docstrings in this script via its direct execution.
    import sys
    sys.path.append('./bitlist')
    from bitlist.bitlist import bitlist

def add(x: bitlist, y: bitlist) -> bitlist:
    """
    Bitwise addition algorithm.

    >>> int(add(bitlist(123), bitlist(456)))
    579
    """
    r: bitlist = bitlist(0)
    carry: int = 0 # Integer that represents an individual bit.

    # Use negative indices to simulate big-endian order of bits.
    for i in range(1, max(len(x), len(y)) + 1): # Upper bound is not inclusive.
        r[-i] = (x[-i] ^ y[-i]) ^ carry
        carry = (x[-i] & y[-i]) | (x[-i] & carry) | (y[-i] & carry)
    r[-(max(len(x), len(y)) + 1)] = carry

    return r

def mul(x: bitlist, y: bitlist) -> bitlist:
    """
    Bitwise multiplication algorithm.

    >>> int(mul(bitlist(123), bitlist(456)))
    56088
    """
    r: bitlist = bitlist(0)

    for i in range(1, len(x) + 1): # Upper bound is not inclusive.
        if x[-i] == 1: # Use negative index to simulate big-endian order of bits.
            r = add(r, y)
        y = y << 1

    return r

def exp(x: bitlist, y: bitlist) -> bitlist:
    """
    Bitwise exponentiation algorithm.

    >>> int(exp(bitlist(123), bitlist(5)))
    28153056843
    """
    r: bitlist = bitlist(1)

    for i in range(1, len(y) + 1): # Upper bound is not inclusive.
        if y[-i] == 1: # Use negative index to simulate big-endian order of bits.
            r = mul(r, x)
        x = mul(x, x)

    return r

def div(x: bitlist, y: bitlist) -> bitlist:
    """
    Bitwise integer division algorithm.

    >>> int(div(bitlist(12345), bitlist(678)))
    18
    """
    if y > x:
        return bitlist(0)

    for _ in range(0, len(x)):
        y = y << 1

    t: bitlist = bitlist(0)
    q: bitlist = bitlist(0)
    p: bitlist = bitlist(2 ** len(x))
    for _ in range(0, len(x) + 1): # Upper bound is not inclusive.
        if add(t, y) <= x:
            t = add(t, y)
            q = add(q, p)
        y = y >> 1
        p = p >> 1

    return q

class Test_bitlist(TestCase):
    """
    Tests of algorithms for bitwise operations.
    """
    # pylint: disable=unnecessary-lambda-assignment
    def test_from_integer(self):
        """Test integer conversion."""
        self.assertEqual(bitlist(123), bitlist('1111011'))

    def test_add(self):
        """Test bitwise addition."""
        op = lambda a, b: int(add(bitlist(a), bitlist(b)))
        for (x, y) in [(a+b, op(a, b)) for a in range(0, 100) for b in range(0, 100)]:
            self.assertEqual(x, y)

    def test_mul(self):
        """Test bitwise multiplication."""
        op = lambda a, b: int(mul(bitlist(a), bitlist(b)))
        for (x, y) in [(a*b, op(a, b)) for a in range(0, 30) for b in range(0, 30)]:
            self.assertEqual(x, y)

    def test_exp(self):
        """Test bitwise exponentiation."""
        op = lambda a, b: int(exp(bitlist(a), bitlist(b)))
        for (x, y) in [(a**b, op(a, b)) for a in range(0, 12) for b in range(0, 4)]:
            self.assertEqual(x, y)

    def test_div(self):
        """Test bitwise division."""
        op = lambda a, b: int(div(bitlist(a), bitlist(b)))
        for (x, y) in [(a//b, op(a, b)) for a in range(0, 12) for b in range(1, 12)]:
            self.assertEqual(x, y)

# Always invoke the doctests in this module.
doctest.testmod()
