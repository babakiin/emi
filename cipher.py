from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util import Padding

def encrypt_file(input_path, output_path, password, chunk_size=4096):
    cipher = AESCipher(password, chunk_size)
    inp = open(input_path, "rb")
    out = open(output_path, "wb")
    data = inp.read(cipher.block_size)
    while data:
        out.write(cipher.encrypt(data))
        data = inp.read(cipher.block_size)
    inp.close()
    out.close()

def decrypt_file(input_path, output_path, password, chunk_size=4096):
    cipher = AESCipher(password, chunk_size)
    inp = open(input_path, "rb")
    out = open(output_path, "wb")
    data = inp.read(cipher.chunk_size)
    while data:
        out.write(cipher.decrypt(data))
        data = inp.read(cipher.chunk_size)
    inp.close()
    out.close()

class AESCipher(object):
    def __init__(self, password, chunk_size=4096):
        self.padding_bytes = 2
        self.block_size = chunk_size - (self.padding_bytes + AES.block_size)
        self.enc_block = chunk_size - AES.block_size
        self.chunk_size = self.enc_block + AES.block_size
        self.key = SHA256.new(password.encode("ascii")).digest()

    def encrypt(self, raw):
        if isinstance(raw, str):
            raw = raw.encode("utf8")
        elif not isinstance(raw, bytes):
            raise ValueError("The data must be an utf8 string or bytes")
        assert len(raw) <= self.block_size
        data = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        enc = cipher.encrypt(data)
        return iv + enc

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        data = enc[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain = cipher.decrypt(data)
        return self.unpad(plain)

    def pad(self, data_to_pad):
        padding_len = (self.block_size - len(data_to_pad)) % self.block_size
        padding = bytes([0]) * padding_len
        padding_size = self.bitefy(padding_len)
        padded_data = data_to_pad + padding + padding_size
        assert len(padded_data) == self.enc_block
        return padded_data

    def unpad(self, data_to_unpad):
        padding_len = self.unbitefy(data_to_unpad[-self.padding_bytes:])
        return data_to_unpad[:-(self.padding_bytes + padding_len)]

    def bitefy(self, number):
        return number.to_bytes(self.padding_bytes, byteorder="big")

    def unbitefy(self, sbytes):
        return int.from_bytes(sbytes, byteorder="big")

