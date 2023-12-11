from pytoniq_core.boc import HashMap, Builder, Address


def test_ser():
    hashmap = HashMap(key_size=267,
                      key_serializer=lambda src: Builder().store_address(src).end_cell().begin_parse().load_uint(267),
                      value_serializer=lambda src, dest: dest.store_coins(src))

    hashmap.set(key=Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG'), value=15) \
        .set(key=Address('EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N'), value=10)
    assert hashmap.serialize().hash.hex() == 'c279e85752ad418d54a023d5d391066fa6a560450f9562dcecfa6e6641393b6a'


def test_parse():
    hashmap = HashMap(key_size=267,
                      key_serializer=lambda src: Builder().store_address(src).end_cell().begin_parse().load_uint(267),
                      value_serializer=lambda src, dest: dest.store_coins(src))

    hashmap.set(key=Address('EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG'), value=15) \
        .set(key=Address('EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N'), value=10)

    assert hashmap.serialize().begin_parse().load_hashmap(267, value_deserializer=lambda i: i.load_coins()) == {118621468258109555883414559823777639640406072296410285331234498098430527437346690: 15, 118630747841378569603204119301805376564831504145530059638093173869611524683674024: 10}
