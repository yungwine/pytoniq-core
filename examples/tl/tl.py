from pytoniq_core.tl import TlGenerator


"""### init TlGenerator from schemas stored in the library files and generate them ###"""

generator = TlGenerator.with_default_schemas()
schemes = generator.generate()

"""### get schemes ###"""

adnl_adr_sch = schemes.get_by_name('adnl.address.udp')

print(adnl_adr_sch)
# TL Schema adnl.address.udp №670da6e7 with args {'ip': 'int', 'port': 'int'}

adnl_adr_schemes = schemes.get_by_class_name('adnl.Address')
print(adnl_adr_schemes)
# [TL Schema adnl.address.udp №670da6e7 with args {'ip': 'int', 'port': 'int'}, TL Schema adnl.address.udp6 №e31d63fa with args {'ip': 'int128', 'port': 'int'}, TL Schema adnl.address.tunnel №092b02eb with args {'to': 'int256', 'pubkey': 'PublicKey'}, TL Schema adnl.address.reverse №27795286 with args {}]
assert adnl_adr_sch is adnl_adr_schemes[0]

"""### serialize ###"""

serialized = schemes.serialize(adnl_adr_sch, data={'ip': 10000, 'port': 15})

print(serialized)
# b"\xe7\xa6\rg\x10'\x00\x00\x0f\x00\x00\x00"

print(schemes.deserialize(serialized))
# ({'ip': 10000, 'port': 15}, 12)  # deserialized dict and read bytes amount
