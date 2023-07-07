from fastapi.testclient import TestClient

from src.handlers.webhook_handler import WebhookConfig, WebhookHandler
from src.jwt.azure_claims_service import AzureClaimsService
from src.jwt.claims_service import ClaimsService
from src.jwt.jwt_service import JWTService
from src.main import app, get_roles_repository, get_webhook_handler
from src.models import (
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Role,
    RoleGraphqlRootFieldName,
    UserRoleMappings,
)
from src.repositories.roles_repository import RoleRepository
from tests.jwt.fake_jwt_service import FakeJWTService
from tests.jwt.fake_membership_service import FakeMembershipService
from tests.repositories.fake_roles_repository import (
    FakeRoleRoleRepository,
    FakeRoleRoleRepositoryRaisingGenericError,
    FakeRoleRoleRepositoryRaisingHandledError,
)

client = TestClient(app)


def get_webhook_handler_for_test() -> WebhookHandler:
    jwt_service: JWTService = FakeJWTService(
        data={"unique_name": "user", "oid": "1234567890"}
    )
    claims_service: ClaimsService = AzureClaimsService(FakeMembershipService(["dev"]))
    return WebhookHandler(
        claims_service=claims_service,
        jwt_service=jwt_service,
        role_repository=get_role_repository_for_test(),
        webhook_config=WebhookConfig(
            authorization_header_field_names=["authorization"]
        ),
    )


app.dependency_overrides[get_webhook_handler] = get_webhook_handler_for_test


def get_role_repository_for_test() -> RoleRepository:
    role = Role(
        role_id="role_id",
        component_id="component_id",
    )
    user_role = UserRoleMappings(role_id="role_id", users=["user:user1"])
    group_role = GroupRoleMappings(role_id="role_id", groups=["group:group1"])
    root_field_name_role = GraphqlRootFieldNameRoleMappings(
        role_id="role_id",
        component_id="component_id",
        graphql_root_field_names=["graphql_root_field_name1"],
    )
    role_root = RoleGraphqlRootFieldName(
        role_id="role_id", graphql_root_field_name="graphql_root_field_name1"
    )
    return FakeRoleRoleRepository(
        role=role,
        user_role=user_role,
        group_role=group_role,
        root_field_name_role=root_field_name_role,
        role_graphql_root_field_names=[role_root],
        roles_by_user_and_groups=["role_id"],
    )


def get_role_repository_for_test_raising_handled_error() -> RoleRepository:
    return FakeRoleRoleRepositoryRaisingHandledError()


def get_role_repository_for_test_raising_generic_error() -> RoleRepository:
    return FakeRoleRoleRepositoryRaisingGenericError()


