# ruff: noqa: E501

query_get_role_by_role_id = """
                query GetRole($role_id: String) {
                  {{schema_name}}roles(where: {role_id: {_eq: $role_id}}) {
                      component_id
                      role_id
                  }
                }
            """

query_get_role_by_component_id = """
                query GetRole($component_id: String) {
                  {{schema_name}}roles(where: {component_id: {_eq: $component_id}}) {
                      component_id
                      role_id
                  }
                }
            """

mutation_upsert_role = """
                mutation InsertRole($component_id: String = "", $role_id: String = "") {
                  insert_{{schema_name}}roles_one(object: {component_id: $component_id, role_id: $role_id}, on_conflict: {constraint: roles_pkey, update_columns: [component_id], where: {component_id: {_eq: $component_id}}}) {
                    component_id
                    role_id
                  }
                }
            """

mutation_upsert_root_field_name_role = """
                mutation UpdateRootFieldNameRole($graphql_root_field_name: String = "", $role_id: String = "") {
                  insert_{{schema_name}}role_graphql_root_field_names(objects: {graphql_root_field_name: $graphql_root_field_name, role_id: $role_id}, on_conflict: {constraint: role_graphql_root_field_names_pkey, update_columns: [graphql_root_field_name], where: {graphql_root_field_name: {_eq: $graphql_root_field_name}}}) {
                    returning {
                      graphql_root_field_name
                    }
                  }
                }
            """

mutation_delete_root_field_name_role = """
                mutation DeleteRootFieldNameRole($graphql_root_field_names: [String!], $role_id: String!) {
                  delete_{{schema_name}}role_graphql_root_field_names(where: {role_id: {_eq: $role_id}, _and: {graphql_root_field_name: {_nin: $graphql_root_field_names}}}) {
                    affected_rows
                  }
                }
            """

mutation_upsert_user_role = """
                mutation UpdateUserRole($user: String = "", $role_id: String = "", $last_update: timestamptz = now) {
                  insert_{{schema_name}}user_roles(objects: {last_update: $last_update, role_id: $role_id, user: $user}, on_conflict: {constraint: user_roles_pkey, update_columns: last_update, where: {}}) {
                    returning {
                      user
                    }
                  }
                }
            """

mutation_delete_user_role = """
                mutation DeleteUserRole($users: [String!], $role_id: String!) {
                  delete_{{schema_name}}user_roles(where: {role_id: {_eq: $role_id}, _and: {user: {_nin: $users}}}) {
                    affected_rows
                  }
                }
            """

mutation_upsert_group_role = """
                mutation UpdateGroupRole($group: String = "", $role_id: String = "", $last_update: timestamptz = now) {
                  insert_{{schema_name}}group_roles(objects: {last_update: $last_update, role_id: $role_id, group: $group}, on_conflict: {constraint: group_roles_pkey, update_columns: last_update, where: {}}) {
                    returning {
                      group
                    }
                  }
                }
            """

mutation_delete_group_role = """
                mutation DeleteGroupRole($groups: [String!], $role_id: String!) {
                  delete_{{schema_name}}group_roles(where: {role_id: {_eq: $role_id}, _and: {group: {_nin: $groups}}}) {
                    affected_rows
                  }
                }
            """

query_get_roles_by_user_and_groups = """
                query GetRolesByUserAndGroups($user: String!, $groups: [String!]) {
                  {{schema_name}}user_roles(where: {user: {_eq: $user}}, distinct_on: role_id) {
                    role_id
                  }
                  {{schema_name}}group_roles(where: {group: {_in: $groups}}, distinct_on: role_id) {
                    role_id
                  }
                }
            """

query_get_role_graphql_root_field_names = """
                query GetRoleGraphqlRootFieldNames($graphql_root_field_names: [String!]) {
                  {{schema_name}}role_graphql_root_field_names(where: {graphql_root_field_name: {_in: $graphql_root_field_names}}) {
                    graphql_root_field_name
                    role_id
                  }
                }
            """
