#V1
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


def main():
    uart = UART(0, 115200)
    start = read_timeout(uart, 3)
    suc = True
    if start == b"###":
        with open("file_name.py", "rb") as f:
            n = 64
            while True:
                chunk = f.read(64)
                if not chunk:
                    break
                x = uart.write(b"".join([b"#", bytes([len(chunk)]), chunk]))
                ack = read_timeout(uart, 2)
                if not ack or ack != b"#1":
                    suc = False
                    break

            # Mark end
            if suc:
                x = uart.write(b"#\0")
        check = read_timeout(uart, 3)

main()