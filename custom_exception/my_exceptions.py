class ContentNotFound(Exception):
    def __init__(self, message="Details not found", status_code=404, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ContentAlreadyExist(Exception):
    def __init__(self, message="Already exist", status_code=409, error_code=1002):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class PermissionNotAllowed(Exception):
    def __init__(self, message="illegal operation", status_code=400, error_code=1002):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)