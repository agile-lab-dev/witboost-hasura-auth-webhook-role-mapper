# generated by fastapi-codegen:
#   filename:  hasura-authenticationwebhook-rolemapping-service/openapi-specification.yml  # noqa: E501
#   timestamp: 2023-06-08T08:32:00+00:00

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Request(BaseModel):
    query: str = Field(
        ...,
        description="JSON-stringified GraphQL query",
        example="query ProductById($id: uuid!) {\n  products_by_pk(id: $id) {\n    id\n    name\n  }\n}",  # noqa: E501
    )
    variables: Optional[Dict[str, Any]] = Field(
        None,
        description="Variable values for the GraphQL query",
        example={"id": "cd6be51c-65b6-11ed-a2f4-4b71f0d3d70f"},
    )
    operationName: Optional[str] = Field(
        None, description="Name of the operation", example="ProductById"
    )


class AuthenticationRequest(BaseModel):
    headers: Dict[str, str]
    request: Request


class AuthenticationResponse(BaseModel):
    X_Hasura_User_Id: str = Field(
        ..., alias="X-Hasura-User-Id", description="User identifier", example="username"
    )
    X_Hasura_Role: str = Field(
        ..., alias="X-Hasura-Role", description="User role", example="role1"
    )

    class Config:
        allow_population_by_field_name = True


class Role(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    component_id: str = Field(
        ..., description="Component id in Witboost", example="urn:dmb:cmp:dom1:dp1:0:op"
    )


class UserRoleMappings(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    users: List[str] = Field(
        ..., description="User list", example=["user:user1", "user:user2"]
    )


class GroupRoleMappings(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    groups: List[str] = Field(
        ..., description="Group list", example=["group:group1", "group:group2"]
    )


class GraphqlRootFieldNameRoleMappings(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    component_id: str = Field(
        ..., description="Component id in Witboost", example="urn:dmb:cmp:dom1:dp1:0:op"
    )
    graphql_root_field_names: List[str] = Field(
        ...,
        description="Root field name list",
        example=["dom1_dp1_0_op1_select", "dom1_dp1_0_op1_aggregate"],
    )


class RoleGraphqlRootFieldName(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    graphql_root_field_name: str = Field(
        ..., description="Root field name", example="dom1_dp1_0_op"
    )


class ValidationError(BaseModel):
    errors: List[str]


class SystemError(BaseModel):
    error: str
