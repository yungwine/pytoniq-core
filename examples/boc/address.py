"""Here hou can see all possibilities you can do with Address class"""

from pytoniq_core import Address



""" 1. Initializing """

# 1 way: from string (any form)

address = Address('0:6f5bc67986e06430961d9df00433926a4cd92e597ddd8aa6043645ac20bd1782')  # raw hex
address = Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG')  # user-friendly bounceable
address = Address('UQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XglxD')  # user-friendly non-bounceable
address = Address('kQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XgroM')  # user-friendly bounceable test-only
address = Address('0QBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XgufJ')  # user-friendly non-bounceable test-only

# 2 way: from another instance of Address

address1 = Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG')
address2 = Address(address1)

# 3 way: from tuple (workchain, hash_part)

address = Address(
    (0, b'o[\xc6y\x86\xe0d0\x96\x1d\x9d\xf0\x043\x92jL\xd9.Y}\xdd\x8a\xa6\x046E\xac \xbd\x17\x82')
)


""" 2. Converting """

# Once you got instance of class Address, you can convert it to any form, using method `to_str()`:

# raw (hex) form:

address.to_str(is_user_friendly=False)  # 0:6f5bc67986e06430961d9df00433926a4cd92e597ddd8aa6043645ac20bd1782

# user-friendly form:

address.to_str(is_bounceable=True)  # EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG
address.to_str(is_bounceable=False)  # UQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XglxD

# test form:

address.to_str(is_test_only=True, is_bounceable=True)  # kQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XgroM
address.to_str(is_test_only=True, is_bounceable=False)  # 0QBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XgufJ

""" 3. Cell/Slice """

# you can convert address to cell just using `to_cell` method:

address.to_cell()  # <Cell 267[800DEB78CF30DC0C8612C3B3BE0086724D499B25CB2FBBB154C086C8B58417A2F040] -> 0 refs>

# or store in builder:

from pytoniq_core import Builder

Builder()\
 .store_address(address)\
 .end_cell()
