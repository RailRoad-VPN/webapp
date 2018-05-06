class DFNError(object):
    UNKNOWN_ERROR_CODE =    'DFN-000000'

    USER_LOGIN_NOT_EXIST =    'DFN-100000'
    USER_SIGNUP_EXIST =       'DFN-100000'
    USER_LOGIN_BAD_PASSWORD = 'DFN-100000'
    USER_UNKNOWN_ERROR =      'DFN-100000'


class DFNException(Exception):
    __version__ = 1

    code = None
    message = None
    data = None

    def __init__(self, message: str, code: int, data: dict = None, *args, **kwargs):
        super().__init__(*args)

        self.code = code
        self.message = message
        self.data = data


class APIException(DFNException):
    __version__ = 1

    http_code = None

    def __init__(self, message: str, code: int, http_code: int, data: dict = None, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)

        self.http_code = http_code
        self.data = data


class UserException(DFNException):
    __version__ = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserNotFoundException(UserException):
    __version__ = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
