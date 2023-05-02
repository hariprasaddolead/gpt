Plug methodology
================

This API works with chalice <https://chalice.readthedocs.io/en/latest/>, 
a microservice framework hosted in AWS.

Prerequites
-----------
*   Python3.9+
*   chalice

How to install
--------------
*   git clone
*   create a virtualenv
*   `All commands will now assume that you are in the virtualenv`
*   pip install`-r requirements.txt

How to run
----------
`chalice local` will launch the webservice in local, 
accessible throught http://localhost:8000/

To send a lead -> 
```bash
curl -XPOST http://localhost:8000/send -d '{}'
``` 
where the data payload represents a lead, which will be  described below. 

Project description
-------------------
For those unfamiliar with chalice, the syntax is quite the same as 
The main entry point is `app.py`, with the `send_lead` function. 

### Success return code

| Status | Meaning  | 
|--------|----------|
| 200    | Success  |   
| 201    | Created  | 
| 202    | Accepted | 

### Success return value 
```json
{
 "request_details": {},
 "customer_lead_id": 123,
 "response_details": {"http_status_code": 200, 
                      "payload_key_1": "abc"}
}
```
Where 
*   request_details = the translated lead to the customer (after your inner transformations)
*   response_details is the raw response of the customer, with the HTTP status code of the customer response, if applicable.
*   customer_lead_id is the unique ID of the lead in the customer system, if he provides it in his response. 

### Error return codes

| Status | Meaning                                                                                                        | 
|--------|----------------------------------------------------------------------------------------------------------------|
| 400    | Invalid lead: one of required fields is missing. Please provide missing fields in the response payload.       |   
| 401    | Unauthorized: the API could not connect to the customer system.                                               | 
| 404    | Could not find the customer API.                                                                               |             
| 406    | Not acceptable: the customer refused the lead. Please provide the reason in the response payload              | 
| 409    | Conflict: the lead is a duplicate, it could be sould to another customer                                      | 
| 500    | Internal error, should not happen. It is probably a bug, please look at the logs / rollbar data                |
| 502    | Bad Gateway: The customer system responded with an error. Please provide the error in the response payload    |

Please make sure to NEVER send back a 504 status code. It is a special code used for timeout handling.

### Error return value 
```json
{"request_details": {},
 "error": {},
 "error_message": "An error occured",
 "response_details": {"http_status_code": 400, 
                      "payload_key_1": "abc"}
}
```

How to test
-----------
You have tests fixtures in the `fixtures/leads` directory. 
Each file represents the input data received by the send_lead project.

You have two scripts to send the fixture to the customer, assuming that the chalice server is running in local
```shell script
./scripts/send_fixture_to_customer.py fixtureLeadId
./scripts/send_all_fixtures_to_customer.py
```

NB : if the customer have a deduplication system, please alter the email address/phone in the fixtures after 
each test to avoid hittings duplicate error after the initial call.

Unit testing
------------
When possible (meaning that the customer call can be easily mocked), 
it is recommended to create unit tests for your chalice app. You have an example in the `tests/test_app.py` file.
If not possible, please deactivate the unit tests are they will be launched by the CI after each pull requests.

Configuration
-------------
Any url, login, passkey, etc should be added to the `environment_variables` object in the file `.chalice/config.json`
There is two stages : one for production and one for testing, if the customer supports such a distinction.

You are not allowed to change anything else in this file, especially the hardcoded ids. 
Beware to not remove the two rollbar parameters in the `environment_variables`. Those are the only ReadOnly
keys in this part of the configuration.

How to prepare a release
-----------------------
You won't have the access to the AWS structure to directly deploy 
your code either in production or in staging environment. 

To release your project, you will have to create a new branch `git checkout -b mybranchname`, 
then create a pull request on github, against staging for tests purpose, against master for a production release. 
Once validated, your project will automatically be deployed in the selected environment.
