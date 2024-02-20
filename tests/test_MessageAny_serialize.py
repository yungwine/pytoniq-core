from pytoniq_core.tlb import MessageAny, ExternalMsgInfo, InternalMsgInfo, CurrencyCollection
from pytoniq_core.tlb.block import ExtraCurrencyCollection
from pytoniq_core.boc import Address, Cell, Builder

from pytoniq_core.tlb.account import StateInit

def test_ser():
    test_addr = Address("EQDLjulz89Z90ReVL-a9TTKc5ON0PVhCHVGx3pkvzX5Qzt3S")
    info = ExternalMsgInfo(test_addr, test_addr, 0)
    body = Builder().store_bits([1,] * 482).end_cell()
    message = MessageAny(info = info, init = None, body = body)
    message.serialize()
