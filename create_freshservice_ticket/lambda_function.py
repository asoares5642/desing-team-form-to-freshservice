import json
import requests
import os

API_KEY = os.environ.get('FRESHSERVICE_API_KEY')
FRESHSERVICE_DOMAIN = os.environ.get('FRESHSERVICE_DOMAIN')

def lambda_handler(event, context):

    print(json.dumps(event))
    headers = {
    'Content-Type': 'application/json'
    }
    body = json.loads(event['body'])

    # The freshservice API currently only supports 'type' = 'Incident'
    # We will hardset this value to 'Incident' until the API supports other values
    body['type'] = 'Incident'

    response = requests.post(
        url = 'https://' + FRESHSERVICE_DOMAIN + '/api/v2/tickets', 
        headers = headers,
        auth = (API_KEY, '_'), 
        json = body
        )

    print(response.status_code)
    print(response.text)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }