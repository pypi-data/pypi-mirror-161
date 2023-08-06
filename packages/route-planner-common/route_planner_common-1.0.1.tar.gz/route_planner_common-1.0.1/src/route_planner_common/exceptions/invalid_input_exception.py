from route_planner_common.exceptions import CustomException


class InvalidInputException(CustomException):
    status_code = 400
    message = 'INVALID_INPUT'
    description = ''
    errors = dict()

    def __init__(self, description='', errors=None):
        self.description = description
        self.errors = errors

    def serialize_exception(self):
        return dict(message=self.message, description=self.description, errors=self.errors), self.status_code
