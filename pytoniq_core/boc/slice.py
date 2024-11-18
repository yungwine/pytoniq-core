import typing
from bitarray.util import ba2int

from .deserialize import Boc, NullCell
from .cell import Cell
from .tvm_bitarray import TvmBitarray, BitarrayLike
from .address import Address, ExternalAddress


class SliceError(Exception):
    pass


class Slice(NullCell):

    def __init__(self, bits: TvmBitarray, refs: typing.List[Cell], type_: int = -1):
        self.bits = bits
        self.refs = refs
        self.type_ = type_
        # super().__init__(bits, refs, type_)
        self.ref_offset = 0

    @property
    def remaining_bits(self):
        return len(self.bits)

    @property
    def remaining_refs(self):
        return len(self.refs) - self.ref_offset

    def is_special(self):
        from .exotic import CellTypes
        return False if self.type_ == CellTypes.ordinary else True

    def preload_bit(self) -> int:
        return self.bits[0]

    def load_bit(self) -> int:
        bit = self.preload_bit()
        del self.bits[0]
        return bit

    def preload_bool(self) -> bool:
        return bool(self.bits[0])

    def load_bool(self) -> bool:
        bit = self.preload_bit()
        del self.bits[0]
        return bool(bit)

    def skip_bits(self, length: int) -> "Slice":
        del self.bits[:length]
        return self

    def preload_bits(self, length: int) -> BitarrayLike:
        bits = self.bits[:length]
        return bits

    def load_bits(self, length: int) -> BitarrayLike:
        bits = self.preload_bits(length)
        del self.bits[:length]
        return bits

    def preload_uint(self, length: int) -> int:
        return ba2int(self.bits[:length], signed=False)

    def load_uint(self, length: int) -> int:
        uint = self.preload_uint(length)
        del self.bits[:length]
        return uint

    def preload_int(self, length: int) -> int:
        return ba2int(self.bits[:length], signed=True)

    def load_int(self, length: int) -> int:
        integer = self.preload_int(length)
        del self.bits[:length]
        return integer

    def preload_bytes(self, length: int) -> bytes:
        return self.bits[:length * 8].tobytes()

    def load_bytes(self, length: int) -> bytes:
        bytes_ = self.preload_bytes(length)
        del self.bits[:length * 8]
        return bytes_

    def preload_address(self) -> typing.Union[Address, ExternalAddress, None]:
        rem = self.preload_uint(2)
        if not rem:
            return None
        if rem == 1:
            len_ = int(self.preload_bits(11)[2:].to01(), 2)
            addr = int(self.preload_bits(11 + len_)[11:].to01(), 2)
            return ExternalAddress(addr, len_)
        if rem != 2:
            raise SliceError('Unsupported address type')
        if self.preload_uint(3) % 2:
            raise SliceError('Unsupported anycast in preload_address')

        rem = self.preload_bits(267)

        wc = ba2int(rem[3:11], signed=True)
        hash_part = rem[11:].tobytes()

        return Address((wc, hash_part))

    def load_address(self) -> typing.Union[Address, ExternalAddress, None]:
        tag = self.load_uint(2)
        if tag == 0:
            return None
        elif tag == 1:
            len_ = self.load_uint(9)
            return ExternalAddress(self.load_uint(len_), len_)
        # todo: addr_var
        is_anycast = False
        if self.load_bool():
            is_anycast = True
            depth = self.load_uint(5)
            if depth < 1:
                raise SliceError('Anycast depth must be greater than 0')
            pfx = self.load_uint(depth)
        if tag == 2:
            wc = self.load_int(8)
            hash_part = self.load_bytes(32)
            addr = Address((wc, hash_part))
        else:
            raise SliceError('Unknown address type')  # todo: addr_var
        if is_anycast:
            addr.set_anycast(depth, pfx)
        return addr

    def preload_var_uint(self, bit_length: int) -> int:
        length = self.preload_uint(bit_length)
        if not length:
            return 0
        num = self.preload_bits(bit_length + length * 8)[bit_length:]
        return ba2int(num, signed=False)

    def load_var_uint(self, bit_length: int) -> int:
        length = self.load_uint(bit_length)
        if not length:
            return 0
        return self.load_uint(length * 8)

    def preload_var_int(self, bit_length: int) -> int:
        length = self.preload_uint(bit_length)
        if not length:
            return 0
        num = self.preload_bits(bit_length + length * 8)[bit_length:]
        return ba2int(num, signed=True)

    def load_var_int(self, bit_length: int) -> int:
        length = self.load_uint(bit_length)
        if not length:
            return 0
        return self.load_int(length * 8)

    def preload_coins(self) -> int:
        length = self.preload_uint(4)
        if not length:
            return 0
        coins = self.preload_bits(4 + length * 8)[4:]
        return ba2int(coins, signed=False)

    def load_coins(self) -> typing.Optional[int]:
        length = self.load_uint(4)
        if not length:
            return 0
        return self.load_uint(length * 8)

    def preload_string(self, byte_length: int = 0) -> str:
        if byte_length == 0:
            byte_length = len(self.bits) // 8
        return self.preload_bytes(byte_length).decode()

    def load_string(self, byte_length: int = 0) -> str:
        if byte_length == 0:
            byte_length = len(self.bits) // 8
        return self.load_bytes(byte_length).decode()

    def load_snake_bytes(self) -> bytes:
        assert not self.remaining_bits % 8, f'invalid string length: {self.remaining_bits}'
        assert self.remaining_refs in (0, 1), f'invalid amount of refs: {self.remaining_refs}'
        if not self.remaining_refs:
            return self.load_bytes(self.remaining_bits // 8)
        return self.load_bytes(self.remaining_bits // 8) + self.load_ref().begin_parse().load_snake_bytes()

    def load_snake_string(self) -> str:
        return self.load_snake_bytes().decode()

    def preload_ref(self, offset: int = 0) -> Cell:
        return self.refs[self.ref_offset + offset]

    def load_ref(self) -> Cell:
        ref = self.refs[self.ref_offset]
        self.ref_offset += 1
        return ref

    def preload_maybe_ref(self) -> typing.Optional[Cell]:
        if self.preload_bool():
            return self.refs[self.ref_offset]
        else:
            return None

    def load_maybe_ref(self) -> typing.Optional[Cell]:
        if self.load_bit():
            ref = self.refs[self.ref_offset]
            self.ref_offset += 1
            return ref
        else:
            return None

    def load_hashmap(self, key_length: int, key_deserializer: typing.Callable = None,
                     value_deserializer: typing.Callable = None):
        from .hashmap.hashmap import HashMap
        return HashMap.parse(self, key_length, key_deserializer, value_deserializer)

    def load_hashmap_aug(self, key_length: int, x_deserializer: typing.Callable = None,
                         y_deserializer: typing.Callable = None):
        from .hashmap.parse import parse_hashmap_aug
        return parse_hashmap_aug(self, key_length, x_deserializer, y_deserializer)

    def load_hashmap_aug_e(self, key_length: int, x_deserializer: typing.Callable = None,
                           y_deserializer: typing.Callable = None):
        if self.is_special():
            return self.to_cell()
        if self.load_bit():
            from .hashmap.parse import parse_hashmap_aug
            return parse_hashmap_aug(self.load_ref().begin_parse(), key_length, x_deserializer, y_deserializer)
        else:
            return {}, [self]  # extra

    def preload_dict(self, key_length: int, key_deserializer: typing.Callable = None,
                     value_deserializer: typing.Callable = None):
        from .hashmap.hashmap import HashMap
        if self.preload_bit():
            return HashMap.parse(self.preload_ref().begin_parse(), key_length, key_deserializer, value_deserializer)
        else:
            return None

    def load_dict(self, key_length: int, key_deserializer: typing.Callable = None,
                  value_deserializer: typing.Callable = None):
        from .hashmap.hashmap import HashMap
        if self.load_bit():
            return HashMap.parse(self.load_ref().begin_parse(), key_length, key_deserializer, value_deserializer)
        else:
            return None

    def to_cell(self):
        from .cell import Cell
        return Cell(self.bits.copy(), self.refs[self.ref_offset:], self.type_)

    def to_builder(self):
        if self.is_special():
            raise SliceError('cant convert exotic slice to builder')
        from .builder import Builder
        return Builder().store_slice(self)

    @classmethod
    def from_cell(cls, cell: "Cell"):
        return cls(cell.bits.copy(), cell.refs.copy(), cell.type_)

    @classmethod
    def one_from_boc(cls, data: typing.Any) -> "Slice":
        boc = Boc(data)
        cells = boc.deserialize()
        return cells[0].begin_parse()

    def copy(self):
        return Slice(self.bits.copy(), self.refs.copy(), self.type_)

    def __repr__(self) -> str:
        return f'<Slice {len(self.bits)}[{self.bits.tobytes().hex().upper()}] -> {len(self.refs) - self.ref_offset} refs>'

    def __str__(self, t=1, comma=False) -> str:
        """
        :param t: \t symbols amount before text
        :param comma: "," after "}"
        """
        text = f'{len(self.bits)}[{self.bits.tobytes().hex().upper()}]'
        if self.refs:
            text += f' -> {{\n'
            for index, ref in enumerate(self.refs[self.ref_offset:]):
                next_comma = True if index != len(self.refs) - 1 else False
                text += '\t' * t + ref.__str__(t + 1, next_comma) + '\n'
            text += '\t' * (t - 1) + '}'
        if comma:
            text += ','
        return text
