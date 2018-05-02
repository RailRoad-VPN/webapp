class AjaxResponse(object):
    success = False
    next = None
    data = {}
    errors = []

    def __init__(self, success: bool, next: str = None, data: dict = None, errors: list = None):
        self.success = success
        self.next = next
        self.data = data
        self.errors = errors

    def add_data(self, key, value):
        if self.data is None:
            self.data = {}

        self.data[key] = value

    def set_data(self, data):
        self.data = data

    def add_error(self, error):
        if self.errors is None:
            self.errors = []
        self.errors.append(error.serialize())

    def set_success(self):
        self.success = True

    def set_failed(self):
        self.success = False

    def set_next(self, url):
        self.next = url

    def serialize(self):
        errors_dict = {}
        if self.errors is not None:
            for ob in self.errors:
                errors_dict[ob.code] = ob.serialize()
        return {
            'success': self.success,
            'data': self.data,
            'errors': errors_dict,
        }