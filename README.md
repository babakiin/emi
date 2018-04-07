# Encryption Multimedia Index

The Encryption Multimedia Layer (EMI) is a middleman between your files and the multimedia applications that run them. For instance, MP4 files and the VLC mediaprogram.

It is responsible for reading encrypted data from your hard disk, decrypting the data and send it to the program. This way, you can keep your files completely safe (encrypted) and still access them through EMI, without ever writing decrypted data back to the disk.

Your file is read in chunks, these chunks are decrypted separately are sent to streaming-capable applications, like VLC. So there is never a decrypted copy of your file in any place of your hard-drive, unless your multimedia application is doing it.

## How to install

Copy this repository into some convinient location of your hard drive and install the Python 3 requirements using pip.

## How to use

Use the `file_cipher.py` script to encrypt files into your hard drive. Like so:

```
$ python3 file_cipher.py --encrypt <SOME_FILE> <OUTPUT_FILE_NAME> "<PASSWORD>"
```

Note: it is a good idea to pass your password between quotes so you can use special characters.

Now, to play the file, you just have to use the `index.py` script, like so:

```
$ python3 index.py <ENCRYPTED_FILE> "<PASSWORD>"
```

Note: again, it is a good idea to provide the password inside double quotes. Of course, the password given here must match the one given when the file was encrypted. This will only work with files which were encrypted using the `file_cipher.py` script.

## How to get a file back to decrypted form

Use again the `file_cipher.py` again. Like so:

```
$ python3 file_cipher.py --decrypt <ENCRYPTED_FILE> <OUTPUT_FILE_NAME> "<PASSWORD>"

```

Note: of course, the provided password must match the password given when the file was encrypted.

## How to uninstall EMI

Simply use the step above to get your files back and them remove the folder where you cloned this repository.
