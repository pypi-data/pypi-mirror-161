from functools import wraps

from marshmallow.exceptions import ValidationError

from rispack.errors import NotFoundError
from rispack.logger import logger

from .interceptors import OtpInterceptor, PinInterceptor, RoleInterceptor
from .request import Request
from .response import Response

_INTERCEPTORS = [RoleInterceptor, PinInterceptor, OtpInterceptor]


def add_interceptor(klass):
    _INTERCEPTORS.append(klass)


def route(*args, **kwargs):
    # looking for interceptors params, e.g @route(role="user.creation")
    route_interceptors = _parse_interceptors(kwargs)

    def inner(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                request = Request(event)
                intercepted = False

                for interceptor in route_interceptors:
                    result = interceptor(request)

                    if isinstance(result, Response):
                        intercepted = True
                        break

                if not intercepted:
                    result = func(request)

                if not isinstance(result, Response):
                    result = Response.internal_server_error("Invalid response error")

            except ValidationError as e:
                errors = _get_validation_errors(e.messages)
                result = Response.bad_request(errors)

            except NotFoundError as e:
                error = e.args[0]
                result = Response.not_found(error)

            except Exception as e:
                logger.exception(e)

                result = Response.internal_server_error()

            return result.dump()

        return wrapper

    # args[0] is the function itself when called
    # without parenthesis e.g. @route. This enables
    return inner if route_interceptors else inner(args[0])


def _get_validation_errors(fields):
    errors = []
    for key, value in fields.items():
        errors.append(
            {
                "id": f"invalid_{key}",
                "message": value[0],
                "field": key,
            }
        )
    return errors


def _parse_interceptors(kwargs):
    interceptors = []

    for interceptor in _INTERCEPTORS:
        param = interceptor.get_param_name()
        route_params = kwargs.get(param)

        if route_params:
            interceptors.append(interceptor(route_params))

    return interceptors
