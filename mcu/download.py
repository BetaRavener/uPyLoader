from machine import UART
import time


def read_timeout(uart, count, retries=1000):
    data = b""
    for i in range(0, retries):
        rec = uart.read(count - len(data))
        if rec:
            data += rec
            if len(data) == count:
                return data
        time.sleep(0.01)
    return None


uart = UART(0, 115200)
start = read_timeout(uart, 3)
suc = True
if start == b"###":
    with open("file_name.py", "r") as f:
        n = 64
        while True:
            chunk = f.read(n)
            if not chunk:
                break
            x = uart.write(("#{:03}{}".format(len(chunk), chunk)).encode("utf-8"))
            ack = read_timeout(uart, 2)
            if not ack or ack != b"#1":
                suc = False
                break

        # Mark end
        if suc:
            x = uart.write(b"#000")
        data = None
        chunks = None
    check = read_timeout(uart, 3)
