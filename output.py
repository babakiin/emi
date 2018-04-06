from cipher import AESCipher

if __name__ == "__main__":
    cipher = AESCipher("mypass")
    fd = open("videos/Nightly.index", "rb")
    out = open("videos/Nightly.mp4", "wb")
    data = fd.read(cipher.chunk_size)
    while data:
        plain = cipher.decrypt(data)
        out.write(plain)
        data = fd.read(cipher.chunk_size)
    fd.close()
    out.close()
