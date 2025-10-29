import typing

from .tlb import TlbScheme, TlbError
from .utils import MerkleUpdate, HashUpdate
from .. import begin_cell
from ..boc import Slice, Builder, Cell
from ..boc.address import Address


class AccountError(TlbError):
    pass


class SimpleAccount(TlbScheme):
    """
    // simple_balance$_ Grams = AccountBalance;

    account_none$0 = SimpleAccount;
    account$1 addr:Address balance:Grams state:SimpleAccountState = SimpleAccount;
    """
    """
    this schema is needed for user-friendly and familiar account representation,
    but not used anywhere outside of this library
    """
    def __init__(self, address: Address, balance: int, state: "SimpleAccountState"):
        self.address = address
        self.balance = balance
        self.state = state

    @classmethod
    def serialize(cls, *args):
        ...

    @classmethod
    def deserialize(cls, *args):
        ...

    @classmethod
    def from_raw(cls, account: "Account", address: typing.Optional[Address] = None):
        if account is None:
            return cls(address=address, balance=0, state=SimpleAccountState.from_raw(None))
        return cls(address=account.addr, balance=account.storage.balance.grams, state=SimpleAccountState.from_raw(account.storage.state))

    def is_uninitialized(self):
        return self.state.type_ == 'uninitialized'

    def is_frozen(self):
        return self.state.type_ == 'frozen'

    def is_active(self):
        return self.state.type_ == 'active'

    def __repr__(self):
        return f'<SimpleAccount {self.address}: state={self.state.type_}, balance={self.balance}>'


class SimpleAccountState(TlbScheme):
    """
    uninitialized$00 = SimpleAccountState;
    frozen$01 state_hash:bits256 = SimpleAccountState;
    active$10 state_init:StateInit = SimpleAccountState;
    """
    """
    this schema is needed for user-friendly and familiar account state representation,
    but not used anywhere outside of this library
    """

    def __init__(self, type_: typing.Literal["uninitialized", "frozen", "active"],
                 state_hash: typing.Optional[bytes] = None,
                 state_init: typing.Optional["StateInit"] = None,
                 ):
        self.type_ = type_
        self.state_hash = state_hash
        self.state_init = state_init

    @classmethod
    def serialize(cls, *args):
        ...

    @classmethod
    def deserialize(cls, *args):
        ...

    @classmethod
    def from_raw(cls, account_state: typing.Optional["AccountState"]):
        if account_state is None or account_state.type_ == 'account_uninit':
            return cls('uninitialized')
        if account_state.type_ == 'account_frozen':
            return cls('frozen', state_hash=account_state.state_hash)
        return cls('active', state_init=account_state.state_init)


class Account(TlbScheme):
    """
    account$1 addr:MsgAddressInt storage_stat:StorageInfo storage:AccountStorage = Account;
    """

    def __init__(self, addr: Address, storage_stat: "StorageInfo", storage: "AccountStorage"):
        self.addr = addr
        self.storage_stat = storage_stat
        self.storage = storage

    def serialize(self) -> Cell:
        builder = Builder()
        builder.store_bit(1)
        builder.store_address(self.addr)
        builder.store_cell(self.storage_stat.serialize())
        builder.store_cell(self.storage.serialize())
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        if cell_slice.load_bit():
            return cls(cell_slice.load_address(), StorageInfo.deserialize(cell_slice), AccountStorage.deserialize(cell_slice))
        else:
            return None


class StorageInfo(TlbScheme):
    """
    storage_info$_ used:StorageUsed storage_extra:StorageExtraInfo last_paid:uint32
              due_payment:(Maybe Grams) = StorageInfo;
    """

    def __init__(self, used: "StorageUsed", storage_extra: "StorageExtraInfo", last_paid: int, due_payment: typing.Optional[int]):
        self.used = used
        self.last_paid = last_paid
        self.storage_extra = storage_extra
        self.due_payment = due_payment

    def serialize(self) -> Cell:
        builder = Builder() \
            .store_cell(self.used.serialize()) \
            .store_cell(self.storage_extra.serialize()) \
            .store_uint(self.last_paid, 32)
        if self.due_payment is not None:
            builder.store_bit(1)
            builder.store_coins(self.due_payment)
        else:
            builder.store_bit(0)
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(StorageUsed.deserialize(cell_slice), StorageExtraInfo.deserialize(cell_slice), cell_slice.load_uint(32), cell_slice.load_coins() if cell_slice.load_bit() else None)


