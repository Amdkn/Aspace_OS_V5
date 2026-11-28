-- Tenant-owned workspace and structure installation lifecycle.
-- Global blueprint tables remain immutable reference catalogs; this migration creates
-- organization-scoped instances only when an authenticated operator requests installation.
BEGIN;

CREATE TABLE enterprise.workspaces (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  workspace_key text NOT NULL CHECK (workspace_key ~ '^[a-z0-9][a-z0-9._-]{1,95}$'),
  name text NOT NULL CHECK (length(btrim(name)) > 0),
  description text NOT NULL DEFAULT '',
  workspace_status text NOT NULL DEFAULT 'ACTIVE' CHECK (workspace_status IN ('ACTIVE','SUSPENDED','ARCHIVED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, workspace_key),
  UNIQUE (id, organization_id)
);
CREATE INDEX workspaces_org_status_idx ON enterprise.workspaces (organization_id, workspace_status, created_at);

CREATE TABLE areas.domain_installations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  domain_code text NOT NULL REFERENCES areas.domain_blueprints(domain_code) ON DELETE RESTRICT,
  parent_installation_id uuid,
  owner_user_id uuid REFERENCES auth.users(id) ON DELETE RESTRICT,
  installation_status text NOT NULL DEFAULT 'ACTIVE' CHECK (installation_status IN ('DRAFT','ACTIVE','SUSPENDED','ARCHIVED')),
  installed_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  installed_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  FOREIGN KEY (parent_installation_id, workspace_id, organization_id)
    REFERENCES areas.domain_installations(id, workspace_id, organization_id) ON DELETE RESTRICT,
  UNIQUE (id, workspace_id, organization_id),
  UNIQUE (workspace_id, domain_code)
);
CREATE INDEX domain_installations_org_idx ON areas.domain_installations (organization_id, workspace_id, installation_status);
CREATE INDEX domain_installations_parent_idx ON areas.domain_installations (parent_installation_id) WHERE parent_installation_id IS NOT NULL;

CREATE TABLE enterprise.department_installations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  department_key text NOT NULL REFERENCES enterprise.department_blueprints(department_key) ON DELETE RESTRICT,
  owner_user_id uuid REFERENCES auth.users(id) ON DELETE RESTRICT,
  installation_status text NOT NULL DEFAULT 'ACTIVE' CHECK (installation_status IN ('DRAFT','ACTIVE','SUSPENDED','ARCHIVED')),
  installed_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  installed_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  UNIQUE (id, workspace_id, organization_id),
  UNIQUE (workspace_id, department_key)
);
CREATE INDEX department_installations_org_idx ON enterprise.department_installations (organization_id, workspace_id, installation_status);

CREATE TABLE areas.holon_installations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  domain_installation_id uuid NOT NULL,
  holon_code text NOT NULL REFERENCES areas.holon_blueprints(holon_code) ON DELETE RESTRICT,
  parent_installation_id uuid,
  owner_user_id uuid REFERENCES auth.users(id) ON DELETE RESTRICT,
  installation_status text NOT NULL DEFAULT 'ACTIVE' CHECK (installation_status IN ('DRAFT','ACTIVE','SUSPENDED','ARCHIVED')),
  installed_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  installed_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  FOREIGN KEY (domain_installation_id, workspace_id, organization_id)
    REFERENCES areas.domain_installations(id, workspace_id, organization_id) ON DELETE RESTRICT,
  FOREIGN KEY (parent_installation_id, workspace_id, organization_id)
    REFERENCES areas.holon_installations(id, workspace_id, organization_id) ON DELETE RESTRICT,
  UNIQUE (id, workspace_id, organization_id),
  UNIQUE (domain_installation_id, holon_code)
);
CREATE INDEX holon_installations_workspace_idx ON areas.holon_installations (organization_id, workspace_id, installation_status);

CREATE TABLE enterprise.structure_installation_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 8 AND 200),
  request_payload jsonb NOT NULL,
  result_payload jsonb NOT NULL,
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  UNIQUE (workspace_id, idempotency_key)
);
CREATE INDEX structure_installation_requests_org_idx
  ON enterprise.structure_installation_requests (organization_id, workspace_id, created_at DESC);

CREATE TABLE enterprise.structure_installation_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  request_id uuid REFERENCES enterprise.structure_installation_requests(id) ON DELETE RESTRICT,
  event_type text NOT NULL CHECK (event_type IN ('WORKSPACE_CREATED','DOMAIN_INSTALLED','DEPARTMENT_INSTALLED','HOLON_INSTALLED','INSTALLATION_REPLAYED')),
  entity_type text NOT NULL CHECK (entity_type IN ('WORKSPACE','DOMAIN','DEPARTMENT','HOLON')),
  entity_id uuid NOT NULL,
  actor_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT
);
CREATE INDEX structure_installation_events_workspace_idx
  ON enterprise.structure_installation_events (organization_id, workspace_id, occurred_at DESC);

ALTER TABLE enterprise.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE areas.domain_installations ENABLE ROW LEVEL SECURITY;
ALTER TABLE enterprise.department_installations ENABLE ROW LEVEL SECURITY;
ALTER TABLE areas.holon_installations ENABLE ROW LEVEL SECURITY;
ALTER TABLE enterprise.structure_installation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE enterprise.structure_installation_events ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON ALL TABLES IN SCHEMA enterprise FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA areas FROM PUBLIC, anon, authenticated;
GRANT ALL ON enterprise.workspaces, enterprise.department_installations,
  enterprise.structure_installation_requests, enterprise.structure_installation_events TO service_role;
GRANT ALL ON areas.domain_installations, areas.holon_installations TO service_role;

REVOKE UPDATE, DELETE, TRUNCATE ON enterprise.structure_installation_events FROM service_role;
CREATE OR REPLACE FUNCTION api.reject_structure_installation_event_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
  RAISE EXCEPTION 'enterprise.structure_installation_events is append-only';
END;
$$;
REVOKE ALL ON FUNCTION api.reject_structure_installation_event_mutation() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION api.reject_structure_installation_event_mutation() TO service_role;
CREATE TRIGGER structure_installation_events_append_only
  BEFORE UPDATE OR DELETE ON enterprise.structure_installation_events
  FOR EACH ROW EXECUTE FUNCTION api.reject_structure_installation_event_mutation();

COMMENT ON TABLE enterprise.workspaces IS
  'Tenant-owned operating workspaces. A workspace always belongs to exactly one organization.';
COMMENT ON TABLE areas.domain_installations IS
  'Tenant-owned domain instances installed from global Areas OS domain blueprints; never seeded implicitly.';
COMMENT ON TABLE enterprise.department_installations IS
  'Tenant-owned Marketplace operating department instances; distinct from Areas OS domain installations.';
COMMENT ON TABLE areas.holon_installations IS
  'Tenant-owned LD01 holon instances. These are structural installations, not executable agent principals.';
COMMENT ON TABLE enterprise.structure_installation_requests IS
  'Idempotency ledger for workspace structure installation requests and their exact result snapshots.';
COMMENT ON TABLE enterprise.structure_installation_events IS
  'Append-only audit trail for workspace and structure installation state transitions.';

COMMIT;
