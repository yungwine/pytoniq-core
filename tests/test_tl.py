from pytoniq_core.tl import TlGenerator


def get_schemas():
    generator = TlGenerator.with_default_schemas()
    schemas = generator.generate()
    return schemas


def test_geneartor():
    get_schemas()


def test_serialization():
    schemas = get_schemas()

    ser1 = schemas.serialize(
        schema=schemas.get_by_name('dht.ping'),
        data={'random_id': 142536475324}
    )

    ser2 = schemas.serialize(
        schema=schemas.get_by_class_name('dht.Pong')[-1],
        data={'random_id': 142536475324}
    )

    assert ser1 == ser2 == b'\x18?\xeb\xcb' + b'\xbc\x02\xd6/!\x00\x00\x00'  # tag + little-endian random id
