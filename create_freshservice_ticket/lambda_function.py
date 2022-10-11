import json
import requests
import os
import boto3
import io
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FRESHSERVICE_API_KEY_SECRET_NAME = os.environ.get('FRESHSERVICE_API_KEY_SECRET_NAME')
FRESHSERVICE_DOMAIN = os.environ.get('FRESHSERVICE_DOMAIN')
SVC_INFO_SECRET_NAME = os.environ.get('SVC_INFO_SECRET_NAME')

def lambda_handler(event, context):

    print(json.dumps(event))
    body = json.loads(event['body'])

    # The freshservice API currently only supports 'type' = 'Incident'
    # We will hardset this value to 'Incident' until the API supports other values
    body['type'] = 'Incident'

    # Identify tags based on keywords in the description
    new_tags = identify_tags(body['description'])
    if body.get('tags'):
        body['tags'].extend(new_tags)
    else:
        body['tags'] = new_tags

    # Generate the url for ticket creation API
    print(FRESHSERVICE_API_KEY_SECRET_NAME)
    API_KEY = get_secret_value(FRESHSERVICE_API_KEY_SECRET_NAME)
    url = f'https://{FRESHSERVICE_DOMAIN}/api/v2/tickets'

    # Check if there are any attachments
    if body.get('attachments'):
        # If there are attchaments, the resquest will be a multipart/form-data request

        # Prepare the multipart payload
        attachments = body['attachments']
        del body['attachments']

        # Build the Google drive client
        secret = get_secret_value(SVC_INFO_SECRET_NAME)
        secret = json.loads(secret)
        credentials = service_account.Credentials.from_service_account_info(secret)
        service = build('drive', 'v3', credentials=credentials)

        # Download and add the attachments to the payload
        files = list()
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
            
            # Attach the file
            files.append(('attachments[]', (file_metadata['name'], fh.getbuffer(), file_metadata['mimeType'])))
        
        # Pop the tags from the payload
        tags = body['tags']
        print(tags)
        del body['tags']

        # Add the tags to the files payload
        files.extend([
            ('tags[]', (None, tag)) for tag in tags
        ])
        
        response = requests.post(url, auth=(API_KEY, '_'), data=body, files=files)
        print(response.status_code)
        print(response.text)
        
    else:
        # In case of no attachments, will be used as a regular JSON request
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.post(
            url = url,
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

def get_secret_value(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    return get_secret_value['SecretString']

def identify_tags(text):
    
    # Creates tags for the card based on keywords in the description
    tags = list()

    # lower the text
    text = text.lower()
    keywords = [
        'video', 'digital presentation', 'physical presentation', 'brochure', 'business'
        ]
    for keyword in keywords:
        if keyword in text:
            tags.append(keyword.replace(' ', '-'))
    return tags