import sys

from flask_babel import _
from flask_babel import lazy_gettext as _l

sys.path.insert(0, '../rest_api_library')
from response import APIErrorEnum

name = 'WEB-'
i = 0


def count():
    global i
    i += 1
    return i


def get_all_error_codes():
    return [e.code for e in DFNError]


class DFNError(APIErrorEnum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    UNKNOWN_ERROR_CODE = (name + str(count()), _l('Internal Server Error'), _('d'))

    USER_SIGNUP_EMAIL_BUSY = (name + str(count()), _l('Entered email is busy'), _('d'))
    USER_SIGNUP_FIELDS_INCOMPLETE = (name + str(count()), _l('Fill all fields to create account'), _('d'))

    USER_LOGIN_NOT_EXIST = (name + str(count()), _l('Unable to log in. Please check the login details'), _('d'))
    USER_LOGIN_BAD_PASSWORD = (name + str(count()), _l('Unable to log in. Please check the login details'), _('d'))
    USER_LOGIN_NOT_ENABLED = (name + str(count()), _l('Unable to log in. You account was deleted. If you want to restore account please contact support'), _('d'))
    USER_LOGIN_LOCKED = (name + str(count()), _l('Unable to log in. You account was locked. If you want to unlock account please contact support'), _('d'))
    USER_LOGIN_EXPIRED = (name + str(count()), _l('Unable to log in. You account was expired. If you want to restore account please contact support'), _('d'))

    USER_UNKNOWN_ERROR = (name + str(count()), _l('Unable to log in. Please check the login details'), _('d'))
    USER_PASSWORDS_NOT_MATCH = (name + str(count()), _l('Password does not match'), _('d'))

    USER_PROFILE_EMAIL_BUSY = (name + str(count()), _l('Entered email is busy'), _('d'))
    USER_PROFILE_BAD_EMAIL_DELETE_ACCOUNT = (name + str(count()), _l('You have entered wrong email. Enter correct email to delete your account'), _('d'))


class UserPolicyException(Exception):
    __version__ = 1

    error = None
    error_code = None
    developer_message = None

    def __init__(self, error: str, error_code: int, developer_message: str = None, *args):
        super().__init__(*args)
        self.error = error
        self.error_code = error_code
        self.developer_message = developer_message
