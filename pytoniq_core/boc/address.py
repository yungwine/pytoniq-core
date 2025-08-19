import base64
import binascii
import typing
from dataclasses import dataclass

from ..crypto.crc import crc16
from .cell import Cell


@dataclass
class Anycast:
    depth: int
    rewrite_pfx: int


class AddressError(Exception):
    pass


class Address:

    def __init__(self, address):
        """
        Note that initializing from hex form is 10 times faster than user-friendly bounceable form
        """
        self.wc: int = None
        self.hash_part: bytes = None
        self.is_bounceable = False
        self.is_test_only = False
        self.anycast = None

        if isinstance(address, tuple):
            # Address((-1, b'\x11\x01\xff...'))
            self.wc = address[0]
            assert isinstance(address[1], bytes), 'expected bytes address hash part'
            self.hash_part = address[1]
            return
        if isinstance(address, self.__class__):
            self.wc = address.wc
            self.hash_part = address.hash_part
            return
        if self.is_hex(address):
            return
        if self.is_b64(address):
            return

        raise AddressError('unknown address type provided')

    def set_anycast(self, depth: int, rewrite_pfx: int):
        self.anycast = Anycast(depth, rewrite_pfx)

    def is_hex(self, addr: str) -> bool:
        try:
            wc, hash_part = addr.split(':')
            int(hash_part, 16)
            self.wc = int(wc)
            self.hash_part = bytes.fromhex(hash_part)
            return True
        except ValueError:
            return False

    def is_b64(self, addr: str) -> bool:
        try:
            decoded = base64.urlsafe_b64decode(addr)
            tag = decoded[0]
            if tag & 0x80:  # test flag
                self.is_test_only = True
                tag ^= 0x80
            if tag == 0x11:  # bounceable
                self.is_bounceable = True
            self.wc = int.from_bytes(decoded[1:2], 'big', signed=True)
            self.hash_part = decoded[2:34]
            if decoded[34:] != crc16(decoded[:34]):
                raise AddressError('the address is invalid')
            return True
        except binascii.Error:
            return False

    def to_str(self, is_user_friendly=True, is_url_safe=True, is_bounceable=True, is_test_only=False):
        """
        Note that to_str(is_user_friendly=False) is 20 times faster than to_str(is_user_friendly=True)
        """

        if not is_user_friendly:
            return f'{self.wc}:{self.hash_part.hex()}'

        tag = 0x11  # bounceable tag

        if not is_bounceable:
            tag = 0x51
        if is_test_only:
            tag |= 0x80

        result = tag.to_bytes(1, 'big') + self.wc.to_bytes(1, 'big', signed=True) + self.hash_part

        result += crc16(result)

        if is_url_safe:
            result = base64.urlsafe_b64encode(result).decode()
        else:
            result = base64.b64encode(result).decode()

        return result

    def to_tl_account_id(self) -> dict:
        return {'workchain': self.wc, 'id': self.hash_part.hex()}

    def to_cell(self) -> Cell:
        from .builder import Builder
        return Builder()\
            .store_bits('100')\
            .store_int(self.wc, 8)\
            .store_bytes(self.hash_part)\
            .end_cell()

    # def __str__(self):
    #     return self.to_str()

    def __eq__(self, other: "Address"):
        return self.wc == other.wc and self.hash_part == other.hash_part and self.anycast == other.anycast

    def __repr__(self):
        if self.anycast is not None:
            return f'Address<{self.to_str()} with {self.anycast}>'
        return f'Address<{self.to_str()}>'
    
    def __hash__(self):
        return int.from_bytes(self.hash_part, "big") + self.wc

    def __json__(self):
        if self.anycast is not None:
            # to_str ignores anycast, that can be dangerous as default strategy
            # thus fallback to __repr__
            return self.__repr__()
        # flags like is_bounceable, is_test_only, as well as url-safeness
        # are application dependent thus in json use not user-friendly form
        return self.to_str(is_user_friendly=False)


class ExternalAddress:
    def __init__(self, address: typing.Union[int, str, bytes, None], length: int = None):
        if isinstance(address, str):
            address = bytes.fromhex(address)
        if isinstance(address, bytes):
            address = int.from_bytes(address, 'big')
        if length is None:
            length = address.bit_length()
        self.external_address = address
        self.len = length

    def to_cell(self):
        from .builder import Builder
        b = (Builder()
                .store_bits('01')
                .store_uint(self.len, 9))
        if self.external_address is not None:
            b.store_uint(self.external_address, self.len)
        return b.end_cell()

    def __repr__(self):
        if self.len != 0:
            return f'ExternalAddress<{hex(self.external_address)}>'
        return f'ExternalAddress<{self.external_address}>'

    def __eq__(self, other):
        return self.external_address == other.external_address and self.len == other.len
