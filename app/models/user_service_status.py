from enum import Enum


class UserServiceStatus(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text):
        self.sid = sid
        self.text = text

    ACTIVE = (1, 'active')
    INACTIVE = (2, 'inactive')
    EXPIRED = (3, 'expired')
    WAIT_FOR_PAYMENT = (4, 'waiting for payment')
