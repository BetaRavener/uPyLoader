#V2
import sys
import time


def _read_timeout(cnt, timeout_ms=2000):
    s_time = time.ticks_ms()
    data = sys.stdin.buffer.read(cnt)
    if time.ticks_diff(time.ticks_ms(), s_time) > timeout_ms or len(data) != cnt:
        return None
    return data


def _upload():
    suc = False
    with open("file_name.py", "wb") as f:
        while True:
            d = _read_timeout(2)
            if not d or d[0] != ord("#"):
                x = sys.stdout.buffer.write(b"#2")
                break
            cnt = d[1] & 0x7F
            if cnt == 0:
                suc = True
                break
            d = _read_timeout(cnt)
            if d:
                esc = False
                for c in d:
                    if c == 0:
                        esc = True
                        continue
                    x = f.write(bytes([c & 0x0F if esc else c]))
                    esc = False
                x = sys.stdout.buffer.write(b"#1")
            else:
                x = sys.stdout.buffer.write(b"#3")
                break
    x = sys.stdout.buffer.write(b"#0" if suc else b"#4")


_upload()