class TestAuthenticationWebhook:
    def test_authenticate_request_200_ok(self):
        response = client.post(
            "/v1/authenticate",
            json={
                "headers": {"authorization": "Bearer eyJ0eXAiO"},
                "request": {
                    "query": "query ProductById($id: uuid!) { graphql_root_field_name1(id: $id) { id name }}",  # noqa: E501
                    "variables": {"id": "cd6be51c-65b6-11ed-a2f4-4b71f0d3d70f"},
                    "operationName": "ProductById",
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "X-Hasura-User-Id": "user:user",
            "X-Hasura-Role": "role_id",
        }

    def test_authenticate_request_unauthorized(self):
        response = client.post(
            "/v1/authenticate",
            json={
                "headers": {"authorization": "Invalid"},
                "request": {
                    "query": "query ProductById($id: uuid!) {\n  products_by_pk(id: $id) {\n    id\n    name\n  }\n}",  # noqa: E501
                    "variables": {"id": "cd6be51c-65b6-11ed-a2f4-4b71f0d3d70f"},
                    "operationName": "ProductById",
                },
            },
        )

        assert response.status_code == 401

    def test_authenticate_request_400_query_not_valid(self):
        response = client.post(
            "/v1/authenticate",
            json={
                "headers": {"authorization": "Bearer eyJ0eXAiO"},
                "request": {
                    "query": "query_not_valid ProductById($id: uuid!) { graphql_root_field_name1(id: $id) { id name }}",  # noqa: E501
                    "variables": {"id": "cd6be51c-65b6-11ed-a2f4-4b71f0d3d70f"},
                    "operationName": "ProductById",
                },
            },
        )

        assert response.status_code == 400


class TestRoleMapper:
    def test_get_role_by_id_200_ok(self):
        app.dependency_overrides[get_roles_repository] = get_role_repository_for_test

        response = client.get("/v1/roles/role_id")

        assert response.status_code == 200
        assert response.json() == {
            "role_id": "role_id",
            "component_id": "component_id",
        }

    def test_get_role_by_id_404(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_handled_error

        response = client.get("/v1/roles/role_id")

        assert response.status_code == 404

    def test_get_role_by_id_500(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_generic_error

        response = client.get("/v1/roles/role_id")

        assert response.status_code == 500

    def test_get_role_by_component_id_200_ok(self):
        app.dependency_overrides[get_roles_repository] = get_role_repository_for_test

        response = client.get("/v1/roles/component_id/component_id")

        assert response.status_code == 200
        assert response.json() == {
            "role_id": "role_id",
            "component_id": "component_id",
        }

    def test_get_role_by_component_id_404(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_handled_error

        response = client.get("/v1/roles/component_id/component_id")

        assert response.status_code == 404

    def test_get_role_by_component_id_500(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_generic_error

        response = client.get("/v1/roles/component_id/component_id")

        assert response.status_code == 500

    def test_upsert_role_200_ok(self):
        app.dependency_overrides[get_roles_repository] = get_role_repository_for_test

        response = client.put(
            "/v1/roles",
            json={
                "role_id": "role_id",
                "component_id": "component_id",
                "graphql_root_field_names": ["graphql_root_field_name1"],
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "role_id": "role_id",
            "component_id": "component_id",
            "graphql_root_field_names": ["graphql_root_field_name1"],
        }

    def test_upsert_role_400(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_handled_error

        response = client.put(
            "/v1/roles",
            json={
                "role_id": "role_id",
                "component_id": "component_id",
                "graphql_root_field_names": ["graphql_root_field_name1"],
            },
        )

        assert response.status_code == 400

    def test_upsert_role_500(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_generic_error

        response = client.put(
            "/v1/roles",
            json={
                "role_id": "role_id",
                "component_id": "component_id",
                "graphql_root_field_names": ["graphql_root_field_name1"],
            },
        )

        assert response.status_code == 500

    def test_upsert_user_roles_200_ok(self):
        app.dependency_overrides[get_roles_repository] = get_role_repository_for_test

        response = client.put(
            "/v1/user_roles",
            json={"role_id": "role_id", "users": ["user:user1"]},
        )

        assert response.status_code == 200
        assert response.json() == {"role_id": "role_id", "users": ["user:user1"]}

    def test_upsert_user_roles_400(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_handled_error

        response = client.put(
            "/v1/user_roles",
            json={"role_id": "role_id", "users": ["user:user1"]},
        )

        assert response.status_code == 400

    def test_upsert_user_roles_500(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_generic_error

        response = client.put(
            "/v1/user_roles",
            json={"role_id": "role_id", "users": ["user:user1"]},
        )

        assert response.status_code == 500

    def test_upsert_group_roles_200_ok(self):
        app.dependency_overrides[get_roles_repository] = get_role_repository_for_test

        response = client.put(
            "/v1/group_roles",
            json={"role_id": "role_id", "groups": ["group:group1"]},
        )

        assert response.status_code == 200
        assert response.json() == {"role_id": "role_id", "groups": ["group:group1"]}

    def test_upsert_group_roles_400(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_handled_error

        response = client.put(
            "/v1/group_roles",
            json={"role_id": "role_id", "groups": ["group:group1"]},
        )

        assert response.status_code == 400

    def test_upsert_group_roles_500(self):
        app.dependency_overrides[
            get_roles_repository
        ] = get_role_repository_for_test_raising_generic_error

        response = client.put(
            "/v1/group_roles",
            json={"role_id": "role_id", "groups": ["group:group1"]},
        )

        assert response.status_code == 500
