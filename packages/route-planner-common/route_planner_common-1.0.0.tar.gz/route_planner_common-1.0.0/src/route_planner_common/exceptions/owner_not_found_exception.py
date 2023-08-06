
from route_planner_common.exceptions import CustomException


class OwnerNotFound(CustomException):
    status_code = 400
    message = 'INVALID_INPUT'
    description = 'Failed to authenticate company, please try again later'

    def serialize_exception(self):
        return dict(message=self.message, description=self.description), self.status_code
