#!/usr/bin/env python3
"""Tool for encrypting and decrypting files"""

import argparse
from cipher import encrypt_file, decrypt_file

DESC = """Tool writen in pure Python 3 to encrypt and decrypt large files."""

def main():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("input", type=str, help="The path to the input file.")
    parser.add_argument("output", type=str, help="The path to the output file.")
    parser.add_argument("password", type=str,
                        help="Password to encrypt/decrypt the file.")
    parser.add_argument("-e", "--encrypt", dest="encrypt", action="store_true",
                        help="If you want to encrypt the input file.")
    parser.add_argument("-d", "--decrypt", dest="decrypt", action="store_true",
                        help="If you want to decrypt the input file.")
    parser.add_argument("-c", "--chunk_size", dest="chunk_size", type=int,
                        default=8192, help="The size of encryption chunks.")
    args = parser.parse_args()
    mode_error = "You should provide either --encrypt or --decrypt option."
    if args.encrypt and args.decrypt:
        raise ValueError(mode_error)
    elif args.encrypt:
        encrypt_file(args.input, args.output, args.password, args.chunk_size)
    elif args.decrypt:
        decrypt_file(args.input, args.output, args.password, args.chunk_size)
    else:
        raise ValueError(mode_error)

if __name__ == "__main__":
    main()
    
