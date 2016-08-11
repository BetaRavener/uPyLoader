import re


class IpHelper:
    @staticmethod
    def is_valid_ipv4(ip):
        """Validates IPv4 addresses.
        """
        pattern = re.compile(r"^\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3}$", re.VERBOSE | re.IGNORECASE)
        if pattern.match(ip) is None:
            return False
        for x in ip.split("."):
            val = int(x)
            if val < 0 or val > 255:
                return False
        return True
