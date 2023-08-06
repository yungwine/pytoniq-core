import typing

import hashlib
import x25519

from nacl.signing import SigningKey as ed25519Private, VerifyKey as ed25519Public
from nacl.public import PublicKey as x25519Public, PrivateKey as x25519Private

from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES


class Crypto:
    magic = b'\xc6\xb4\x13\x48'
    magic_aes = b'\xd4\xad\xbc-'

    def __init__(self):
        raise NotImplementedError

    def get_key_id(self):
        return hashlib.sha256(self.magic + self.ed25519_public.encode()).digest()

    def get_aes_key_id(self):
        return hashlib.sha256(self.magic_aes + self.ed25519_private.encode()).digest()


class Server(Crypto):

    def __init__(self, host: str, port: int, pub_key: bytes):
        self.host = host
        self.port = port
        self.ed25519_public = ed25519Public(pub_key)
        self.x25519_public = self.ed25519_public.to_curve25519_public_key()


class Client(Crypto):
    def __init__(self, ed25519_private_key: bytes) -> None:
        self.ed25519_private = ed25519Private(ed25519_private_key)
        self.ed25519_public = self.ed25519_private.verify_key
        self.x25519_private = self.ed25519_private.to_curve25519_private_key()
        self.x25519_public = self.x25519_private.public_key

    @staticmethod
    def generate_ed25519_private_key() -> bytes:
        return bytes(ed25519Private.generate())

    def sign(self, message: bytes) -> bytes:
        return get_signature(self.ed25519_private, message)


class AdnlChannel:
    """
    A class that represents adnl channel with node
    """

    def __init__(self, client: Client, server: Server, local_id: bytes, peer_id: bytes):
        self.client_channel = client
        self.server_channel = server
        self.channel_shared = get_shared_key(self.client_channel.x25519_private.encode(), self.server_channel.x25519_public.encode())
        if local_id > peer_id:
            self.enc_key = self.channel_shared
            self.dec_key = self.channel_shared[::-1]
        elif local_id < peer_id:
            self.enc_key = self.channel_shared[::-1]
            self.dec_key = self.channel_shared
        else:
            self.enc_key = self.channel_shared
            self.dec_key = self.channel_shared
        self.client_aes_key_id = get_key_aes_id(self.enc_key)
        self.server_aes_key_id = get_key_aes_id(self.dec_key)

    def encrypt(self, data: bytes) -> bytes:
        checksum = hashlib.sha256(data).digest()
        enc_cipher = create_aes_ctr_sipher_from_key_n_data(self.enc_key, checksum)
        data = aes_ctr_encrypt(enc_cipher, data)
        return self.client_aes_key_id + checksum + data

    def decrypt(self, encrypted_data: bytes, checksum: bytes) -> bytes:
        dec_cipher = create_aes_ctr_sipher_from_key_n_data(self.dec_key, checksum)
        return aes_ctr_decrypt(dec_cipher, encrypted_data)


def get_random(bytes_size: int) -> bytes:
    return get_random_bytes(bytes_size)


def create_aes_ctr_sipher_from_key_n_data(key: bytes, data: bytes):
    return create_aes_ctr_cipher(key[0:16] + data[16:32], data[0:4] + key[20:32])


def create_aes_ctr_cipher(key: bytes, iv: bytes):
    if len(key) != 32:
        raise Exception('key should be 32 bytes exactly!')

    cipher = AES.new(key, AES.MODE_CTR, initial_value=iv, nonce=b'')
    # cipher = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()

    return cipher


def get_key_aes_id(key: bytes):
    return hashlib.sha256(b'\xd4\xad\xbc-' + key).digest()


def aes_ctr_encrypt(cipher, data: bytes) -> bytes:
    # return cipher.encryptor().update(data)
    return cipher.encrypt(data)


def aes_ctr_decrypt(cipher, data: bytes) -> bytes:
    # return cipher.decryptor().update(data)
    return cipher.decrypt(data)


def get_shared_key(private_key: bytes, public_key: bytes) -> bytes:
    """
    :param public_key: peer public x25519 key
    :param private_key: client private x25519 key
    :return: ECDH x25519 shared key
    """
    return x25519.scalar_mult(private_key, public_key)


def get_signature(private_key: ed25519Private, message: bytes) -> bytes:
    return ed25519Private(seed=private_key.encode()).sign(message)[:64]
