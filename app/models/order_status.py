from enum import Enum


class OrderStatus(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text):
        self.sid = sid
        self.text = text

    NEW = (1, 'new')
    PROCESSING = (2, 'processing')
    SUCCESS = (3, 'success')
    FAILED = (4, 'failed')
