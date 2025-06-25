import pytest

from pytoniq_core import Cell, MessageAny, ExternalAddress
from pytoniq_core.boc import begin_cell, Slice, Address


def test_boc():

    empty_cs = Slice.one_from_boc('b5ee9c72010101010002000000')

    assert empty_cs.remaining_bits == 0
    assert empty_cs.remaining_refs == 0


def test_bits():

    for btcnt in range(0, 1023):
        cs = begin_cell().store_bits('1' * btcnt).end_cell().begin_parse()
        assert cs.remaining_bits == btcnt
        assert cs.load_bits(btcnt).to01() == '1' * btcnt


def test_preload():

    cs = begin_cell().store_int(-100, 100).end_cell().begin_parse()

    cs.skip_bits(15)

    assert cs.preload_int(85) == -100
    assert cs.remaining_bits == 85


@pytest.mark.parametrize("addr", [
    'EQDtFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74p4q2',
    None,
    '0:ed1691307050047117b998b561d8de82d31fbf84910ced6eb5fc92e7485ef8a7',
    '-1:ed1691307050047117b998b561d8de82d31fbf84910ced6eb5fc92e7485ef8a7',
    (0, b'\xed\x16\x910pP\x04q\x17\xb9\x98\xb5a\xd8\xde\x82\xd3\x1f\xbf\x84\x91\x0c\xedn\xb5\xfc\x92\xe7H^\xf8\xa7'),
    'Ef_tFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74p3X-',
    'EQHtFpEwcFAEcRe5mLVh2N6C0x-_hJEM7W61_JLnSF74pwdq'
])
def test_address(addr):
    if isinstance(addr, tuple):
        cs = begin_cell().store_address(Address(addr)).end_cell().begin_parse()
    else:
        cs = begin_cell().store_address(addr).end_cell().begin_parse()

    if addr is None:
        assert cs.preload_address() is None
        assert cs.load_address() is None
        return

    assert cs.preload_address() == Address(addr)
    assert cs.load_address() == Address(addr)


def test_var_ints():

    assert begin_cell().store_var_int(-10, 10).to_slice().load_var_int(10) == -10
    assert begin_cell().store_var_uint(10, 10).to_slice().load_var_uint(10) == 10

    assert begin_cell().store_var_int(0, 10).to_slice().load_var_int(10) == 0
    assert begin_cell().store_var_uint(0, 10).to_slice().load_var_uint(10) == 0

    assert begin_cell().store_var_int(1, 1).to_slice().load_var_int(1) == 1
    assert begin_cell().store_var_int(1, 1).to_slice().preload_var_int(1) == 1


def test_copy():
    c = begin_cell().store_uint(15, 32).store_ref(Cell.empty()).end_cell()

    cs = c.begin_parse()
    cs.skip_bits(10)
    cs.load_ref()
    cs2 = cs.copy()
    assert cs2.remaining_refs == 0
    assert cs2.remaining_bits == 22


def test_empty_ext_addr():

    a = ExternalAddress(address=None, length=0)
    assert a.external_address is None
    assert a.len == 0
    assert str(a) == 'ExternalAddress<None>'

    a1 = a.to_cell().begin_parse().load_address()
    assert a1.external_address is None
    assert a1.len == 0

    a2 = a.to_cell().begin_parse().preload_address()
    assert a2.external_address is None
    assert a2.len == 0

    # message example with empty external address from mainnet
    m = MessageAny.deserialize(Slice.one_from_boc('b5ee9c720101030100a700015fe0077b12d86ad2f15a1a2fc0ec1115b1706f3904f0588f0158b5a589638cc21b8c520000003532342cfb0568541a68600101dd0000500161f5ebc497e0bf46b6a53a0bae46aa04018006d01aeeec276b151a419bf14e6354acbc6e9fc144b9221b5ddccb4966ea005690018a2e1c7e316821626399dcf1778c38e7f12901c17d5d2bbe8afc2130c2981f280000000400040000000000000003fffffffd02faf08020020000'))
    assert m.info.dest.external_address is None
    assert m.info.dest.len == 0

