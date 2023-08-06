import os
import logging
import json
import random
import time
from datetime import datetime, timedelta
import copy
from route_planner_common.utils.logger import Logger


class Util:

    @classmethod
    def check_if_integer(cls, key, value):
        try:
            convert_to_int = int(value)
        except:
            Logger.error(
                u"Key: {0}, does not contain a valid integer value. Value is: {1}".format(key, value))
            return False
        return True

    @classmethod
    def check_if_float(cls, key, value):
        try:
            convert_to_float = float(value)
        except:
            Logger.error(
                u"Key: {0}, does not contain a valid float value. Value is: {1}".format(key, value))
            return False
        return True

    @classmethod
    def check_if_json(cls, key, value):
        try:
            convert_to_json = json.loads(value)
        except:
            Logger.error(
                u"Key: {0}, does not contain a valid JSON value. Value is: {1}".format(key, value))
            return False
        return True

    @classmethod
    def check_if_string(cls, key, value):
        try:
            convert_to_string = str(value)
        except:
            Logger.error(
                u"Key: {0}, does not contain a valid string value. Value is: {1}".format(key, value))
            return False
        return True

    @classmethod
    def check_if_true(cls, key, value):
        new_value = None
        if isinstance(value, bool):
            new_value = str(value).lower()
        elif isinstance(value, bytes):
            new_value = value.lower()
        elif isinstance(value, str):
            new_value = value.lower()

        if new_value and new_value == 'true':
            return True
        else:
            Logger.info(
                u"Key: {0}, does not contain a valid TRUE boolean value. Value is: {1}".format(key, value))
            return False

    @classmethod
    def check_if_false(cls, key, value):
        new_value = None
        if isinstance(value, bool):
            new_value = str(value).lower()
        elif isinstance(value, bytes):
            new_value = value.lower()
        elif isinstance(value, str):
            new_value = value.lower()

        if new_value and new_value == 'false':
            return True
        else:
            Logger.info(
                u"Key: {0}, does not contain a valid FALSE boolean value. Value is: {1}".format(key, value))
            return False

    @classmethod
    def check_attribute_type(cls, key, value):
        if isinstance(value, bytes):
            return 'string'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, dict):
            return 'dict'
        elif isinstance(value, list):
            return 'list'

    @classmethod
    def generate_random_string(cls):
        return cls.get_uuid()

    @classmethod
    def get_uuid(cls):
        import uuid
        return str(uuid.uuid4())

    @classmethod
    def upload_file_to_bucket(cls, payload, company_id, unique_id, unique_key):
        from google.cloud import storage
        if not company_id:
            company_id = 9999999999999999
        try:
            GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
            GCS_ROUTE_OPTIMIZATION_RESULT_PATH_PREFIX = os.getenv(
                'GCS_ROUTE_OPTIMIZATION_RESULT_PATH_PREFIX')

            bucket_name = GCS_BUCKET_NAME
            destination_blob_name = GCS_ROUTE_OPTIMIZATION_RESULT_PATH_PREFIX.format(
                company_id=company_id,
                optimization_id=unique_id)

            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob('{}_{}'.format(
                destination_blob_name, unique_key))

            # blob.upload_from_string(data=json.dumps({'payload': payload}), content_type='application/json')
            Logger.info(u'file path is : {} '.format(payload))
            with open(payload, "rb") as my_file:
                blob.upload_from_file(my_file, num_retries=10)
            blob.make_public()
            Logger.info(u"Blob {} is publicly accessible at {}".format(
                blob.name, blob.public_url))
            return blob.public_url
        except Exception as file_upload_exception:
            Logger.info(
                'error uploading data to bucket, optimization will not be initiated')
            Logger.info(file_upload_exception)
            return None

    @classmethod
    def save_and_upload_file_to_bucket(cls, filename, company_id, unique_id, unique_key, data=None, file_to_save=None, file_path_to_save=None):
        if data is not None:
            file_path_to_save = os.path.join('/', filename)
            file_to_save = open(file_path_to_save, "w")
            file_to_save.writelines([json.dumps(data)])
            file_to_save.close()
        elif not file_to_save or not file_path_to_save:
            return None
        Logger.info('file_path_to_save: {}'.format(file_path_to_save))
        return cls.upload_file_to_bucket(payload=file_path_to_save, company_id=company_id, unique_id=unique_id, unique_key=unique_key)

    @classmethod
    def download_file(cls, path, name=None):
        import requests
        try:
            file_download_request = requests.get(path)
            if file_download_request.status_code != 200:
                return None
        except Exception as e:
            Logger.info(e)
            return None
        return file_download_request.content

    @classmethod
    def get_request_content(cls, request, logging_info=None):
        request_content = None
        if request.method == 'POST':
            if request.headers.get('Content-Type') == 'x-www-form-urlencoded':
                request_content = request.form.to_dict()
            else:
                request_content = request.get_json()
        elif request.method == 'GET':
            request_content = request.args.to_dict()

        query_params = request.args.to_dict()

        Logger.info('query_params : {}' .format(
            query_params), logging_info=logging_info)
        Logger.info('request_content : {}' .format(
            request_content), logging_info=logging_info)

        return request_content, query_params

    @classmethod
    def log(cls, msg):
        Logger.info('{} {}'.format(datetime.now(), msg))

    @classmethod
    def get_owner_from_auth(cls, auth_info):
        from route_planner_common.exceptions import OwnerNotFound

        owner = auth_info.get('user', dict()).get('company_id', None)
        if not owner:
            raise OwnerNotFound()
        return owner

    @classmethod
    def get_user_id_from_auth(cls, auth_info):
        from route_planner_common.exceptions import UserIdNotFound

        userid = auth_info.get('user', dict()).get('userId', None)
        if not userid:
            raise UserIdNotFound()
        return userid

    @classmethod
    def is_valid_uuid(cls, uuid_to_test, version=4):
        from uuid import UUID
        try:
            uuid_obj = UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test

    @classmethod
    def generate_headers_for_arrivy_from_request(cls, request):
        headers = dict(request.headers)
        if headers.get('Host'):
            del headers['Host']
        if headers.get('Content-Length'):
            del headers['Content-Length']
        if headers.get('Re-Cookie'):
            headers['Cookie'] = headers.get('Re-Cookie')

        return headers

    @classmethod
    def load_dict(cls, _json):
        _json = _json if _json else dict()
        if _json and Util.check_attribute_type('_json', _json) != 'dict':
            return json.loads(_json)
        return _json

    @classmethod
    def is_admin(cls, request):
        import os
        return request.headers.get('Admin-Key') and request.headers.get('Admin-Key') == os.getenv('ADMIN_KEY')

    @classmethod
    def print_traceback(cls):
        import traceback
        Logger.info(traceback.format_exc())


