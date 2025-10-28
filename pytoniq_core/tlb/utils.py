import typing

from .tlb import TlbScheme, TlbError
from .. import Builder
from ..boc import Slice, Cell, CellTypes


class MerkleUpdate(TlbScheme):
    """
    !merkle_update#02 {X:Type} old_hash:bits256 new_hash:bits256 old:^X new:^X = MERKLE_UPDATE X;
    """

    def __init__(self, cell: Cell, old_hash: bytes, new_hash: bytes, old, new):
        self.cell = cell
        self.old_hash = old_hash
        self.new_hash = new_hash
        self.old = old
        self.new = new

    @classmethod
    def serialize(cls, *args): ...

    @classmethod
    def deserialize(cls, cell: Cell, deserializer: typing.Callable) -> typing.Optional["MerkleUpdate"]:
        if cell.type_ != CellTypes.merkle_update:
            return None

        cell_slice = cell.begin_parse()
        tag = cell_slice.load_bytes(1)[:1]
        # if tag != b'\x02':
        #     raise TlbError(f'MerkleUpdate deserialization error: unexpected tag {tag}')
        old_hash = cell_slice.load_bytes(32)
        new_hash = cell_slice.load_bytes(32)
        old = deserializer(cell_slice.load_ref().begin_parse())
        new = deserializer(cell_slice.load_ref().begin_parse())
        return cls(cell, old_hash, new_hash, old, new)


class HashUpdate(TlbScheme):
    """
    update_hashes#72 {X:Type} old_hash:bits256 new_hash:bits256 = HASH_UPDATE X;
    """

    def __init__(self, old_hash: bytes, new_hash: bytes):
        self.old_hash = old_hash
        self.new_hash = new_hash

    def serialize(self):
        return Builder()\
                .store_bytes(b'\x72')\
                .store_bytes(self.old_hash)\
                .store_bytes(self.new_hash)\
                .end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        tag = cell_slice.load_bytes(1)[:1]
        if tag != b'r':
            raise TlbError(f'HashUpdate deserialization error: unexpected tag {tag}')
        old_hash = cell_slice.load_bytes(32)
        new_hash = cell_slice.load_bytes(32)
        return cls(old_hash, new_hash)


class WalletV5WalletID:
    """
    schema:
    wallet_id -- int32
    wallet_id = network_global_id ^ context_id
    context_id_client$1 = wc:int8 version:uint8 counter:uint15
    context_id_backoffice$0 = counter:uint31

    calculated default values serialisation:

    network_global_id = -239, workchain = 0, version = 0', subwallet_number = 0 (client context)
    gives wallet_id = 2147483409

    network_global_id = -239, workchain = -1, version = 0', subwallet_number = 0 (client context)
    gives wallet_id = 8388369

    network_global_id = -3, workchain = 0, version = 0', subwallet_number = 0 (client context)
    gives wallet_id = 2147483645

    network_global_id = -3, workchain = -1, version = 0', subwallet_number = 0 (client context)
    gives wallet_id = 8388605
    """
    def __init__(self,
                 subwallet_number: int = 0,
                 workchain: int = 0,
                 version: int = 0,
                 network_global_id: int = -239,
    ) -> None:
        self.subwallet_number = subwallet_number
        self.workchain = workchain
        self.version = version
        self.network_global_id = network_global_id

    def pack(self) -> int:
        ctx = 0
        ctx |= 1 << 31
        ctx |= (self.workchain & 0xFF) << 23
        ctx |= (self.version & 0xFF) << 15
        ctx |= self.subwallet_number & 0x7FFF
        return ctx ^ (self.network_global_id & 0xFFFFFFFF)

    @classmethod
    def unpack(
        cls,
        value: int,
        network_global_id: int,
    ) -> "WalletV5WalletID":
        ctx = (value ^ network_global_id) & 0xFFFFFFFF

        subwallet_number = ctx & 0x7FFF
        version = (ctx >> 15) & 0xFF
        wc_u8 = (ctx >> 23) & 0xFF
        workchain = (wc_u8 ^ 0x80) - 0x80

        return cls(
            subwallet_number=subwallet_number,
            workchain=workchain,
            version=version,
            network_global_id=network_global_id,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.pack()!r}>"


def deserialize_shard_hashes(cell_slice: Slice):
    from .block import BinTree, ShardDescr
    shard_hashes = cell_slice.load_dict(32, value_deserializer=lambda src: BinTree.deserialize(
        src.load_ref().begin_parse()))
    if shard_hashes:
        for k in shard_hashes:
            for i in range(len(shard_hashes[k].list)):
                if not shard_hashes[k].list[i].is_special():
                    shard_hashes[k].list[i] = ShardDescr.deserialize(shard_hashes[k].list[i])
                else:
                    shard_hashes[k].list[i] = None
    return shard_hashes


def uint64_to_int64(num: int):
    return (num & ((1 << 63) - 1)) - (num & (1 << 63))
