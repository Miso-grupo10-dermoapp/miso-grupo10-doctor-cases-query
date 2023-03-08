import boto3
from boto3.dynamodb.conditions import Attr

import app

def get_item():
    client = boto3.resource('dynamodb')
    try:
        table = client.Table(app.ENV_TABLE_NAME)
        result = table.scan(
              Select= 'ALL_ATTRIBUTES',
              FilterExpression=Attr('status').eq('created') | Attr('status').eq('available')
              )
        items = result['Items']
        if items:
            return items
        else:
            return []
    except Exception as e:
        raise RuntimeError('cannot retrieve data from db cause: ' + str(e))
