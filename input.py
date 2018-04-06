from cipher import AESCipher


if __name__ == "__main__":
    cipher = AESCipher("mypass")
    fd = open("videos/Night_Shift_Nurses_01_BaixarHentai.net.mp4", "rb")
    out = open("videos/Nightly.index", "wb")
    data = fd.read(cipher.block_size)
    while data:
        outdata = cipher.encrypt(data)
        out.write(outdata)
        data = fd.read(cipher.block_size)
    fd.close()
    out.close()
