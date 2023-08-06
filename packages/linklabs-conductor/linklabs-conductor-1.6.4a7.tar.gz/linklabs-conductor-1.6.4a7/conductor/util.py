import re
import dateutil.parser
import logging

from enum import IntEnum

LOG = logging.getLogger(__name__)
NODE_TYPE_PATTERN = r'^\$([0-9]+)\$.*'


class DeviceType(IntEnum):
    GATEWAY_SYMPHONY = 101
    REPEATER_SYMPHONY = 201
    MOD_SYMPHONY = 301
    MOD_LTE_M = 303
    APP_TOKEN = 401
    MOD_VIRTUAL = 501
    MOD_SYMBLE = 502
    NONE = 999


def find_cls(parent, app_token):
    """ Will search through Node child objects to find the specific
    implementation for the requested application token.

    Args:
        parent(obj): The parent object, whose subclasses we will search
            through.
        app_token(str): The Applicaton Token that will statisfy the search.

    Returns:
        The correct Node Subclass when found, parent otherwise.
    """
    def rec(parent, app_tok):
        if app_tok == parent.application:
            return parent
        for sc in parent.__subclasses__():
            if sc.application == app_tok:
                return sc
            obj = rec(sc, app_tok)
            if obj:
                return obj
        return None
    obj = rec(parent, app_token)
    return obj if obj else parent


def get_device_type(module):
    """
    Gets the node type from the module field
    :param module: module field from uplink event
    :return: DeviceType IntEnum
    """
    types = [t.value for t in DeviceType]
    p = re.compile(NODE_TYPE_PATTERN)
    m = re.match(p, module)
    if m:
        node_type = int(m.groups()[0])
        if node_type in types:
            return DeviceType(node_type)
    return DeviceType.NONE


def parse_time(time_str):
    """ Parses a time string from Conductor into a datetime object. """
    return dateutil.parser.parse(time_str)


def format_time(dtime):
    """ Converts a `datetime` object into a string that Conductor
    understands. """
    return dtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


def hexlify(buff):
    """
    We write our own version of hexlify because python 3's version returns
    a binary string that can't be converted to JSON.
    """
    if isinstance(buff, str):
        buff = (ord(x) for x in buff)
    return ''.join('{:02X}'.format(x) for x in buff)


# TODO: Unit test that assert is raised when operating against non-Version objs
class Version(object):
    """ Represents a Software Version. """

    def __init__(self, major=0, minor=0, tag=0):
        self.major = int(major)
        self.minor = int(minor)
        self.tag = int(tag)

    def __str__(self):
        return "{}.{}.{}".format(self.major, self.minor, self.tag)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Version):
            if self.major != other.major:
                return False
            if self.minor != other.minor:
                return False
            if self.tag != other.tag:
                return False
            return True
        else:
            raise TypeError("Can only compare version objects to other version"
                            " objects!")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Version):
            if self.major < other.major:
                return True
            elif self.major == other.major:
                if self.minor < other.minor:
                    return True
                elif self.minor == other.minor:
                    if self.tag < other.tag:
                        return True
            return False
        else:
            raise TypeError("Can only compare version objects to other version"
                            " objects!")

    def __le__(self, other):
        if isinstance(other, Version):
            return self.__lt__(other) or self.__eq__(other)
        else:
            raise TypeError("Can only compare version objects to other version"
                            " objects!")

    def __gt__(self, other):
        if isinstance(other, Version):
            if self.major > other.major:
                return True
            elif self.major == other.major:
                if self.minor > other.minor:
                    return True
                elif self.minor == other.minor:
                    if self.tag > other.tag:
                        return True
            return False
        else:
            raise TypeError("Can only compare version objects to other version objects!")

    def __ge__(self, other):
        if isinstance(other, str):
            other = str_to_version(other)
        if isinstance(other, Version):
            return self.__gt__(other) or self.__eq__(other)
        else:
            raise TypeError("Can only compare version objects to other version objects!")

    def to_bytes(self):
        return bytearray.fromhex("{:02X}{:02X}{:04X}".format(self.major, self.minor, self.tag))

    def to_int(self):
        return int("{:02X}{:02X}{:04X}".format(self.major, self.minor, self.tag), 16)


def str_to_version(version_string: str) -> Version:
    """ Converts a string to a Version object. """
    if not version_string:
        return None
    return Version(int(version_string[:version_string.find('.')]),
                   int(version_string[version_string.find('.') + 1:version_string.find('.', 2)]),
                   int(version_string[version_string.rfind('.') + 1:]))


def mac_to_addr(mac):
    """ Converts a BLE MAC Address into a Conductor Endnode Address. """
    if len(mac) == 26:  # Mac is already in $501$0-0-0000XXX-XXXXXX format.
        return mac  # Done.
    elif len(mac) == 17:  # Mac is in XX:XX:XX:XX:XX:XX format.
        new_mac = mac.replace(':', '')  # Put mac in expected format.
    elif len(mac) == 12:  # Mac is in expected format.
        new_mac = mac
    else:
        # Mac is not in expected format.
        LOG.exception("Mac is in invalid format {} len : {}".format(mac, len(mac)))
        raise Exception("Mac is in invalid format")

    af_fmt = "{}-{}".format(new_mac[:3], new_mac[3:])
    return "$501$0-0-0000{}".format(af_fmt)


def addr_to_mac(addr):
    """ Converts a BLE MAC Address into a Conductor Endnode Address. """
    mac_addr = "{}:{}:{}:{}:{}:{}"

    if len(addr) == 17:  # Mac is already in XX:XX:XX:XX:XX:XX format.
        return addr
    elif len(addr) == 12:  # Mac is in XXXXXXXXXX format.
        return mac_addr.format(addr[:2], addr[2:4], addr[4:6], addr[6:8], addr[8:10], addr[10:])
    elif len(addr) == 20:
        return mac_addr.format("c0", "0" + addr[11:12], addr[12:14], addr[14:16], addr[16:18], addr[18:])
    elif len(addr) == 26:  # Mac is in $501$0-0-0000XXX-XXXXXX format.
        return mac_addr.format(addr[13:15], addr[15] + addr[17], addr[18:20], addr[20:22], addr[22:24], addr[24:])

    # Mac is not in expected format.
    LOG.exception("Address is in invalid format {} len : {}".format(addr, len(addr)))
    raise Exception("Address is in invalid format")