class StorageExtraInfo(TlbScheme):
    """
    storage_extra_none$000 = StorageExtraInfo;
    storage_extra_info$001 dict_hash:uint256 = StorageExtraInfo;
    """

    def __init__(self, type_: typing.Literal["storage_extra_none", "storage_extra_info"], dict_hash: bytes = None):
        self.type_ = type_
        self.dict_hash = dict_hash

    def serialize(self) -> Cell:
        builder = Builder()
        if self.type_ == "storage_extra_none":
            builder.store_uint(0, 3)
        elif self.type_ == "storage_extra_info":
            builder.store_uint(1, 3)
            builder.store_bytes(self.dict_hash)
        else:
            raise TlbError(f"Unknown StorageExtraInfo type: {self.type_}")
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        tag = cell_slice.load_uint(3)
        if tag == 0:  # 000: storage_extra_none
            return cls(type_="storage_extra_none")
        elif tag == 1:  # 001: storage_extra_info
            dict_hash = cell_slice.load_bytes(32)
            return cls(type_="storage_extra_info", dict_hash=dict_hash)
        else:
            raise TlbError(f"Unknown StorageExtraInfo tag: {tag}")


class StorageUsed(TlbScheme):
    """
    storage_used$_ cells:(VarUInteger 7) bits:(VarUInteger 7) = StorageUsed;
    """

    def __init__(self, cells, bits, *args, **kwargs):
        self.cells = cells
        self.bits = bits
        self.public_cells = None  # for backward compatibility

    def serialize(self) -> Cell:
        builder = Builder() \
            .store_var_uint(self.cells, 3) \
            .store_var_uint(self.bits, 3)
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        l = 3  # int(7).bit_length()
        return cls(cell_slice.load_var_uint(l), cell_slice.load_var_uint(l))


class StorageUsedShort(TlbScheme):
    """
    storage_used_short$_ cells:(VarUInteger 7) bits:(VarUInteger 7) = StorageUsedShort;
    """

    def __init__(self, cells, bits):
        self.cells = cells
        self.bits = bits

    def serialize(self):
        l = 3  # int(7).bit_length()
        return Builder().store_var_uint(self.cells, l).store_var_uint(self.bits, l)

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        l = 3  # int(7).bit_length()
        return cls(cell_slice.load_var_uint(l), cell_slice.load_var_uint(l))


class AccountStorage(TlbScheme):
    """
    account_storage$_ last_trans_lt:uint64
    balance:CurrencyCollection state:AccountState
    = AccountStorage;
    """

    def __init__(self, last_trans_lt: int, balance, state: "AccountState"):
        from .transaction import CurrencyCollection
        self.last_trans_lt = last_trans_lt
        self.balance: CurrencyCollection = balance
        self.state = state

    def serialize(self) -> Cell:
        builder = Builder() \
            .store_uint(self.last_trans_lt, 64) \
            .store_cell(self.balance.serialize()) \
            .store_cell(self.state.serialize())

        return builder.end_cell() 

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        from .block import CurrencyCollection
        return cls(
            cell_slice.load_uint(64),
            CurrencyCollection.deserialize(cell_slice),
            AccountState.deserialize(cell_slice)
        )


class AccountState(TlbScheme):
    """
    account_uninit$00 = AccountState;
    account_active$1 _:StateInit = AccountState;
    account_frozen$01 state_hash:bits256 = AccountState;
    """

    def __init__(self, type_: str, **kwargs):
        self.type_ = type_
        self.state_init: StateInit
        self.state_hash: bytes
        for k, v in kwargs.items():
            setattr(self, k, v)

    def serialize(self) -> Cell:
        builder = Builder()

        if self.type_ == "account_uninit":
            builder.store_uint(0, 2)
        elif self.type_ == "account_active":
            builder.store_uint(1, 1)
            builder.store_cell(self.state_init.serialize())
        elif self.type_ == "account_frozen":
            assert len(self.state_hash) == 64 # bytes are stored in hex ...
            builder.store_uint(1, 2)
            builder.store_bytes(bytes.fromhex(self.state_hash))

        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        b = cell_slice.load_bit()
        kwargs = {}
        if b:  # $1
            type_ = 'account_active'
            kwargs['state_init'] = StateInit.deserialize(cell_slice)
        else:
            b = cell_slice.load_bit()
            if b:  # $01
                type_ = 'account_frozen'
                kwargs['state_hash'] = cell_slice.load_bytes(32).hex()
            else:  # $00
                type_ = 'account_uninit'
        return cls(type_, **kwargs)


