import json
import requests
import os
import boto3
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FRESHSERVICE_API_KEY_SECRET_NAME = os.environ.get('FRESHSERVICE_API_KEY_SECRET_NAME')
FRESHSERVICE_DOMAIN = os.environ.get('FRESHSERVICE_DOMAIN')
SVC_INFO_SECRET_NAME = os.environ.get('SVC_INFO_SECRET_NAME')

def lambda_handler(event, context):

    print(json.dumps(event))
    headers = {
    'Content-Type': 'multipart/form-data',
    }
    body = json.loads(event['body'])

    # The freshservice API currently only supports 'type' = 'Incident'
    # We will hardset this value to 'Incident' until the API supports other values
    body['type'] = 'Incident'

    # Prepare the attachments, if any
    files = None
    if body.get('attachments'):

        # Pop the attachments from the body
        attachments = body['attachments']
        del body['attachments']

        # Prepare the multipart data
        multipart_data = dict()
        for key in body:
            multipart_data_key = key

        print(attachments)

        # The attachments are list of Google Drive file IDs
        # We need to download the files and add them in a multipart/form-data request

        # Credentiate the service account
        secret = get_secret_value(SVC_INFO_SECRET_NAME)
        secret = json.loads(secret)
        credentials = service_account.Credentials.from_service_account_info(secret)

        # Build the service
        service = build('drive', 'v3', credentials=credentials)

        # Download the files
        files = {'attachments[]': []}
        for attachment in attachments:
                
            print(attachment)
            # Get the file name and mime type
            file_metadata = service.files().get(fileId=attachment, fields='name, mimeType').execute()
            print(file_metadata)


            # Get the file content
            request = service.files().get_media(fileId=attachment)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
            
            # Save to tmp folder
            path = f"tmp/{file_metadata['name']}"
            with open(path, 'wb') as tmpfile:
                tmpfile.write(fh.getbuffer())
            
            # Attach the file
            body['attachments[]'] = open(path, 'rb')

    # Delete tags for now
    del body['tags']
    url = f'https://{FRESHSERVICE_DOMAIN}/api/v2/tickets'
    secret = get_secret_value(FRESHSERVICE_API_KEY_SECRET_NAME)
    print(url)
    response = requests.post(
        url = url,
        headers = headers,
        auth = (secret, '_'), 
        data = body
    )
    
    print(response.status_code)
    print(response.text)


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def get_secret_value(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    return get_secret_value_response['SecretString']