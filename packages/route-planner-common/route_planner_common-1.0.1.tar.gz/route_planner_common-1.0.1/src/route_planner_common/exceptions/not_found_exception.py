from route_planner_common.exceptions import CustomException


class NotFoundException(CustomException):
    status_code = 404
    message = 'NOT_FOUND'
    description = ''

    def __init__(self, description=''):
        self.description = description

    def serialize_exception(self):
        return dict(message=self.message, description=self.description), self.status_code
