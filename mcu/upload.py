#V1
from machine import UART
import time

def read_timeout(uart, cnt, retries=1000):
    data = b""
    for i in range(0, retries):
        rec = uart.read(cnt - len(data))
        if rec:
            data += rec
            if len(data) == cnt:
                return data
        time.sleep(0.01)
    return None

def main():
    uart = UART(0, 115200)
    suc = False
    with open("file_name.py", "wb") as f:
        while True:
            d = read_timeout(uart, 2)
            if not d or d[0] != ord("#"):
                x = uart.write(b"#2")
                break
            cnt = d[1] & 0x7F
            if cnt == 0:
                suc = True
                break
            d = read_timeout(uart, cnt)
            if d:
                esc = False
                for c in d:
                    if c == 0:
                        esc = True
                        continue
                    x = f.write(bytes([c & 0x0F if esc else c]))
                    esc = False
                x = uart.write(b"#1")
            else:
                x = uart.write(b"#3")
                break
    x = uart.write(b"#1#" if suc else b"#0#")

main()