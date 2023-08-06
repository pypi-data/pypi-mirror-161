from route_planner_common.exceptions import CustomException


class IncorrectParameterFormat(CustomException):
    status_code = 400
    message = 'INVALID_INPUT'
    description = ''

    def __init__(self, description):
        self.description = description

    def serialize_exception(self):
        return dict(message=self.message, description=self.description), self.status_code