# [START cloud_tasks_create_queue]


    @classmethod
    def enqueue_http_request(cls, url, payload=None, in_seconds=None):
        project = os.getenv('PROJECT_ID')
        location = os.getenv('LOCATION')
        queue_name = os.getenv('QUEUE_NAME')
        base_url = os.getenv('BASE_URL')

        if not url.startswith('http'):
            url = '{}/{}'.format(base_url, url)

        if not cls.does_queue_exists(project=project, location=location, queue_name=queue_name):
            Logger.info(
                'no queue exists with the name : {}, creating new queue'.format(queue_name))
            create_queue_response = cls.create_queue(
                project=project, queue_name=queue_name, location=location)
            Logger.info('create_queue_response is : {}'.format(
                create_queue_response))

        try:
            create_task_response = cls.create_http_task(project=project, queue=queue_name, location=location,
                                                        task_name='{}_{}'.format(
                                                            os.getenv('TASK_NAME_PREFIX'), cls.generate_random_string()),
                                                        url=url, payload=payload, in_seconds=in_seconds)

            return "success"
        except Exception as e:
            Logger.info('Exception in enqueue_http_request ')
            Logger.info(e)

        return "error"

    @classmethod
    def create_queue(cls, project, queue_name, location):
        """Create a task queue."""

        from google.cloud import tasks_v2

        # Create a client.
        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified location path.
        parent = f"projects/{project}/locations/{location}"

        # Construct the create queue request.
        queue = {"name": client.queue_path(project, location, queue_name)}

        # Use the client to create the queue.
        response = client.create_queue(
            request={"parent": parent, "queue": queue})

        Logger.info("Created queue {}".format(response.name))
        return response

