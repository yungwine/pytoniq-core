import pytest

from pytoniq_core.crypto.ciphers import Client, get_shared_key

# RFC 7748, section 6.1
ALICE_PRIVATE = bytes.fromhex('77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a')
ALICE_PUBLIC = bytes.fromhex('8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a')
BOB_PRIVATE = bytes.fromhex('5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb')
BOB_PUBLIC = bytes.fromhex('de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f')
SHARED = bytes.fromhex('4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742')


def test_shared_key_rfc7748_vectors():
    assert get_shared_key(ALICE_PRIVATE, BOB_PUBLIC) == SHARED
    assert get_shared_key(BOB_PRIVATE, ALICE_PUBLIC) == SHARED


def test_shared_key_matches_between_adnl_peers():
    client = Client(Client.generate_ed25519_private_key())
    server = Client(Client.generate_ed25519_private_key())

    assert get_shared_key(client.x25519_private.encode(), server.x25519_public.encode()) == \
        get_shared_key(server.x25519_private.encode(), client.x25519_public.encode())


def test_shared_key_rejects_low_order_public_key():
    with pytest.raises(RuntimeError):
        get_shared_key(ALICE_PRIVATE, bytes(32))
