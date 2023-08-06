from enum import Enum

from rispack.handler import Request, Response


class RoleInterceptor:
    @classmethod
    def get_param_name(cls):
        return "role"

    def __init__(self, role):
        if isinstance(role, Enum):
            role = role.value

        self.role = role

    def __call__(self, request: Request):
        user_role = request.authorizer.get("role")

        if user_role != self.role:
            return Response.forbidden(f"Authorizer does not have role '{self.role}'.")
