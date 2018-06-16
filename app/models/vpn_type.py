from enum import Enum


class VPNType(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, value, description):
        self.sid = sid
        self.value = value
        self.description = description

    UNKNOWN = (0, 'unknown', 'Unknown, for reports only')
    OPENVPN = (1, 'openvpn', 'Standard OpenVPN server')
    IKEV2 = (2, 'ikev2', 'IPSec w IKEv2')
