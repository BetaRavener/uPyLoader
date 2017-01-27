import esptool
import argparse
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
        esptool.erase_flash(esp, args)

    if not firmware_file:
        return

    # Reconnect
    esp.connect()

    # Prepare arguments for writing flash
    address = 0
    args.flash_size = "detect"
    args.addr_filename = [(address, open(firmware_file, "rb"))]

    # Write flash
    esptool.write_flash(esp, args)
    print "Done writing new firmware."

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('port', type=str)
        parser.add_argument('--fw', type=str, action='store')
        parser.add_argument('--erase', action='store_true')
        parser.add_argument('--debug', action='store_true')
        args = parser.parse_args()

        if args.debug:
            print "Character test: "
            for i in range(0, 256):
                print chr(i),
            print ""
        flash(args.port, args.fw, args.erase)
    except Exception as e:
        exit(1)
    exit(0)
