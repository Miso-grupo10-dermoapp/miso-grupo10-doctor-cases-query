import json
import os

import boto3
import moto
import pytest
from request_validation_utils import body_properties
import app

TABLE_NAME = "dermoapp-patient-cases"


@pytest.fixture
def lambda_environment():
    os.environ[app.ENV_TABLE_NAME] = TABLE_NAME


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def data_table(aws_credentials):
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            KeySchema=[
                {"AttributeName": "case_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "case_id", "AttributeType": "S"},
            ],
            TableName=TABLE_NAME,
            BillingMode="PAY_PER_REQUEST"
        )

        yield TABLE_NAME

@pytest.fixture
def load_table(data_table):
    client = boto3.resource("dynamodb")
    table = client.Table(app.ENV_TABLE_NAME)
    body = {
        'case_id': '123',
        'injury_type': 'test_inj',
        'shape': 'shape-test',
        'number_of_lessions': 'lesson_test',
        'distributions': 'test',
        'color': 'test-red',
        'patient_id': '123'
    }
    table.put_item(Item=body)
def test_givenValidInputRequestThenReturn200AndValidArray(lambda_environment, load_table):
    event = {
        "resource": "/patient/{patient_id}/case/{case_id}",
        "path": "/patient/123/case/123",
        "httpMethod": "GET",
        "pathParameters": {
            "patient_id": "123"
        },
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 200
    data = json.loads(lambdaResponse['body'])
    assert len(data) == 1
    for item in data:
        assert item['patient_id'] == '123'

def test_givenValidInputRequestThenReturn200AndEmptyArray(lambda_environment, load_table):
    event = {
        "resource": "/patient/{patient_id}/case/{case_id}",
        "path": "/patient/123/case/123",
        "httpMethod": "GET",
        "pathParameters": {
            "patient_id": "1234"
        },
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 200
    data = json.loads(lambdaResponse['body'])
    assert len(data) == 0


def test_givenMissingQueryParamsOnRequestThenReturnError412(lambda_environment, data_table):
    event = {
        "resource": "/patient/{patient_id}/case/{case_id}",
        "path": "/patient/123/case/123",
        "httpMethod": "GET",
        "pathParameters": {
        },
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 412
    assert '{"message": "missing or malformed query params"}' in lambdaResponse['body']


def test_givenRequestWithErrorInDBThenReturnError500(lambda_environment):
    event = {
        "resource": "/patient/{patient_id}/case/{case_id}",
        "path": "/patient/123/case/123",
        "httpMethod": "GET",
        "pathParameters": {
            "patient_id": "1234"
        },
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 500
    assert "cannot proceed with the request error:"in  lambdaResponse['body']
