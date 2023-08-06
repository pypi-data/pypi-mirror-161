import requests
from functools import wraps
import json
from flask import request


def authorized(handler):
    @wraps(handler)
    def authorize(*args, **kwargs):
        from route_planner_common.utils.util import Util
        from route_planner_common.utils import Logger
        from route_planner_common.exceptions import CustomException, AuthenticationException
        import os
        arrivy_base_url = os.getenv('ARRIVY_BASE_URL')

        headers = Util.generate_headers_for_arrivy_from_request(request)

        url = arrivy_base_url + '/api/task_routes/route_optimization/authorize'
        data = dict(company_id="")

        if request.method == 'POST':
            if headers.get('Content-Type') == 'application/json':
                if request.get_json().get('company_id'):
                    data['company_id'] = request.get_json().get(
                        'company_id')
            elif headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                if request.form.get('company_id'):
                    data['company_id'] = request.form.get('company_id')
        elif request.method == 'GET':
            query_params = dict(request.args)
            url += '?' + \
                '&'.join([f'{key}={value}' for key,
                          value in query_params.items()])
            for key, value in query_params.items():
                data[key] = value

        query_params = dict(request.args)
        if query_params and query_params.get('company_id'):
            data['company_id'] = query_params.get('company_id')

        try:
            response = requests.post(
                url=url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                res = response.json()
                user = res.get('user')
                logging_info = None
                Logger.info('session found for user user_name: {}, email: {}. user_id: {}, company_id: {}, is_company:{}'.format(
                    user.get('userName'), user.get('emailAddress'), user.get('userId'), user.get('company_id'), user.get('is_company')))
                logging_info = Util.create_logging_info(res)
                Logger.info('logging_info is : {}'.format(logging_info))
                Logger.info('path is: {}'.format(request.url_rule),
                            logging_info=logging_info)
                Logger.info('url is: {}'.format(request.path),
                            logging_info=logging_info)

                return handler(auth_info=response.json(), logging_info=logging_info, *args, **kwargs)
            return response.json(), response.status_code
        except requests.RequestException as e:
            raise AuthenticationException(e)
        except requests.ConnectionError as e:
            raise AuthenticationException(e)
        except requests.HTTPError as e:
            raise AuthenticationException(e)
        except requests.Timeout as e:
            raise AuthenticationException(e)
        except requests.TooManyRedirects as e:
            raise AuthenticationException(e)
        except requests.URLRequired as e:
            raise AuthenticationException(e)
        except Exception as e:
            raise e

    # Renaming the function name:
    # authorize.__name__ = handler.__name__
    return authorize
