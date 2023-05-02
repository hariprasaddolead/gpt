import json
from os import environ

import requests_mock

from tests.utils.base_test import BaseTest
from app import MANDATORY_MAPPING_FIELDS, \
    MANDATORY_COMPUTED_FIELDS, translate_lead

from chalicelib.utils import (MissingMandatoryFieldsError,
                              ValueNotMappedError,
                              FieldNotComputedError)


class TestApp(BaseTest):
    LEAD_FIXTURE_ID = 'form_643799610b19d9.81688994'
    LEAD_TRANSLATED_FOR_CLIENT = {
        "Nom_Voie_Adresse_Titulaire": "Place de la République",
        "Numero_Voie_Adresse_Titulaire": "12",
        "Code_Postal_Adresse_Titulaire": "75015",
        "Email_Titulaire": "doleadtest__1373@dolead.com",
        "Nom_Titulaire": "doleadtest",
        "Tel_Mobile_Titulaire": "0623456789",
        "Prenom_Titulaire": "Imad",
        "Ville_Adresse_Titulaire": "Paris",
        "Operateur_Fixe_Prospect ": "Orange",
        "Eligibilite_FTTH_Adresse_Titulaire  ": "box_tres_haut_debit",
        "ID_Traitement": "form_643799610b19d9.81688994",
        "Civilite_Titulaire": "",
        "Complement_Adresse_Titulaire": "",
        "Complement_Adresse_2_Titulaire": ""
    }

    PAMARS_TRANSLATED_FOR_CLIENT = {
        'UserName': environ.get('username'),
        'Password': environ.get('password')}

    def __remove_mapping(self, lead, customer_key):
        dolead_key = None
        print(lead['customer_fields_mapping'])
        for key, value in lead['customer_fields_mapping'].items():
            if value['customer_key'] == customer_key:
                dolead_key = key
        lead['customer_fields_mapping'].pop(dolead_key, None)

    def test_empty_lead_is_ko(self):
        response = self.lg.handle_request(
            method='POST',
            path='/send',
            headers={"Content-Type": "application/json"},
            body='{}'
        )
        assert response['statusCode'] == 400 #  Client responds in case of empty lead like for duplicate lead !
        json_result = json.loads(response['body'])
        assert json_result is not None  # Assert that the result is a real JSON.

    def test_lead_missing_mapping_success(self):
        # Simulate call from dolead
        lead_body = self._load_valid_fixture(self.LEAD_FIXTURE_ID, 't1')

        if not MANDATORY_MAPPING_FIELDS:
            return

        first = list(MANDATORY_MAPPING_FIELDS)[0]
        self.__remove_mapping(lead_body, first)

        # response_for_dolead_core
        response_for_dolead_core = self._send_call(lead_body)
        # Assert response for Dolead is correct
        json_result = json.loads(response_for_dolead_core['body'])
        self.assertEqual(response_for_dolead_core['statusCode'], 400)
        self.assertEqual(json_result,
                         MissingMandatoryFieldsError([first]).error_body)

    def test_lead_computed_values(self):
        lead_body = self._load_valid_fixture(self.LEAD_FIXTURE_ID, 't2')
        translated = translate_lead(lead_body)

        for field in MANDATORY_COMPUTED_FIELDS:
            # To change for nested fields
            self.assertIn(field, translated)

        MANDATORY_COMPUTED_FIELDS.add('Dummy field')
        # response_for_dolead_core
        response_for_dolead_core = self._send_call(json.dumps(lead_body))
        # Assert response for Dolead is correct
        json_result = json.loads(response_for_dolead_core['body'])
        self.assertEqual(response_for_dolead_core['statusCode'], 400)
        self.assertEqual(json_result['error'], 'Mandatory field not computed')
        self.assertIn(
            'Missing mandatory field after translation: Dummy field. Computed lead',
            json_result['error_message']
        )
        # Remove the 'Dummy field' from Global Var 'MANDATORY_COMPUTED_FIELDS'
        MANDATORY_COMPUTED_FIELDS.remove('Dummy field')

    @requests_mock.Mocker()
    def test_get_token_and_send_lead_success(self, mock):
        # CASE OF SUCCESS
        response_token_from_customer_json = {
            "Token": "12345"}
        response_code_from_customer_for_token = 200
        response_from_customer_json = {"Message": "OK",
                                       "Records": [{"ID_Traitement": "form_643799610b19d9.81688994"}]}
        response_code_from_customer = 200

        # Describe the API conversation with customer
        self._mock_token_request_and_response(
            mock, response_token_from_customer_json, response_code_from_customer_for_token)

        self._mock_request_and_response(
            mock, response_from_customer_json, response_code_from_customer)

        # Simulate call from dolead
        lead_body = self._load_valid_fixture(self.LEAD_FIXTURE_ID, 't3')
        # Update lead_id value in the lead
        self.LEAD_TRANSLATED_FOR_CLIENT['ID_Traitement'] = 't3'
        # response_for_dolead_core
        response_for_dolead_core = self._send_call(lead_body)
        # Assert response for Dolead is correct
        json_result = json.loads(response_for_dolead_core['body'])
        assert response_for_dolead_core['statusCode'] == 200
        assert json_result['request_details']['json'] == self.LEAD_TRANSLATED_FOR_CLIENT
        assert json_result['request_details']['headers']['Token'] == "12345"

    @requests_mock.Mocker()
    def test_normal_lead_get_token_unauthorized(self, mock):
        # CASE OF FAILURE : Authentication problem
        response_token_from_customer_json = ''
        response_code_from_customer_for_token = 401
        response_from_customer_json = ''
        response_code_from_customer = 401

        # Describe the API conversation with customer
        self._mock_token_request_and_response(
            mock, response_token_from_customer_json, response_code_from_customer_for_token)

        self._mock_request_and_response(
            mock, response_from_customer_json, response_code_from_customer)

        # Simulate call from dolead
        lead_body = self._load_valid_fixture(self.LEAD_FIXTURE_ID, 't4')
        # Update lead_id value in the lead
        self.LEAD_TRANSLATED_FOR_CLIENT['ID_Traitement'] = 't4'
        # response_for_dolead_core
        response_for_dolead_core = self._send_call(lead_body)
        # Assert response for Dolead is correct
        assert response_for_dolead_core['statusCode'] == 401


    @requests_mock.Mocker()
    def test_get_token_success_lead_duplicated_error(self, mock):
        # CASE OF FAILURE : Duplicate lead
        response_token_from_customer_json = {
            "Token": "12345"}
        response_code_from_customer_for_token = 200
        response_from_customer_json = {"Message": "Client record duplicate",
                                       "Records": [{"ID_Traitement": "form_643799610b19d9.81688994"}]}
        response_code_from_customer = 400

        # Describe the API conversation with customer
        self._mock_token_request_and_response(
            mock, response_token_from_customer_json, response_code_from_customer_for_token)

        self._mock_request_and_response(
            mock, response_from_customer_json, response_code_from_customer)

        # Simulate call from dolead
        lead_body = self._load_valid_fixture(self.LEAD_FIXTURE_ID, 't6')
        # Update lead_id value in the lead
        self.LEAD_TRANSLATED_FOR_CLIENT['ID_Traitement'] = 't6'
        # response_for_dolead_core
        response_for_dolead_core = self._send_call(lead_body)
        # Assert response for Dolead is correct
        json_result = json.loads(response_for_dolead_core['body'])
        assert response_for_dolead_core['statusCode'] == 409
        assert json_result['request_details']['headers']['Token'] == "12345"


    def _mock_request_and_response(self, mock, response_json, response_code):
        # README:
        # https://requests-mock.readthedocs.io/en/latest/response.html
        # https://requests-mock.readthedocs.io/en/latest/matching.html#request-headers

        # This is the REQUEST
        def _match_request_body(request):
            # 2. REQUEST to CUSTOMER API
            body_is_correct = request.json() == self.LEAD_TRANSLATED_FOR_CLIENT
            return body_is_correct

        # Mock the call with the REQUEST and the RESPONSE
        mock.post(
            # MATCH
            environ.get('customer_api_url').format('ClientRecords'),
            additional_matcher=_match_request_body,
            json=response_json,
            status_code=response_code
        )

    def _mock_token_request_and_response(self, mock, response_json, response_code):
        # This is the REQUEST
        def _match_request_body(request):
            # 2. REQUEST to CUSTOMER API
            body_is_correct = request.json() == self.PAMARS_TRANSLATED_FOR_CLIENT
            return body_is_correct

        mock.post(
            environ.get('customer_api_url').format('Authenticate'),
            # 3. RESPONSE from CUSTOMER API
            # Return response
            json=response_json,
            status_code=response_code
        )
