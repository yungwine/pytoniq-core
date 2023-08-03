from pytoniq_core.boc import HashMap, Builder, Address


"""### ways to set values in hashmaps ###"""


hashmap = HashMap(key_size=267,  # key bit length
                  key_serializer=lambda src: Builder().store_address(src).end_cell().begin_parse().load_uint(267),  # function to serialize keys if they're not integers or type of dict.Key
                  value_serializer=lambda src, dest: dest.store_coins(src)  # function to serialize value if they're not cells
                  )

hashmap2 = HashMap(267).with_coins_values()

hashmap.set(key=Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG'), value=15) \
    .set(key=Address('EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N'), value=10)

hashmap2.set(key=Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG'), value=15) \
    .set(key=Address('EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N'), value=10)

assert hashmap.serialize() == hashmap2.serialize()


"""### serializing hashmaps ###"""

print(hashmap.map)

#  {118621468258109555883414559823777639640406072296410285331234498098430527437346690: 15, 118630747841378569603204119301805376564831504145530059638093173869611524683674024: 10}

hashmap_cell = hashmap.serialize()

# 22[817000] -> {
# 	277[BFF7ADE33CC37032184B0ECEF80219C935266C972CBEEEC553021B22D6105E8BC10878],
# 	277[BFC1EFEAA9731B94DA397E5E64622F5E63348B812AC5B4763A93F0DD201D0798D40850]
# }

empty_hashmap = HashMap(10)

print(empty_hashmap.serialize())  # None


"""### parsing hashmaps ###"""

print(HashMap.parse(hashmap_cell.begin_parse(), key_length=267))

# {118621468258109555883414559823777639640406072296410285331234498098430527437346690: <Slice 12[10F0] -> 0 refs>, 118630747841378569603204119301805376564831504145530059638093173869611524683674024: <Slice 12[10A0] -> 0 refs>}

def key_deserializer(src):
    return Builder().store_bits(src).to_slice().load_address()
def value_deserializer(src):
    return src.load_coins()

print(HashMap.parse(hashmap_cell.begin_parse(), key_length=267, key_deserializer=key_deserializer, value_deserializer=value_deserializer))

# {Address<EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG>: 15, Address<EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N>: 10}

"""### load hashmaps from slices ###"""

slice_with_hashmap = Builder().store_dict(hashmap_cell).end_cell().begin_parse()

print(slice_with_hashmap)

# 1[80] -> {
# 	22[817000] -> {
# 		277[BFF7ADE33CC37032184B0ECEF80219C935266C972CBEEEC553021B22D6105E8BC10878],
# 		277[BFC1EFEAA9731B94DA397E5E64622F5E63348B812AC5B4763A93F0DD201D0798D40850]
# 	}
# }

# load and parse HashmapE from reference
print(slice_with_hashmap.load_dict(key_length=267, key_deserializer=key_deserializer, value_deserializer=value_deserializer))

# {Address<EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG>: 15, Address<EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N>: 10}

# parse Hashmap directly from cell
print(hashmap_cell.begin_parse().load_hashmap(key_length=267, key_deserializer=key_deserializer, value_deserializer=value_deserializer))

# {Address<EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG>: 15, Address<EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N>: 10}
