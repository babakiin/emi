import asyncio
import logging
import mimetypes
import os
import re
import subprocess
import sys
import threading

from flask import Flask, Response, request

app = Flask(__name__)
LOG = logging.getLogger(__name__)

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

@app.route("/")
def home():
    return "Hello, World!"

@app.route("/video")
def video():
    path = "videos/Nightly.mp4"
    start, end = get_range(request)
    return partial_response(path, start, end)

def start_server(port):
    app.run(host="127.0.0.1", port=port)

def main():
    logging.basicConfig(level=logging.INFO)
    port = 8080
    t1 = threading.Thread(target=start_server, args=(port,))
    t1.daemon = True
    t1.start()
    pid = subprocess.Popen(["vlc",
        "http://127.0.0.1" + ":" + str(port) + "/video"])
    pid.wait()
    sys.exit(0)

if __name__ == "__main__":
    main()
