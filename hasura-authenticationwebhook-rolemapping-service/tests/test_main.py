from fastapi.testclient import TestClient

from src.handlers.webhook_handler import WebhookHandler
from src.jwt.azure_claims_service import AzureClaimsService
from src.jwt.claims_service import ClaimsService
from src.jwt.jwt_service import JWTService
from src.main import app, get_webhook_handler
from tests.jwt.fake_jwt_service import FakeJWTService
from tests.jwt.fake_membership_service import FakeMembershipService

client = TestClient(app)


def get_webhook_handler_for_test() -> WebhookHandler:
    jwt_service: JWTService = FakeJWTService(
        data={"unique_name": "user", "oid": "1234567890"}
    )
    claims_service: ClaimsService = AzureClaimsService(FakeMembershipService(["dev"]))
    return WebhookHandler(claims_service=claims_service, jwt_service=jwt_service)


app.dependency_overrides[get_webhook_handler] = get_webhook_handler_for_test


class TestAuthenticationWebhook:
    def test_authenticate_request_200_ok(self):
        response = client.post(
            "/v1/authenticate",
            json={
                "headers": {"Authorization": "Bearer eyJ0eXAiO"},
                "request": {
                    "query": "query ProductById($id: uuid!) {\n  products_by_pk(id: $id) {\n    id\n    name\n  }\n}",  # noqa: E501
                    "variables": {"id": "cd6be51c-65b6-11ed-a2f4-4b71f0d3d70f"},
                    "operationName": "ProductById",
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "X-Hasura-User-Id": "X_Hasura_User_Id",
            "X-Hasura-Role": "X_Hasura_Role",
        }

    def test_authenticate_request_unauthorized(self):
        response = client.post(
            "/v1/authenticate",
            json={
                "headers": {"Authorization": "Invalid"},
                "request": {
                    "query": "query ProductById($id: uuid!) {\n  products_by_pk(id: $id) {\n    id\n    name\n  }\n}",  # noqa: E501
                    "variables": {"id": "cd6be51c-65b6-11ed-a2f4-4b71f0d3d70f"},
                    "operationName": "ProductById",
                },
            },
        )

        assert response.status_code == 401
