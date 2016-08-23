import esptool
from time import sleep

import sys

ESP_ROM_BAUD = 115200


class Args:
    def __init__(self):
        self.port = "/dev/ttyUSB0"
        self.baud = ESP_ROM_BAUD
        self.flash_mode = "qio"
        self.flash_size = "4m"
        self.flash_freq = "40m"
        self.addr_filename = None
        self.no_progress = False
        self.verify = False


def flash(port, firmware_file, erase_flash):
    # Initialize parameters
    args = Args()
    args.port = port
    args.baud = 460800

    # Initialize device
    initial_baud = min(ESP_ROM_BAUD, args.baud)
    esp = esptool.ESPROM(args.port, initial_baud)

    if erase_flash:
        # Connect to the device
        esp.connect()

        # Erase flash
        esptool.erase_flash(esp, None)
        # Wait for flash erase
        for i in xrange(10):
            print ".",
            sleep(1)
        print ""

    # Reconnect
    esp.connect()

    # Prepare arguments for writing flash
    address = 0
    args.flash_size = "8m"
    args.addr_filename = [(address, open(firmware_file, "rb"))]

    # Write flash
    esptool.write_flash(esp, args)

if __name__ == '__main__':
    try:
        port = sys.argv[1]
        firmware_file = sys.argv[2]
        erase_flash = len(sys.argv) >= 4 and sys.argv[3] == "--erase"
        debug = len(sys.argv) >= 5 and sys.argv[4] == "--debug"
        if debug:
            print "Character test: "
            for i in range(0, 256):
                print chr(i),
            print ""
        flash(port, firmware_file, erase_flash)
    except:
        exit(1)
    exit(0)
