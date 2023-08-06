import json
from dataclasses import dataclass
from typing import Any, Dict, Union


@dataclass
class Request:
    event: Dict[str, Any]
    authorizer: Dict[str, Any] = None
    body: Union[Dict[str, Any], str] = None
    path_params: Dict[str, Any] = None
    query_params: Dict[str, Any] = None
    headers: Dict[str, str] = None
    identity: Dict[str, Any] = None
    source_ip: str = None
    user_agent: str = None

    def __post_init__(self):
        self.authorizer = self._load_auth()
        self.body = self._load_body()
        self.path_params = self._load_path()
        self.query_params = self._load_query()
        self.headers = self._load_headers()
        self.identity = self._load_identity()
        self.params = self._load_params()

    def _load_auth(self):
        context = self.event.get("requestContext") or {}
        authorizer = context.get("authorizer") or None

        return authorizer

    def _load_body(self):
        body = self.event.get("body") or ""

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    def _load_path(self):
        path = self.event.get("pathParameters") or {}
        return path

    def _load_query(self):
        query = self.event.get("queryStringParameters") or {}
        return query

    def _load_headers(self):
        headers = self.event.get("headers") or {}
        return headers

    def _load_identity(self):
        context = self.event.get("requestContext") or {}
        identity = context.get("identity") or {}

        if identity.get("sourceIp"):
            self.source_ip = identity.get("sourceIp")

        if identity.get("userAgent"):
            self.user_agent = identity.get("userAgent")

        return identity

    def _load_params(self):
        return {**self.query_params, **self.path_params}
