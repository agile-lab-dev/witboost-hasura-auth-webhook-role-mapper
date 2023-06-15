import logging
from typing import Any

import jwt
from jwt import PyJWKClient, PyJWTError
from pydantic import BaseSettings

from src.jwt.jwt_service import JWTService


class JWTConfig(BaseSettings):
    jwks_url: str
    jwt_audience: str | list[str] | None
    jwt_algorithms: list[str] | None
    jwt_options: dict[str, Any] | None


class ConcreteJWTService(JWTService):
    def __init__(self, config: JWTConfig):
        self.config = config
        self.jwks_client: PyJWKClient = PyJWKClient(self.config.jwks_url)
        self.logger = logging.getLogger(__name__)

    def validate(self, token: str) -> None:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            jwt.decode(
                token,
                signing_key.key,
                algorithms=self.config.jwt_algorithms,
                audience=self.config.jwt_audience,
                options=self.config.jwt_options,
            )
        except PyJWTError:
            self.logger.exception("Exception in validate:")
            raise

    def get_payload(self, token: str) -> dict[str, Any]:
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=self.config.jwt_algorithms,
            audience=self.config.jwt_audience,
            options=self.config.jwt_options,
        )
