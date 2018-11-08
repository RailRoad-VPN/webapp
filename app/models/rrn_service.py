from enum import Enum
from flask_babel import _


class RRNServiceType(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text):
        self.sid = sid
        self.text = text

    VPN_SUBSCRIPTION = (1, _('vpn_subscription_type'))
