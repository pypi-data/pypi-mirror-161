from route_planner_common.exceptions import CustomException
from route_planner_common.utils.util import Util
from werkzeug.exceptions import HTTPException


def handle_exception(e):
    print('in handle_exception')
    print(e)
    if isinstance(e, CustomException):
        response, status_code = e.serialize_exception()
        for key in list(response.keys()):
            if response[key] is None or response[key] == '':
                del response[key]
        return response, status_code

    if isinstance(e, HTTPException) and hasattr(e, 'description') and hasattr(e, 'code'):
        return dict(message=e.description), e.code

    Util.print_traceback()

    import os
    if not os.getenv('IS_DEV'):
        from google.cloud import error_reporting
        client = error_reporting.Client()
        client.report_exception(e)

    return dict(message='SERVER_ERROR', description='Something went wrong'), 500
