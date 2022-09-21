import json
from lambda_function import lambda_handler

# Load the test data
with open('test_event.json') as f:
    event = json.load(f)

if __name__ == '__main__':
    lambda_handler(event, None)