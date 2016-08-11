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
suc = False
with open("file_name.py", "wb") as f:
    while True:
        data = read_timeout(uart, 4)
        if not data or data[0] != ord("#"):
            x = uart.write(b"#2")
            break
        count = int(data[1:])
        if count == 0:
            suc = True
            break
        data = read_timeout(uart, count)
        if data:
            x = f.write(data)
            # Send ACK
            x = uart.write(b"#1")
        else:
            x = uart.write(b"#3")
            break
x = uart.write(b"#1#" if suc else b"#0#")
