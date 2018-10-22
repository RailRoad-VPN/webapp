from enum import Enum


class PaymentStatus(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text):
        self.sid = sid
        self.text = text

    SUCCESS = (1, 'success')
    FAILED = (2, 'failed')
    PROCESSING = (3, 'processing')

