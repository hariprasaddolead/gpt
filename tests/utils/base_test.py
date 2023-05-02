import json
import os
from unittest import TestCase

from chalice.config import Config
from chalice.local import LocalGateway

from app import app


class BaseTest(TestCase):

    def setUp(self):
        self.lg = LocalGateway(app, Config())
        self._load_chalice_env_variables()

    @staticmethod
    def _load_chalice_env_variables():
        stage = 'test'

        with open('.chalice/config.json') as f:
            config = json.load(f)

        env_variables = config['stages'][stage]["environment_variables"]
        for k, v in env_variables.items():
            os.environ[k] = v

    @staticmethod
    def _load_valid_fixture_str(lead_id):
        with open('./fixtures/leads/{}.json'.format(lead_id)) as fixture:
            return fixture.read()

    @classmethod
    def _load_valid_fixture(cls, lead_id, override_lead_id=None):
        lead = json.loads(cls._load_valid_fixture_str(lead_id))
        if override_lead_id:
            lead['lead_id'] = override_lead_id
        return lead

    @staticmethod
    def _load_invalid_fixture():
        # No lead_id
        return {"clearly_an_error": "Please crash"}

    def _send_call(self, body='{}'):
        # 1. REQUEST to Chalice Plug (from DOLEAD Core)
        # Simulate Dolead's call
        if isinstance(body, dict):
            body = json.dumps(body)
        return self.lg.handle_request(
            method='POST',
            path='/send',
            headers={"Content-Type": "application/json"},
            body=body
        )