# [END cloud_tasks_create_queue]

    @classmethod
    def does_queue_exists(cls, project, location, queue_name):
        from google.cloud import tasks_v2

        # projects/arrivy-sandbox/locations/us-central1/queues/worker-requests
        # Create a client.
        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified location path.
        parent = f"projects/{project}/locations/{location}"

        queue_full_name = client.queue_path(project, location, queue_name)

        # Use the client to obtain the queues.
        response = client.list_queues(request={"parent": parent})

        return len(list(filter(lambda q: q.name == queue_full_name, response))) > 0

# [START create_http_task]

    @classmethod
    def create_http_task(cls,
                         project, queue, location, url, payload=None, in_seconds=None, task_name=None
                         ):
        from google.cloud import tasks_v2
        from google.protobuf import timestamp_pb2, duration_pb2

        # [START cloud_tasks_create_http_task]
        """Create a task for a given queue with an arbitrary payload."""

        # Create a client.
        client = tasks_v2.CloudTasksClient()

        # TODO(developer): Uncomment these lines and replace with your values.
        # project = 'my-project-id'
        # queue = 'my-queue'
        # location = 'us-central1'
        # url = 'https://example.com/task_handler'
        # payload = 'hello' or {'param': 'value'} for application/json
        # in_seconds = 180
        # task_name = 'my-unique-task'

        # Construct the fully qualified queue name.
        parent = client.queue_path(project, location, queue)

        # Construct the request body.
        d = duration_pb2.Duration()
        d.FromSeconds(15)
        task = {
            "dispatch_deadline":  d,
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.POST,

                "url": url,  # The full url path that the task will be sent to.
            }
        }
        if payload is not None:
            if isinstance(payload, dict):
                # Convert dict to JSON string
                payload = json.dumps(payload)
                # specify http content-type to application/json
                task["http_request"]["headers"] = {
                    "Content-type": "application/json"}

            # The API expects a payload of type bytes.
            converted_payload = payload.encode()

            # Add the payload to the request.
            task["http_request"]["body"] = converted_payload

        if in_seconds is not None:
            # Convert "seconds from now" into an rfc3339 datetime string.
            d = datetime.utcnow() + timedelta(seconds=in_seconds)

            # Create Timestamp protobuf.
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            # Add the timestamp to the tasks.
            task["schedule_time"] = timestamp

        if task_name is not None:
            # Add the name to tasks.
            task["name"] = client.task_path(
                project, location, queue, task_name)

        # Use the client to build and send the task.
        response = client.create_task(request={"parent": parent, "task": task})

        Logger.info("Created task {}".format(response.name))
        # [END cloud_tasks_create_http_task]
        return response

# [END create_http_task]

    @classmethod
    def log_exception(cls, e):
        import os
        if not os.getenv('IS_DEV'):
            from google.cloud import error_reporting
            client = error_reporting.Client()
            client.report_exception(e)

    @classmethod
    def create_logging_info(cls, auth_info):
        owner = auth_info.get('user').get('company_id')
        session_id = cls.get_uuid()

        logging_info = 'Owner: {}, Session ID: {}'.format(owner, session_id)
        return logging_info
