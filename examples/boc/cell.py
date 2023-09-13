from pytoniq_core import begin_cell

builder = begin_cell().store_uint(15, 32).store_address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG').store_ref(begin_cell().end_cell())

cell1 = builder.end_cell()
cell2 = builder.store_uint(1, 1).end_cell()
cell3 = builder.store_uint(0, 1).end_cell()

"""### you can store cells in sets or dicts ###"""

s = {cell1: 1, cell2: 2}

print(cell1 in s)  # True

print(cell3 in s)  # False

print(s[cell2])  # 2




