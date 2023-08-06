""" module:: uds.security_access
    :platform: Posix
    :synopsis: Examples and known security methods of UDS and KWP2000
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPL v3
"""

import struct
from typing import Union


def seed_to_key(seed: Union[int, bytes, bytearray],
                mask: int = 0xDEADBEEF,
                shifts: int = 35):
    """
    A seed to key method is a challenge response method with a known secret. In fact is usually a couple of
    arithmetic operations, shifts, XORs in a loop, branch if carry bit is set.

    This is the standard seed to key method of a really big tier 1 supplier in southern Germany.
    Note: In reality nobody changes the shifts, only the mask which makes it easy to brute force.
          From practical experience you need 6 to 7 recorded seed key handshakes to determine the mask or
          end up with a single digit number of possible masks. Be aware that these methods are >20 years old.

    :param seed: The challenge number or bytes, 4 bytes is the standard.
    :param mask: A constant used for XOR in this case.
    :param shifts: A constant used for shift operations and loops in this case.
    :return: The key as a number or in bytes, depending on the type that the seed was given.
    """
    if isinstance(seed, int):
        seed_as_integer = seed
    elif isinstance(seed, bytes) or isinstance(seed, bytearray):
        seed_as_integer = struct.unpack('>I', seed)[0]
    else:
        raise ValueError("Not Handled {0}".format(seed))

    for i in range(shifts):
        seed_as_integer = seed_as_integer << 1
        if seed_as_integer & 0x100000000:
            seed_as_integer = seed_as_integer ^ mask
        seed_as_integer &= 0xFFFFFFFF  # make it 32Bit
    if isinstance(seed, int):
        return seed_as_integer
    elif isinstance(seed, bytes) or isinstance(seed, bytearray):
        return bytes(struct.pack('>I', seed_as_integer))
