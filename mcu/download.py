#V2
import sys
import time


def _read_timeout(cnt, timeout_ms=2000):
    s_time = time.ticks_ms()
    data = sys.stdin.buffer.read(cnt)
    if time.ticks_diff(time.ticks_ms(), s_time) > timeout_ms or len(data) != cnt:
        return None
    return data


def _download():
    if _read_timeout(3) != b"###":
        return
    with open("file_name.py", "rb") as f:
        while True:
            chunk = f.read(64)
            if not chunk:
                break
            x = sys.stdout.buffer.write(b"".join([b"#", bytes([len(chunk)]), chunk]))
            ack = _read_timeout(2)
            if not ack or ack != b"#1":
                return

        # Mark end
        x = sys.stdout.buffer.write(b"#\0")

_download()
