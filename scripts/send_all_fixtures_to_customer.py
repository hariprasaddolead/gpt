#!/usr/bin/env python3
# pylint: disable=invalid-name
import json
import os

import requests

# We are assuming here that the chalice is launched in local : localhost:8000

# Usage: ./script/send_fixture_to_customer.py [lead_id]

FIXTURE_DIR = '../fixtures/leads/'
if not os.path.exists(FIXTURE_DIR):
    FIXTURE_DIR = './fixtures/leads/'

if __name__ == '__main__':
    print("Will load all fixtures")
    for filename in os.listdir(FIXTURE_DIR):
        if not filename.endswith('.json'):
            continue
        print('Sending fixture', filename)
        fixture_file = os.path.join(FIXTURE_DIR, filename)
        with open(fixture_file) as fixture:
            lead = json.load(fixture)
        result = requests.post('http://localhost:8000/send', json=lead)
        print('Status code is', result.status_code)
        print('Result is', result.json())
        input("Press Enter to continue...")
