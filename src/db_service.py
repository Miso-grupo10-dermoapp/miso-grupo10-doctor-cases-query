import boto3
from boto3.dynamodb import conditions
from boto3.dynamodb.conditions import Key, Attr

import app

def get_item(patient_id):
    client = boto3.resource('dynamodb')
    try:
        table = client.Table(app.ENV_TABLE_NAME)
        result = table.scan(FilterExpression=Attr('patient_id').contains(patient_id))
        items = result['Items']
        if items:
            return items
        else:
            return []
    except Exception as e:
        raise RuntimeError('cannot retrieve data from db cause: ' + str(e))
