import json

from chalice import Response


class MissingMandatoryFieldsError(ValueError):

    def __init__(self, missing_fields):
        self.missing_fields = set(missing_fields)

    @property
    def error_body(self):
        return {
            "error": "Missing mandatory field",
            "error_message": f"Missing mandatory fields "
                             f"in customer field mapping: "
                             f"{self.missing_fields}",
        }


class ValueNotMappedError(ValueError):

    def __init__(self, field, value, allowed_values):
        self.field = field
        self.value = value
        self.allowed_values = sorted(list(allowed_values))

    @property
    def error_body(self):
        return {
            "error": "Invalid value",
            "error_message":
                f"Field {self.field}: value {self.value} not in "
                f"allowed values: {self.allowed_values}"
        }


class FieldNotComputedError(ValueError):

    def __init__(self, field, lead):
        self.field = field
        self.lead = lead

    @property
    def error_body(self):
        return {
            "error": "Mandatory field not computed",
            "error_message": f"Missing mandatory "
                             f"field after translation: {self.field}. "
                             f"Computed lead is {self.lead}"
        }


def build_response(body, status_code=200):
    return Response(
        body=json.dumps(body),
        status_code=status_code,
        headers={'Content-Type': 'application/json'}
    )