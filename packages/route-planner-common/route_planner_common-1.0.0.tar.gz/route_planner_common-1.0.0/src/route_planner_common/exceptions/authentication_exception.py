from route_planner_common.exceptions import CustomException


class AuthenticationException(CustomException):
    status_code = 500
    message = 'SERVER_ERROR'
    description = 'Failed to authenticate, please try again later'

    def serialize_exception(self):
        return dict(message=self.message, description=self.description), self.status_code
