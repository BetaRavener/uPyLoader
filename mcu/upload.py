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
    suc = False
    with open("file_name.py", "wb") as f:
        while True:
            data = read_timeout(uart, 2)
            if not data or data[0] != ord("#"):
                x = uart.write(b"#2")
                break
            count = data[1]
            if count == 0:
                suc = True
                break
            data = read_timeout(uart, count)
            if data:
                esc = False
                for c in data:
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