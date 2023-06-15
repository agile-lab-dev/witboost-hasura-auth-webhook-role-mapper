import pytest

from src.handlers.webhook_handler import (
    WebhookHandler,
    WebhookHandlerUnauthorizedException,
)
from src.jwt.azure_claims_service import AzureClaimsService
from src.jwt.claims_service import ClaimsService
from src.models import AuthenticationRequest, Headers, Request
from tests.jwt.fake_jwt_service import FakeJWTService
from tests.jwt.fake_membership_service import FakeMembershipService


class TestWebhookHandler:
    authorization_header = "Bearer eyJ0eXAiO"
    token = "eyJ0eXAiO"
    jwt_service = FakeJWTService(data={"unique_name": "user", "oid": "1234567890"})
    claims_service: ClaimsService = AzureClaimsService(FakeMembershipService(["dev"]))
    webhook_handler = WebhookHandler(
        claims_service=claims_service, jwt_service=jwt_service
    )

    def test_get_token_fail_on_invalid_header(self):
        with pytest.raises(ValueError):
            self.webhook_handler.get_token("Invalid token")

    def test_get_token_ok(self):
        token = self.webhook_handler.get_token(self.authorization_header)

        assert token == self.token

    @pytest.mark.asyncio
    async def test_authenticate_request_fail_on_invalid_token(self):
        auth_request = AuthenticationRequest(
            headers=Headers(Authorization=""), request=Request(query="")
        )

        with pytest.raises(WebhookHandlerUnauthorizedException):
            await self.webhook_handler.authenticate_request(auth_request)

    @pytest.mark.asyncio
    async def test_authenticate_request_ok(self):
        auth_request = AuthenticationRequest(
            headers=Headers(Authorization=self.authorization_header),
            request=Request(query=""),
        )

        res = await self.webhook_handler.authenticate_request(auth_request)

        assert res.X_Hasura_User_Id == "X_Hasura_User_Id"
        assert res.X_Hasura_Role == "X_Hasura_Role"
