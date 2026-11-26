BEGIN;
CREATE INDEX IF NOT EXISTS workspace_memberships_granted_by_idx
  ON enterprise.workspace_memberships (granted_by_user_id);
CREATE INDEX IF NOT EXISTS domain_installations_owner_idx
  ON areas.domain_installations (owner_user_id) WHERE owner_user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS domain_installations_installed_by_idx
  ON areas.domain_installations (installed_by_user_id);
CREATE INDEX IF NOT EXISTS department_installations_owner_idx
  ON enterprise.department_installations (owner_user_id) WHERE owner_user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS department_installations_installed_by_idx
  ON enterprise.department_installations (installed_by_user_id);
CREATE INDEX IF NOT EXISTS holon_installations_owner_idx
  ON areas.holon_installations (owner_user_id) WHERE owner_user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS holon_installations_installed_by_idx
  ON areas.holon_installations (installed_by_user_id);
CREATE INDEX IF NOT EXISTS structure_installation_requests_creator_idx
  ON enterprise.structure_installation_requests (created_by_user_id);
CREATE INDEX IF NOT EXISTS structure_installation_events_actor_idx
  ON enterprise.structure_installation_events (actor_user_id);
CREATE INDEX IF NOT EXISTS structure_installation_events_request_idx
  ON enterprise.structure_installation_events (request_id) WHERE request_id IS NOT NULL;
COMMIT;