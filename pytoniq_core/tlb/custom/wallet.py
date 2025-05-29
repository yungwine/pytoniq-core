import typing

from ..tlb import TlbScheme
from ..transaction import MessageAny
from ...boc import Cell, Builder, Slice, HashMap


class WalletV3Data(TlbScheme):
    """
    wallet_v3_data#_ seqno:uint32 wallet_id:uint32 public_key:bits256 = WalletV3Data;
    """
    def __init__(self,
                 seqno: typing.Optional[int] = 0,
                 wallet_id: typing.Optional[int] = None,
                 public_key: typing.Optional[bytes] = None
                 ):
        self.seqno = seqno
        if wallet_id is None:
            wallet_id = 698983191
        self.wallet_id = wallet_id
        if public_key is None:
            raise Exception('Public Key required for Wallet!')
        self.public_key = public_key

    def serialize(self) -> Cell:
        builder = Builder()
        builder\
            .store_uint(self.seqno, 32)\
            .store_uint(self.wallet_id, 32)\
            .store_bytes(self.public_key)
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(seqno=cell_slice.load_uint(32), wallet_id=cell_slice.load_uint(32), public_key=cell_slice.load_bytes(32))


class WalletV4Data(TlbScheme):
    """
    // wc_n_address#_ wc:int8 addr_hash:uint256 = WcAndAddress;
    wallet_v4_data#_ seqno:uint32 wallet_id:uint32 public_key:bits256 plugins:(Maybe ^Cell) = WalletV4Data;
    """
    def __init__(self,
                 seqno: typing.Optional[int] = 0,
                 wallet_id: typing.Optional[int] = None,
                 public_key: typing.Optional[bytes] = None,
                 plugins: typing.Optional[Cell] = None
                 ):
        self.seqno = seqno
        if wallet_id is None:
            wallet_id = 698983191
        self.wallet_id = wallet_id
        if public_key is None:
            raise Exception('Public Key required for Wallet!')
        self.public_key = public_key
        self.plugins = plugins

    def serialize(self) -> Cell:
        builder = Builder()
        builder\
            .store_uint(self.seqno, 32)\
            .store_uint(self.wallet_id, 32)\
            .store_bytes(self.public_key)\
            .store_dict(self.plugins)
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(seqno=cell_slice.load_uint(32), wallet_id=cell_slice.load_uint(32), public_key=cell_slice.load_bytes(32), plugins=cell_slice.load_maybe_ref())


class HighloadWalletData(TlbScheme):
    """
    highload_wallet_data#_ wallet_id:uint32 last_cleaned:uint64 public_key:bits256 old_queries:(HashmapE 64 WalletMessage) = HighloadWalletData;
    """
    def __init__(self,
                 wallet_id: typing.Optional[int] = None,
                 last_cleaned: typing.Optional[int] = None,
                 public_key: typing.Optional[bytes] = None,
                 old_queries: typing.Optional[dict] = None
                 ):
        if wallet_id is None:
            wallet_id = 698983191
        self.wallet_id = wallet_id
        if public_key is None:
            raise Exception('Public Key required for Wallet!')
        self.last_cleaned = last_cleaned
        self.public_key = public_key
        self.old_queries = old_queries

    @staticmethod
    def old_queries_serializer(src, dest):
        dest.store_cell(src.serialize())

    @staticmethod
    def old_queries_deserializer(src):
        return WalletMessage.deserialize(src)

    def serialize(self) -> Cell:
        builder = Builder()
        builder\
            .store_uint(self.wallet_id, 32) \
            .store_uint(self.last_cleaned, 64) \
            .store_bytes(self.public_key)\
            .store_dict(HashMap(key_size=64, value_serializer=self.old_queries_serializer).serialize())
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(wallet_id=cell_slice.load_uint(32), last_cleaned=cell_slice.load_uint(64), public_key=cell_slice.load_bytes(32), old_queries=cell_slice.load_dict(key_length=64, value_deserializer=cls.old_queries_deserializer))


class HighloadWalletV3Data(TlbScheme):

    """
    storage$_ public_key:bits256 subwallet_id:uint32 old_queries:(HashmapE 14 ^Cell)
              queries:(HashmapE 14 ^Cell) last_clean_time:uint64 timeout:uint22 = Storage;
    """

    def __init__(
            self,
            public_key: typing.Optional[bytes] = None,
            wallet_id: typing.Optional[int] = None,
            old_queries: typing.Optional[dict] = None,
            queries: typing.Optional[dict] = None,
            last_clean_time: typing.Optional[int] = None,
            timeout: int = None,
    ) -> None:
        self.public_key = public_key
        if wallet_id is None:
            wallet_id = 0x10ad
        self.wallet_id = wallet_id
        self.old_queries = old_queries
        self.queries = queries
        self.last_clean_time = last_clean_time
        self.timeout = timeout

    def serialize(self) -> Cell:
        builder = Builder()
        builder\
            .store_bytes(self.public_key) \
            .store_uint(self.wallet_id, 32) \
            .store_dict(HashMap(key_size=13, map_=self.old_queries).serialize()) \
            .store_dict(HashMap(key_size=13, map_=self.queries).serialize()) \
            .store_uint(self.last_clean_time, 64) \
            .store_uint(self.timeout, 22)

        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(
            public_key=cell_slice.load_bytes(32),
            wallet_id=cell_slice.load_uint(32),
            old_queries=cell_slice.load_dict(key_length=13),
            queries=cell_slice.load_dict(key_length=13),
            last_clean_time=cell_slice.load_uint(64),
            timeout=cell_slice.load_uint(22)
        )


class WalletMessage(TlbScheme):
    """
    wallet_message$_ send_mode:uint8 message:^MessageAny = WalletMessage;
    """

    def __init__(self, send_mode: int, message: MessageAny):
        self.send_mode = send_mode
        self.message = message

    def serialize(self):
        builder = Builder()
        builder.store_uint(self.send_mode, 8)
        builder.store_ref(self.message.serialize())
        return builder.end_cell()

    @classmethod
    def deserialize(cls, *args):
        pass
