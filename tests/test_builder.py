import pytest
import typing

import pytoniq_core
from pytoniq_core.boc import begin_cell, Builder, Address, Cell, ExternalAddress


@pytest.mark.parametrize("num,num_len", [
    (0, 1),
    (-1, 1),
    (2, 3),
    (-2, 2),
    (2**256-1, 257),
    (-2**256, 257),
    (0xefffffff, 33)
])
def test_int(num: int, num_len: int):
    builder = Builder()
    builder.store_int(num, num_len)
    assert builder.to_slice().load_int(num_len) == num


@pytest.mark.parametrize("num,num_len", [
    (0, 1),
    (1, 1),
    (4, 3),
    (2**256-1, 256),
    (2**256, 257),
    (0xefffffff, 32)
])
def test_uint(num: int, num_len: int):
    builder = Builder()
    builder.store_uint(num, num_len)
    assert builder.to_slice().load_uint(num_len) == num


@pytest.mark.parametrize("num,num_len", [
    (-2, 1),
    (1, 1),
    (2, 2),
    (2**256, 256),
    (-2**256, 256),
    (0xefffffff, 32)
])
def test_int_overflow(num: int, num_len: int):
    builder = Builder()
    with pytest.raises(OverflowError):
        builder.store_int(num, num_len)


@pytest.mark.parametrize("num,num_len", [
    (2, 1),
    (2, 1),
    (2**256, 256),
    (0xefffffff, 31)
])
def test_uint_overflow(num: int, num_len: int):
    builder = Builder()
    with pytest.raises(OverflowError):
        builder.store_uint(num, num_len)


def test_builder_bits():

    with pytest.raises(pytoniq_core.boc.tvm_bitarray.TvmBitarrayOverflowException):
        begin_cell().store_int(1, 1000).store_bits(bin(16777216).replace('0b', ''))

    builder = begin_cell()

    assert builder.available_bits == 1023
    assert builder.available_refs == 4

    builder.store_uint(1000, 10)

    assert builder.bits.to01() == bin(1000).replace('0b', '')
    assert builder.available_bits == 1013

    builder.store_ref(
        begin_cell().store_uint(1, 1).end_cell()
    )

    assert builder.available_refs == 3

    cs = builder.to_slice()

    assert cs.load_uint(10) == 1000
    assert cs.load_ref() == begin_cell().store_uint(1, 1).end_cell()


@pytest.mark.parametrize("uint,uint_len,int_,int_len,address,coins,string", [
    (15, 32, -15, 32, 'EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG', 10, 'very long string, ' * 100),
    (100, 10, -3, 3, 'Ef8zMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzM0vF', 10**18, 'short str'),
    (0, 1, -1, 1, Address('EQDtFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74p4q2'), 0, ''),
])
def test_builder_parse(
        uint: int,
        uint_len: int,
        int_: int,
        int_len: int,
        address: typing.Union[str, Address],
        coins: int,
        string: str,
):
    builder = (begin_cell()
               .store_uint(uint, uint_len)
               .store_address(address)
               .store_int(int_, int_len)
               .store_maybe_ref(begin_cell().end_cell())
               .store_coins(coins)
               .store_snake_string(string)
               )
    cs = builder.end_cell().begin_parse()

    assert cs.load_uint(uint_len) == uint
    assert cs.load_address() == Address(address)
    assert cs.load_int(int_len) == int_
    assert cs.load_maybe_ref() == begin_cell().end_cell() == Cell.empty()
    assert cs.load_coins() == coins
    assert cs.load_snake_string() == string

    assert cs.remaining_bits == 0 and cs.remaining_refs == 0


def test_builder_exotic():

    builder = Builder()
    ref1 = builder \
            .store_uint(15, 32) \
            .store_ref(
                Builder()
                .store_bit(1)
                .store_ref(
                    Builder().store_uint(14, 32).end_cell()
                ).end_cell()
            ) \
            .store_ref(
                Builder()
                .store_bit(0)
                .store_ref(
                    Builder().store_uint(12, 32).end_cell()
                )
                .end_cell()
            ) \
        .end_cell()

    ref2 = Builder() \
            .store_uint(11, 16) \
            .store_ref(
                Builder()
                .store_bits('1000')
                .store_ref(
                    Builder().store_address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG').end_cell()
                )\
                .store_ref(Builder().store_uint(100, 512).end_cell())\
                .end_cell()
            ) \
        .end_cell()

    cell = Builder().store_int(120, 24).store_ref(ref1).store_ref(ref2).end_cell()

    pruned1 = Builder(type_=1).store_uint(1, 8).store_bytes(b'\x01').store_bytes(ref1.hash).store_uint(2, 16).end_cell()
    pruned2 = Builder(type_=1).store_uint(1, 8).store_bytes(b'\x01').store_bytes(ref2[0][1].hash).store_uint(0, 16).end_cell()
    new_ref2 = Builder() \
            .store_uint(11, 16) \
            .store_ref(
                Builder()
                .store_bits('1000')
                .store_ref(
                    Builder().store_address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG').end_cell()
                )\
                .store_ref(pruned2)\
                .end_cell()
            ) \
        .end_cell()

    new_cell = Builder().store_int(120, 24).store_ref(pruned1).store_ref(new_ref2).end_cell()

    proof = Builder(type_=3).store_uint(3, 8).store_bytes(new_cell.get_hash(0)).store_uint(3, 16).store_ref(new_cell).end_cell()

    assert proof.is_exotic

    assert proof[0].get_hash(0) == cell.hash


def test_builder_ext_address():
    builder = Builder()
    builder.store_address(ExternalAddress(0x12345678, 32))
    assert builder.end_cell().begin_parse().load_address() == ExternalAddress(0x12345678, 32)
