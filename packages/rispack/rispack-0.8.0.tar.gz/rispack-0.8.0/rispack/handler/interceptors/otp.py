import os
from http import HTTPStatus

import requests

from rispack.aws import get_signed_auth
from rispack.errors import RispackError
from rispack.handler import Request, Response


class InvalidOtpEndpoint(RispackError):
    pass


# TODO: OTP is the same as PIN with different headers name.
# It shoud be refactored a single class. (TokenInterceptor for example).


class OtpInterceptor:
    SETTINGS = {"header": "X-Authorization-Otp"}

    @classmethod
    def get_param_name(cls):
        return "otp"

    def __init__(self, validate_pin):
        self.validate_pin = validate_pin
        self.endpoint = os.environ.get("OTP_AUTHORIZATION_URL")

        if not self.endpoint:
            raise InvalidOtpEndpoint

    def __call__(self, request: Request):
        id = request.authorizer.get("profile_id")
        otp = request.headers.get(self.SETTINGS["header"])

        if not otp:
            return Response.forbidden(f"Invalid {self.SETTINGS['header']} header")

        payload = {"otp": otp, "profile_id": id}

        response = requests.post(self.endpoint, auth=get_signed_auth(), json=payload)

        if response.status_code != HTTPStatus.OK:
            return Response.forbidden("Invalid OTP")

        return None
