from pytoniq_core import Cell, Builder
from pytoniq_core.tlb.account import Account, ShardAccount
import os

def test_account_regular():
    account = Cell.one_from_boc('b5ee9c720101030100a900026dc00f5f09760a78c84bab1153c4876ebde53f17942190f54b21c2d132a1d416259da20680ec433fbf6d600000cb7102293d0cd6ae72d34001020842028f452d7a4dfd74066b682365177259ed05734435be76b5fd4bd5d8af2b7c3d6800910505d1bf1f408006c0b20d2e4980a9656da6117470d08956a955da832f6167ccad80c1f9782e451002c44ea652d4092859c67da44e4ca3add6565b0e2897d640a2c51bfb370d8877fa')
    deserialized = Account.deserialize(account.begin_parse())

    assert deserialized.serialize().hash == account.hash


def test_storage_frozen():
    account = Cell.one_from_boc('b5ee9c7201010101005a0000afcff7294428f130c71b08e164eadbc699145b14eb4301dfd9f92ea6ca73ea0d7a27d2028051c33a4dd8852afb386a80000bae23276780c0e22a3ad11cd49d7c209be8e3badc53112b881c298c42242ca1917a56dac8d0b140')
    deserialized = Account.deserialize(account.begin_parse())

    assert deserialized.storage.state.type_ == "account_frozen"
    assert deserialized.serialize().hash == account.hash

def test_shard_account_regular():
    last_trans_hash = bytes(range(32))
    last_trans_lt = 1234
    assert len(last_trans_hash) == 32

    account = Cell.one_from_boc('b5ee9c7201010101005a0000afcff7294428f130c71b08e164eadbc699145b14eb4301dfd9f92ea6ca73ea0d7a27d2028051c33a4dd8852afb386a80000bae23276780c0e22a3ad11cd49d7c209be8e3badc53112b881c298c42242ca1917a56dac8d0b140')
    shard_account = Builder() \
        .store_ref(account) \
        .store_bytes(last_trans_hash) \
        .store_uint(last_trans_lt, 64)
    
    serialized = shard_account.end_cell()
    deserialized = ShardAccount.deserialize(serialized.begin_parse())
    serialized_using_shard_account = deserialized.serialize()

    assert deserialized.last_trans_hash == last_trans_hash
    assert deserialized.last_trans_lt == last_trans_lt
    assert deserialized.account.serialize().hash == account.hash
    assert serialized_using_shard_account.hash == serialized.hash
