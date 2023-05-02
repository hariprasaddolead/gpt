#!/usr/bin/env python3
# pylint: disable=invalid-name
import json
import sys

import requests


# We are assuming here that the chalice is launched in local : localhost:8000
# Usage: ./scripts/send_fixture_to_customer.py [lead_id]
if __name__ == '__main__':
    lead_id = sys.argv[1]
    print("Will load fixture %s" % lead_id)
    try:
        with open('../fixtures/leads/{}.json'.format(lead_id)) as fixture:
            lead = json.load(fixture)
    except FileNotFoundError:
        with open('./fixtures/leads/{}.json'.format(lead_id)) as fixture:
            lead = json.load(fixture)
    result = requests.post('http://localhost:8000/ping', json=lead)
    print('Status code is', result.status_code)
    print('Result is', result.json())
