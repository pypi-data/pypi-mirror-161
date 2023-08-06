import os
from http import HTTPStatus

import requests

from rispack.aws import get_signed_auth
from rispack.errors import RispackError
from rispack.handler import Request, Response


class InvalidPinEndpoint(RispackError):
    pass


class PinInterceptor:
    SETTINGS = {"header": "X-Authorization-Pin", "iam": True}

    @classmethod
    def get_param_name(cls):
        return "pin"

    def __init__(self, validate_pin):
        self.validate_pin = validate_pin
        self.endpoint = os.environ.get("PIN_AUTHORIZATION_URL")

        if not self.endpoint:
            raise InvalidPinEndpoint

    def __call__(self, request: Request):
        id = request.authorizer.get("profile_id")
        pin = request.headers.get(self.SETTINGS["header"])

        if not pin:
            return Response.forbidden(f"Invalid {self.SETTINGS['header']} header")

        payload = {"pin": pin, "profile_id": id}

        response = requests.post(self.endpoint, auth=get_signed_auth(), json=payload)

        if response.status_code != HTTPStatus.OK:
            return Response.forbidden("Invalid PIN")

        return None
