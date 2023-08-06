import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rispack.aws import get_secret


class DatabaseCredentialError(RuntimeError):
    pass


class Database:
    def __init__(
        self,
        user: str = None,
        endpoint: str = None,
        port: int = None,
        name: str = None,
        secret_arn: str = None,
        password: str = None,
    ) -> None:
        self._session = None
        self._engine = None
        self.user = user or os.environ.get("DB_USER")
        self.endpoint = endpoint or os.environ.get("DB_ENDPOINT")
        self.port = port or os.environ.get("DB_PORT", "5432")
        self.name = name or os.environ.get("DB_NAME")
        self.secret_arn = secret_arn or os.environ.get("DB_SECRET_ARN", None)
        self.password = password or os.environ.get("DB_PASSWORD", None)
        self.region = os.environ.get("AWS_REGION")
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.is_development = self.environment == "development"

        if not (self.user and self.endpoint and self.name and self.port):
            raise DatabaseCredentialError("Invalid database credentials.")

        if not self.secret_arn:
            if not self.is_development:
                raise DatabaseCredentialError(
                    "You must provide DB_SECRET_ARN environment variable."
                )

            if not self.password:
                raise DatabaseCredentialError(
                    f"You must provide DB_PASSWORD or DB_SECRET_ARN environment variable."
                )

    @property
    def session(self):
        if self._session:
            return self._session

        self._session = self.create_session()

        return self._session

    def create_session(self):
        session = Session(self._get_engine(), future=True, expire_on_commit=False)

        return session

    def dispose_session(self):
        self.session.close()

        self._session = None

    def get_connection_string(self):
        password = None

        if self.is_development and self.password:
            password = self.password
        else:
            password = self.get_secret_password()

        conn = "postgresql+pg8000://{}:{}@{}:{}/{}".format(
            self.user, password, self.endpoint, self.port, self.name
        )

        return conn

    def get_secret_password(self):
        secret = get_secret(self.secret_arn)

        password = json.loads(secret).get("password")

        return password

    def _get_engine(self):
        if self._engine:
            return self._engine

        self._engine = create_engine(self.get_connection_string())

        return self._engine
