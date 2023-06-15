from azure.identity import ClientSecretCredential
from kiota_authentication_azure.azure_identity_authentication_provider import (  # type: ignore # noqa: E501
    AzureIdentityAuthenticationProvider,
)
from msgraph import GraphRequestAdapter, GraphServiceClient  # type: ignore
from pydantic import BaseSettings

from src.jwt.membership_service import MembershipService


class AzureConfig(BaseSettings):
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str
    azure_scopes: list[str]


class AzureMembershipService(MembershipService):
    def __init__(self, config: AzureConfig):
        self.config = config
        self.credential = ClientSecretCredential(
            tenant_id=self.config.azure_tenant_id,
            client_id=self.config.azure_client_id,
            client_secret=self.config.azure_client_secret,
        )
        self.auth_provider = AzureIdentityAuthenticationProvider(
            self.credential, scopes=self.config.azure_scopes
        )
        self.request_adapter = GraphRequestAdapter(self.auth_provider)
        self.client = GraphServiceClient(self.request_adapter)

    async def get_memberships(self, user_id: str) -> list[str]:
        memberships = await self.client.users.by_user_id(
            user_id
        ).transitive_member_of.get()
        groups: list[str] = []
        if memberships and memberships.value:
            for membership in memberships.value:
                if membership.odata_type == "#microsoft.graph.group":
                    groups.append(membership.display_name)
        return groups
