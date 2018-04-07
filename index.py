import argparse
import asyncio
import logging
import math
import mimetypes
import os
import re
import subprocess
import sys
import threading

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from cipher import AESCipher
from file_cipher import get_plain_size
from flask import Flask, Response, request

app = Flask(__name__)
LOG = logging.getLogger(__name__)
PATH = str()
PASSWORD = str()
CHUNK_SIZE = 8192
FILE_SIZE = 0
CIPHER = None
DESC = """A tool for viewing encrypted files."""

MB = 1 << 20
BUFF_SIZE = 10 * MB

def generate(path, start, length):
    chunk_jumped = math.floor(start / CIPHER.block_size)
    start_index = chunk_jumped * CIPHER.chunk_size
    chunks_to_read = math.ceil(length / CIPHER.block_size)
    read_length = chunks_to_read * CIPHER.chunk_size
    bytes_jumped = chunk_jumped * CIPHER.block_size
    bytes_to_jump = start - bytes_jumped
    fd = open(path, "rb")
    fd.seek(start_index)
    while length > 0:
        chunk = fd.read(CIPHER.chunk_size)
        plain = CIPHER.decrypt(chunk)
        len_plain = len(plain)
        plain = plain[bytes_to_jump:]
        bytes_to_jump -= len_plain - len(plain)
        len_plain = len(plain)
        if length < len_plain:
            length = 0
            yield plain[:length]
        else:
            length -= len_plain
            yield plain
    return

def partial_response(path, start, end=None):
    LOG.info("Requested: %s, %s", start, end)
    file_size = FILE_SIZE
    print("FILE SIZE = " + str(file_size))

    # determine (end, length)
    if end is None:
        end = file_size
    length = end - start

    response = Response(
        generate(path, start, length),
        206,
        mimetype='video/mp4',
        direct_passthrough=True,
    )
    response.headers.add(
        "Content-Range", "bytes {0}-{1}/{2}".format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        "Accept-Ranges", "bytes"
    )
    LOG.info("Response: %s", response)
    LOG.info("Response: %s", response.headers)
    return response

def get_range(request):
    rrange = request.headers.get("Range")
    LOG.info("Requested: %s", rrange)
    if not rrange:
        return 0, None
    m = re.match("bytes=(?P<start>\d+)-(?P<end>\d_)?", rrange)
    if m:
        start = m.group("start")
        end = m.group("end")
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None

@app.route("/video")
def video():
    start, end = get_range(request)
    return partial_response(PATH, start, end)

def start_tornado(event_loop, http_server, port):
    asyncio.set_event_loop(event_loop)
    http_server.listen(port)
    IOLoop.instance().start()

def main():
    global PATH, PASSWORD, CHUNK_SIZE, FILE_SIZE, CIPHER
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("file_path", type=str,
                        help="The encrypted file to be played.")
    parser.add_argument("password", type=str,
                        help="Password to decrypt the file.")
    parser.add_argument("-c", "--chunk_size", dest="chunk_size", type=int,
                        default=8192, help="The size of encryption chunks.")
    parser.add_argument("-p", "--port", dest="port", type=int, default=8080,
                        help="The port where the internal server will run.")
    args = parser.parse_args()
    PATH = args.file_path
    PASSWORD = args.password
    CHUNK_SIZE = args.chunk_size
    CIPHER = AESCipher(PASSWORD, CHUNK_SIZE)
    FILE_SIZE = get_plain_size(PATH, CIPHER)

    logging.basicConfig(level=logging.INFO)
    HOST = "127.0.0.1"
    http_server = HTTPServer(WSGIContainer(app))
    t1 = threading.Thread(target=start_tornado,
            args=[asyncio.get_event_loop(), http_server, args.port])
    t1.daemon = True
    t1.start()
    pid = subprocess.Popen(["vlc",
        "http://" + HOST + ":" + str(args.port) + "/video"])
    pid.wait()
    http_server.stop()
    IOLoop.instance().stop()
    sys.exit(0)

if __name__ == "__main__":
    main()
