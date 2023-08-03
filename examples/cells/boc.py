from pytoniq_core import Cell, Builder, Slice


"""### initializing from boc: bytes, hex string and b64 string ###"""

cell = Cell.one_from_boc(b'\xb5\xee\x9cr\x01\x01\x02\x01\x00+\x00\x01K\x00\x00\x00\x0f\x80\r\xebx\xcf0\xdc\x0c\x86\x12\xc3\xb3\xbe\x00\x86rMI\x9b%\xcb/\xbb\xb1T\xc0\x86\xc8\xb5\x84\x17\xa2\xf0P\x01\x00\x00')

assert cell == Cell.one_from_boc('b5ee9c7201010201002b00014b0000000f800deb78cf30dc0c8612c3b3be0086724d499b25cb2fbbb154c086c8b58417a2f050010000')

assert cell == Cell.one_from_boc('te6ccgEBAgEAKwABSwAAAA+ADet4zzDcDIYSw7O+AIZyTUmbJcsvu7FUwIbItYQXovBQAQAA')

"""### works fine with multi roots ###"""

cells = Cell.from_boc('b5ee9c7201010201002b00014b0000000f800deb78cf30dc0c8612c3b3be0086724d499b25cb2fbbb154c086c8b58417a2f050010000')

print(cells)  # [<Cell 299[0000000F800DEB78CF30DC0C8612C3B3BE0086724D499B25CB2FBBB154C086C8B58417A2F040] -> 1 refs>]

"""### init slice and builder from boc ###"""

print(Slice.one_from_boc('te6ccgEBAgEAKwABSwAAAA+ADet4zzDcDIYSw7O+AIZyTUmbJcsvu7FUwIbItYQXovBQAQAA').__repr__())
# <Slice 299[0000000F800DEB78CF30DC0C8612C3B3BE0086724D499B25CB2FBBB154C086C8B58417A2F040] -> 1 refs>

print(Builder.one_from_boc('te6ccgEBAgEAKwABSwAAAA+ADet4zzDcDIYSw7O+AIZyTUmbJcsvu7FUwIbItYQXovBQAQAA').__repr__())
# <Builder 299[0000000F800DEB78CF30DC0C8612C3B3BE0086724D499B25CB2FBBB154C086C8B58417A2F040] -> 1 refs>

