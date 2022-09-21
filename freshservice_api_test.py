import requests
import json

API_KEY = 'NcJm9lH0xxzWZjJT3zq8'
url = 'https://covidclinic.freshservice.com//api/v2/tickets/19'

# Test the API
headers = {
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers, auth=(API_KEY, '_'))
print(response.status_code)
r = json.loads(response.text)

# save r[departments] to a json file
print(r)