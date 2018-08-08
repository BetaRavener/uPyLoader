import glob
import sys

import serial


class ConnectionScanner:
    def __init__(self):
        self.port_list = []

    @staticmethod
    def _serial_ports(with_wifi):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial()
                # DTR & RTS: False == High, True == Low
                s.dtr = False
                s.rts = False
                s.port = port
                s.open()
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        if with_wifi:
            result.append("wifi")
        return result

    def scan_connections(self, with_wifi):
        self.port_list = ConnectionScanner._serial_ports(with_wifi)

