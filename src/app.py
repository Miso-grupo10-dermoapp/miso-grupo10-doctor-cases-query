
from db_service import get_item
from request_response_utils import return_error_response, return_status_ok

ENV_TABLE_NAME = "dermoapp-patient-cases"


def handler(event, context):
    try:
        print("lambda execution with contexts {0}".format(str(context)))
        response = get_item()
        return return_status_ok(response)
    except Exception as err:
        return return_error_response("cannot proceed with the request error: " + str(err), 500)
