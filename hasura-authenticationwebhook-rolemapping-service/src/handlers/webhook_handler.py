import logging

from src.jwt.claims_service import ClaimsService
from src.jwt.jwt_service import JWTService
from src.models import AuthenticationRequest, AuthenticationResponse


class WebhookHandlerUnauthorizedException(Exception):
    pass


class WebhookHandler:
    def __init__(self, claims_service: ClaimsService, jwt_service: JWTService):
        self.claims_service = claims_service
        self.jwt_service = jwt_service
        self.PREFIX = "Bearer"
        self.logger = logging.getLogger(__name__)

    def get_token(self, authorization_header: str) -> str:
        """Extracts the JWT token from Authorization Header string

        Args:
            authorization_header: Authorization Header containing bearer token

        Returns:
            The JWT token

        Raises:
            ValueError: if the Authorization Header is not valid
        """
        bearer, _, token = authorization_header.partition(" ")
        if bearer != self.PREFIX:
            self.logger.error(f"Invalid Authorization Header: {authorization_header}")
            raise ValueError("Invalid Authorization Header")
        return token

    async def authenticate_request(
        self, authentication_request: AuthenticationRequest
    ) -> AuthenticationResponse:
        """Authenticates a request

        Args:
            authentication_request: Authentication request sent by Hasura about a client

        Returns:
            Authentication response with the X-Hasura-* variables

        Raises:
            WebhookHandlerUnauthorizedException: if the user is not authorized
        """
        try:
            token = self.get_token(authentication_request.headers.Authorization)
            self.jwt_service.validate(token)
            payload = self.jwt_service.get_payload(token)
            await self.claims_service.get_user(payload)
            await self.claims_service.get_groups(payload)
        except Exception:
            self.logger.exception("Exception in authenticate_request")
            raise WebhookHandlerUnauthorizedException()
        else:
            # TODO role mapper business logic
            return AuthenticationResponse(
                X_Hasura_User_Id="X_Hasura_User_Id", X_Hasura_Role="X_Hasura_Role"
            )
