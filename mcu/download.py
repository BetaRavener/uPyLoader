#V2
import sys
import time
from ubinascii import b2a_base64


def _read_timeout(cnt, timeout_ms=2000):
    s_time = time.ticks_ms()
    data = sys.stdin.read(cnt)
    if time.ticks_diff(time.ticks_ms(), s_time) > timeout_ms or len(data) != cnt:
        return None
    return data


def _download():
    if _read_timeout(3) != "###":
        return
    with open("file_name.py", "rb") as f:
        while True:
            chunk = f.read(48)
            if not chunk:
                break
            chunk = b2a_base64(chunk).strip()
            if isinstance(chunk, bytes):
                chunk = chunk.decode("ascii")
            cl = len(chunk)
            x = sys.stdout.write("".join(["#", "0" if cl < 10 else "", str(cl), chunk]))
            ack = _read_timeout(2)
            if not ack or ack != "#1":
                return

        # Mark end
        x = sys.stdout.write("#00")

_download()
