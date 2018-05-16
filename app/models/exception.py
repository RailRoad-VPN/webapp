from enum import IntEnum
from flask_babel import _

class DFNError(IntEnum):
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    UNKNOWN_ERROR_CODE = (0, _('Internal Server Error'), _(''))

    USER_LOGIN_NOT_EXIST = (1, _('Unable to log in. Please check the login details.'), _(''))
    USER_SIGNUP_EMAIL_BUSY = (2, _('Email is busy.'), _(''))
    USER_LOGIN_BAD_PASSWORD = (3, _('Unable to log in. Please check the login details.'), _(''))
    USER_UNKNOWN_ERROR = (4, _('Unable to log in. Please check the login details.'), _(''))
