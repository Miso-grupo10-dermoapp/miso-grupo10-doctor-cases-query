import json

from db_service import get_item
from request_validation_utils import validate_property_exist
from request_response_utils import return_error_response, return_status_ok

ENV_TABLE_NAME = "dermoapp-patient-cases"


def handler(event, context):
    try:
        print("lambda execution with context {0}".format(str(context)))
        if validate_property_exist("patient_id", event['pathParameters']):
                response = get_item(event['pathParameters']['patient_id'])
                return return_status_ok(response)
        else:
            return return_error_response("missing or malformed query params", 412)
    except Exception as err:
        return return_error_response("cannot proceed with the request error: " + str(err), 500)
