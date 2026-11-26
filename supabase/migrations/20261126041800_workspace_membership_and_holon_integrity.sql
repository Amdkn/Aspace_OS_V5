BEGIN;

CREATE TABLE enterprise.workspace_memberships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  membership_status text NOT NULL DEFAULT 'ACTIVE'
    CHECK (membership_status IN ('ACTIVE','SUSPENDED','REVOKED')),
  workspace_role text NOT NULL DEFAULT 'MEMBER'
    CHECK (workspace_role IN ('OWNER','ADMIN','MEMBER','VIEWER')),
  granted_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  UNIQUE (workspace_id, user_id),
  UNIQUE (id, workspace_id, organization_id)
);
CREATE INDEX workspace_memberships_user_status_idx
  ON enterprise.workspace_memberships (user_id, membership_status, workspace_id);
CREATE INDEX workspace_memberships_org_role_idx
  ON enterprise.workspace_memberships (organization_id, workspace_id, workspace_role);

ALTER TABLE enterprise.workspace_memberships ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON enterprise.workspace_memberships FROM PUBLIC, anon, authenticated;
GRANT ALL ON enterprise.workspace_memberships TO service_role;

ALTER TABLE areas.domain_installations
  ADD CONSTRAINT domain_installations_id_domain_code_key UNIQUE (id, domain_code);

ALTER TABLE areas.holon_blueprints
  ADD CONSTRAINT holon_blueprints_holon_code_area_code_key UNIQUE (holon_code, area_code);

ALTER TABLE areas.holon_installations
  ADD COLUMN domain_code text NOT NULL;

ALTER TABLE areas.holon_installations
  ADD CONSTRAINT holon_installations_id_domain_workspace_org_key
  UNIQUE (id, domain_installation_id, workspace_id, organization_id);

ALTER TABLE areas.holon_installations
  DROP CONSTRAINT holon_installations_parent_installation_id_workspace_id_or_fkey;

ALTER TABLE areas.holon_installations
  ADD CONSTRAINT holon_installations_domain_code_installation_fk
  FOREIGN KEY (domain_installation_id, domain_code)
  REFERENCES areas.domain_installations(id, domain_code) ON DELETE RESTRICT;

ALTER TABLE areas.holon_installations
  ADD CONSTRAINT holon_installations_holon_domain_blueprint_fk
  FOREIGN KEY (holon_code, domain_code)
  REFERENCES areas.holon_blueprints(holon_code, area_code) ON DELETE RESTRICT;

ALTER TABLE areas.holon_installations
  ADD CONSTRAINT holon_installations_parent_same_domain_fk
  FOREIGN KEY (parent_installation_id, domain_installation_id, workspace_id, organization_id)
  REFERENCES areas.holon_installations(id, domain_installation_id, workspace_id, organization_id)
  ON DELETE RESTRICT;

COMMENT ON TABLE enterprise.workspace_memberships IS
  'Explicit tenant workspace membership and scoped workspace role; organization membership alone never grants workspace access.';

COMMIT;
