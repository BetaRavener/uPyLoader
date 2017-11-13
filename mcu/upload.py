#V2
import sys
import time
from ubinascii import a2b_base64


def _read_timeout(cnt, timeout_ms=2000):
    s_time = time.ticks_ms()
    data = sys.stdin.read(cnt)
    if time.ticks_diff(time.ticks_ms(), s_time) > timeout_ms or len(data) != cnt:
        return None
    return data


def _upload():
    suc = False
    with open("file_name.py", "wb") as f:
        while True:
            d = _read_timeout(3)
            if not d or d[0] != "#":
                x = sys.stdout.write("#2")
                break
            cnt = int(d[1:3])
            if cnt == 0:
                suc = True
                break
            d = _read_timeout(cnt)
            if d:
                x = f.write(a2b_base64(d))
                x = sys.stdout.write("#1")
            else:
                x = sys.stdout.write("#3")
                break
    x = sys.stdout.write("#0" if suc else "#4")


_upload()
