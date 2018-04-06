from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util import Padding

class AESCipher(object):
    def __init__(self, password):
        self.block_size = 239 
        self.padding_bytes = 1
        self.enc_block = self.block_size + self.padding_bytes
        self.chunk_size = self.block_size + 1 + AES.block_size
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
        sbytes = bytes([number])
        assert len(sbytes) == self.padding_bytes
        return sbytes

    def unbitefy(self, sbytes):
        number = sbytes[0]
        return number

