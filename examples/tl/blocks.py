from pytoniq_core.tl.block import BlockIdExt

init_mainnet_block = BlockIdExt.from_dict({
    "root_hash": "61192b72664cbcb06f8da9f0282c8bdf0e2871e18fb457e0c7cca6d502822bfe",
    "seqno": 27747086,
    "file_hash": "378db1ccf9c98c3944de1c4f5ce6fea4dcd7a26811b695f9019ccc3e7200e35b",
    "workchain": -1,
    "shard": -9223372036854775808
})

print(init_mainnet_block)
# <TL BlockIdExt [wc=-1, shard=-9223372036854775808, seqno=27747086, root_hash=61192b72664cbcb06f8da9f0282c8bdf0e2871e18fb457e0c7cca6d502822bfe, file_hash=378db1ccf9c98c3944de1c4f5ce6fea4dcd7a26811b695f9019ccc3e7200e35b] >

print(init_mainnet_block.to_bytes()) # big-endian !
# b'\xff\xff\xff\xff\x80\x00\x00\x00\x00\x00\x00\x00\x01\xa7c\x0ea\x19+rfL\xbc\xb0o\x8d\xa9\xf0(,\x8b\xdf\x0e(q\xe1\x8f\xb4W\xe0\xc7\xcc\xa6\xd5\x02\x82+\xfe7\x8d\xb1\xcc\xf9\xc9\x8c9D\xde\x1cO\\\xe6\xfe\xa4\xdc\xd7\xa2h\x11\xb6\x95\xf9\x01\x9c\xcc>r\x00\xe3['
