
CREATE SCHEMA IF NOT EXISTS rolemapping;

CREATE TABLE IF NOT EXISTS rolemapping.roles (
  role_id VARCHAR(255) PRIMARY KEY,
  component_id VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS rolemapping.role_graphql_root_field_names (
  role_id VARCHAR(255) NOT NULL,
  graphql_root_field_name VARCHAR(255) NOT NULL,
  PRIMARY KEY (role_id, graphql_root_field_name),
  FOREIGN KEY (role_id)
      REFERENCES rolemapping.roles (role_id)
);

CREATE TABLE IF NOT EXISTS rolemapping.user_roles (
  "user" VARCHAR(255) NOT NULL,
  role_id VARCHAR(255) NOT NULL,
  last_update TIMESTAMPTZ,
  PRIMARY KEY ("user", role_id),
  FOREIGN KEY (role_id)
      REFERENCES rolemapping.roles (role_id)
);

CREATE TABLE IF NOT EXISTS rolemapping.group_roles (
  "group" VARCHAR(255) NOT NULL,
  role_id VARCHAR(255) NOT NULL,
  last_update TIMESTAMPTZ,
  PRIMARY KEY ("group", role_id),
  FOREIGN KEY (role_id)
      REFERENCES rolemapping.roles (role_id)
);