class StateInit(TlbScheme):
    """
    _ split_depth:(Maybe (## 5)) special:(Maybe TickTock)
    code:(Maybe ^Cell) data:(Maybe ^Cell)
    library:(Maybe ^Cell) = StateInit;
    """

    def __init__(self,
                 split_depth: typing.Optional[int] = None,
                 special: typing.Optional["TickTock"] = None,
                 code: typing.Optional[Cell] = None,
                 data: typing.Optional[Cell] = None,
                 library: typing.Optional[Cell] = None):
        self.split_depth = split_depth
        self.special = special
        self.code = code
        self.data = data
        self.library = library

    def serialize(self) -> Cell:
        builder = Builder()
        builder.store_bit(1).store_uint(self.split_depth, 5) if self.split_depth is not None else builder.store_bit(0)
        builder.store_bit(1).store_cell(self.special.serialize()) if self.special is not None else builder.store_bit(0)
        builder.store_maybe_ref(self.code)
        builder.store_maybe_ref(self.data)
        builder.store_maybe_ref(self.library)
        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(
            split_depth=cell_slice.load_uint(5) if cell_slice.load_bit() else None,
            special=TickTock.deserialize(cell_slice) if cell_slice.load_bit() else None,
            code=cell_slice.load_ref() if cell_slice.load_bit() else None,
            data=cell_slice.load_ref() if cell_slice.load_bit() else None,
            library=cell_slice.load_ref() if cell_slice.load_bit() else None,
        )


class TickTock(TlbScheme):
    """
    tick_tock$_ tick:Bool tock:Bool = TickTock;
    """
    def __init__(self, tick: bool, tock: bool):
        self.tick = tick
        self.tock = tock

    def serialize(self) -> Cell:
        return Builder().store_bool(self.tick).store_bool(self.tock).end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        return cls(cell_slice.load_bool(), cell_slice.load_bool())


class ShardAccount(TlbScheme):
    """
    account_descr$_ account:^Account last_trans_hash:bits256
    last_trans_lt:uint64 = ShardAccount;
    """
    def __init__(self, account: typing.Optional[Account], last_trans_hash: bytes, last_trans_lt: int, cell: typing.Optional[Cell] = None):
        self.account = account
        self.last_trans_hash = last_trans_hash
        self.last_trans_lt = last_trans_lt
        self.cell = cell  # to check merkle proof of account states

    def serialize(self) -> Cell:
        assert len(self.last_trans_hash) == 32

        builder = Builder()
        if self.account is None:
            builder.store_ref(begin_cell().store_bit_int(0).end_cell())
        else:
            builder.store_ref(self.account.serialize())

        builder.store_bytes(self.last_trans_hash) \
               .store_uint(self.last_trans_lt, 64)

        return builder.end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        cell_copy = cell_slice.copy()  # TODO optimize
        return cls(account=Account.deserialize(cell_slice.load_ref().begin_parse()),
                   last_trans_hash=cell_slice.load_bytes(32),
                   last_trans_lt=cell_slice.load_uint(64), cell=cell_copy.to_cell())


class AccountStatus(TlbScheme):
    """
    acc_state_uninit$00 = AccountStatus;
    acc_state_frozen$01 = AccountStatus;
    acc_state_active$10 = AccountStatus;
    acc_state_nonexist$11 = AccountStatus;
    """
    def __init__(self, type_: typing.Literal["uninitialized", "frozen", "active", "nonexist"]):
        self.type_ = type_

    def serialize(self) -> Cell:
        if self.type_ == 'uninitialized':
            return Builder().store_uint(0, 2).end_cell()
        if self.type_ == 'frozen':
            return Builder().store_uint(1, 2).end_cell()
        if self.type_ == 'active':
            return Builder().store_uint(2, 2).end_cell()
        if self.type_ == 'nonexist':
            return Builder().store_uint(3, 2).end_cell()

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        tag = cell_slice.load_bit()
        if tag:
            tag2 = cell_slice.load_bit()
            if tag2:  # 11
                return cls(type_='nonexist')
            else:  # 10
                return cls(type_='active')
        else:
            tag2 = cell_slice.load_bit()
            if tag2:  # 01
                return cls(type_='frozen')
            else:  # 00
                return cls(type_='uninitialized')


class AccountBlock(TlbScheme):
    """
    acc_trans#5 account_addr:bits256
    transactions:(HashmapAug 64 ^Transaction CurrencyCollection)
    state_update:^(HASH_UPDATE Account)
    = AccountBlock;
    """
    def __init__(self,
                 account_addr: str,
                 transactions: typing.Tuple[dict, list],
                 state_update: HashUpdate):
        self.account_addr = account_addr
        self.transactions = transactions
        self.state_update = state_update

    @classmethod
    def serialize(cls, *args):
        pass

    @classmethod
    def deserialize(cls, cell_slice: Slice):
        from .transaction import Transaction, CurrencyCollection
        tag = cell_slice.load_uint(4)
        if tag != 5:
            raise AccountError(f'AccountBlock deserialization error: unknown prefix tag {tag}')
        return cls(
            account_addr=cell_slice.load_bytes(32).hex(),
            transactions=cell_slice.load_hashmap_aug(64, x_deserializer=lambda src: Transaction.deserialize(src.load_ref().begin_parse()), y_deserializer=CurrencyCollection.deserialize),
            state_update=HashUpdate.deserialize(cell_slice.load_ref().begin_parse())
        )
