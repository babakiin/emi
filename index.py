import argparse
import asyncio
import logging
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
DESC = """A tool for viewing encrypted files."""

MB = 1 << 20
BUFF_SIZE = 10 * MB

def partial_response(path, start, end=None):
    LOG.info("Requested: %s, %s", start, end)
    file_size = os.path.getsize(path)

    # determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # read file
    with open(path, "rb") as fd:
        fd.seek(start)
        sbytes = fd.read(length)
    assert len(sbytes) == length

    response = Response(
        sbytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
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
    global PATH, PASSWORD, CHUNK_SIZE
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
    logging.basicConfig(level=logging.INFO)
    HOST = "0.0.0.0"
    http_server = HTTPServer(WSGIContainer(app))
    t1 = threading.Thread(target=start_tornado,
            args=[asyncio.get_event_loop(), http_server, args.port])
    t1.daemon = True
    t1.start()
    pid = subprocess.Popen(["vlc", "http://" + HOST + ":" +
        str(args.port) + "/video"])
    pid.wait()
    http_server.stop()
    IOLoop.instance().stop()
    sys.exit(0)

if __name__ == "__main__":
    main()
