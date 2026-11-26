BEGIN;

CREATE TABLE enterprise.installation_ownership_assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  entity_type text NOT NULL CHECK (entity_type IN ('DOMAIN','DEPARTMENT','HOLON')),
  installation_id uuid NOT NULL,
  principal_type text NOT NULL CHECK (principal_type IN ('USER','AGENT')),
  user_id uuid REFERENCES auth.users(id) ON DELETE RESTRICT,
  agent_principal_id uuid,
  assignment_role text NOT NULL CHECK (assignment_role IN ('OWNER','MANAGER','TECHNICIAN','STEWARD','OBSERVER')),
  assignment_status text NOT NULL DEFAULT 'ACTIVE' CHECK (assignment_status IN ('ACTIVE','REVOKED','EXPIRED')),
  assigned_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  starts_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((principal_type='USER' AND user_id IS NOT NULL AND agent_principal_id IS NULL)
      OR (principal_type='AGENT' AND agent_principal_id IS NOT NULL AND user_id IS NULL)),
  CHECK (expires_at IS NULL OR expires_at > starts_at)
);
CREATE INDEX installation_ownership_workspace_idx ON enterprise.installation_ownership_assignments(workspace_id,entity_type,installation_id,assignment_status);
CREATE INDEX installation_ownership_principal_idx ON enterprise.installation_ownership_assignments(organization_id,principal_type,user_id,agent_principal_id);
CREATE UNIQUE INDEX installation_ownership_active_principal_role_uq ON enterprise.installation_ownership_assignments(entity_type,installation_id,principal_type,coalesce(user_id,agent_principal_id),assignment_role) WHERE assignment_status='ACTIVE';
CREATE UNIQUE INDEX installation_ownership_single_owner_uq ON enterprise.installation_ownership_assignments(entity_type,installation_id) WHERE assignment_status='ACTIVE' AND assignment_role='OWNER';

CREATE TABLE enterprise.installation_dependencies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  source_entity_type text NOT NULL CHECK (source_entity_type IN ('DOMAIN','DEPARTMENT','HOLON')),
  source_installation_id uuid NOT NULL,
  depends_on_entity_type text NOT NULL CHECK (depends_on_entity_type IN ('DOMAIN','DEPARTMENT','HOLON')),
  depends_on_installation_id uuid NOT NULL,
  dependency_type text NOT NULL DEFAULT 'REQUIRES' CHECK (dependency_type IN ('REQUIRES','BLOCKS','INFORMS','CONTAINS')),
  dependency_status text NOT NULL DEFAULT 'ACTIVE' CHECK (dependency_status IN ('ACTIVE','REMOVED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  removed_at timestamptz,
  CHECK (source_entity_type <> depends_on_entity_type OR source_installation_id <> depends_on_installation_id),
  UNIQUE(workspace_id,source_entity_type,source_installation_id,depends_on_entity_type,depends_on_installation_id,dependency_type),
  FOREIGN KEY(workspace_id,organization_id) REFERENCES enterprise.workspaces(id,organization_id) ON DELETE RESTRICT
);
CREATE INDEX installation_dependencies_source_idx ON enterprise.installation_dependencies(workspace_id,source_entity_type,source_installation_id,dependency_status);
CREATE INDEX installation_dependencies_target_idx ON enterprise.installation_dependencies(workspace_id,depends_on_entity_type,depends_on_installation_id,dependency_status);

CREATE TABLE catalog.capability_installations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  target_entity_type text NOT NULL CHECK (target_entity_type IN ('DOMAIN','DEPARTMENT','HOLON')),
  target_installation_id uuid NOT NULL,
  capability_id uuid NOT NULL,
  capability_owner_organization_id uuid NOT NULL,
  capability_version_id uuid NOT NULL,
  installation_status text NOT NULL DEFAULT 'ACTIVE' CHECK (installation_status IN ('ACTIVE','SUSPENDED','REMOVED')),
  configuration jsonb NOT NULL DEFAULT '{}'::jsonb,
  installed_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  installed_at timestamptz NOT NULL DEFAULT now(),
  removed_at timestamptz,
  FOREIGN KEY(workspace_id,organization_id) REFERENCES enterprise.workspaces(id,organization_id) ON DELETE RESTRICT,
  FOREIGN KEY(capability_id,capability_owner_organization_id) REFERENCES catalog.capabilities(id,owner_organization_id) ON DELETE RESTRICT,
  FOREIGN KEY(capability_version_id,capability_id) REFERENCES catalog.capability_versions(id,capability_id) ON DELETE RESTRICT,
  UNIQUE(workspace_id,target_entity_type,target_installation_id,capability_id,capability_version_id)
);
CREATE INDEX capability_installations_target_idx ON catalog.capability_installations(workspace_id,target_entity_type,target_installation_id,installation_status);
CREATE INDEX capability_installations_capability_idx ON catalog.capability_installations(capability_id,capability_version_id,installation_status);

CREATE OR REPLACE FUNCTION enterprise.assert_installation_target(p_org uuid,p_workspace uuid,p_type text,p_id uuid)
RETURNS boolean LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,enterprise,areas AS $$
BEGIN
 IF p_type='DOMAIN' THEN RETURN EXISTS(SELECT 1 FROM areas.domain_installations WHERE id=p_id AND organization_id=p_org AND workspace_id=p_workspace);
 ELSIF p_type='DEPARTMENT' THEN RETURN EXISTS(SELECT 1 FROM enterprise.department_installations WHERE id=p_id AND organization_id=p_org AND workspace_id=p_workspace);
 ELSIF p_type='HOLON' THEN RETURN EXISTS(SELECT 1 FROM areas.holon_installations WHERE id=p_id AND organization_id=p_org AND workspace_id=p_workspace);
 END IF;
 RETURN false;
END; $$;

CREATE OR REPLACE FUNCTION enterprise.validate_ownership_assignment()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,enterprise,identity,areas AS $$
BEGIN
 IF NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.entity_type,NEW.installation_id) THEN RAISE EXCEPTION 'Ownership target does not belong to this organization/workspace'; END IF;
 IF NEW.principal_type='USER' THEN
  IF NOT EXISTS(SELECT 1 FROM enterprise.workspace_memberships wm WHERE wm.organization_id=NEW.organization_id AND wm.workspace_id=NEW.workspace_id AND wm.user_id=NEW.user_id AND wm.membership_status='ACTIVE') THEN RAISE EXCEPTION 'Assigned user must be an active workspace member'; END IF;
 ELSE
  IF NOT EXISTS(SELECT 1 FROM identity.agent_principals ap WHERE ap.id=NEW.agent_principal_id AND ap.organization_id=NEW.organization_id AND ap.principal_status='ACTIVE') THEN RAISE EXCEPTION 'Assigned agent must be an active principal in this organization'; END IF;
 END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER installation_ownership_validate BEFORE INSERT OR UPDATE ON enterprise.installation_ownership_assignments FOR EACH ROW EXECUTE FUNCTION enterprise.validate_ownership_assignment();

CREATE OR REPLACE FUNCTION enterprise.validate_installation_dependency()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,enterprise,areas AS $$
DECLARE cycle_found boolean;
BEGIN
 IF NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.source_entity_type,NEW.source_installation_id)
 OR NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.depends_on_entity_type,NEW.depends_on_installation_id) THEN RAISE EXCEPTION 'Dependency endpoints must belong to the same organization/workspace'; END IF;
 IF NEW.dependency_status='ACTIVE' THEN
  WITH RECURSIVE reachable(entity_type,installation_id) AS (
   SELECT d.depends_on_entity_type,d.depends_on_installation_id FROM enterprise.installation_dependencies d
   WHERE d.workspace_id=NEW.workspace_id AND d.source_entity_type=NEW.depends_on_entity_type AND d.source_installation_id=NEW.depends_on_installation_id AND d.dependency_status='ACTIVE'
   UNION
   SELECT d.depends_on_entity_type,d.depends_on_installation_id FROM enterprise.installation_dependencies d
   JOIN reachable r ON d.source_entity_type=r.entity_type AND d.source_installation_id=r.installation_id
   WHERE d.workspace_id=NEW.workspace_id AND d.dependency_status='ACTIVE'
  ) SELECT EXISTS(SELECT 1 FROM reachable WHERE entity_type=NEW.source_entity_type AND installation_id=NEW.source_installation_id) INTO cycle_found;
  IF cycle_found THEN RAISE EXCEPTION 'Dependency would create a cycle'; END IF;
 END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER installation_dependency_validate BEFORE INSERT OR UPDATE ON enterprise.installation_dependencies FOR EACH ROW EXECUTE FUNCTION enterprise.validate_installation_dependency();

CREATE OR REPLACE FUNCTION catalog.validate_capability_installation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,enterprise,areas,catalog AS $$
BEGIN
 IF NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.target_entity_type,NEW.target_installation_id) THEN RAISE EXCEPTION 'Capability target does not belong to this organization/workspace'; END IF;
 IF NEW.capability_owner_organization_id<>NEW.organization_id THEN RAISE EXCEPTION 'External capability installation requires a completed marketplace entitlement'; END IF;
 IF NOT EXISTS(SELECT 1 FROM catalog.capabilities c JOIN catalog.capability_versions v ON v.capability_id=c.id WHERE c.id=NEW.capability_id AND c.owner_organization_id=NEW.capability_owner_organization_id AND c.capability_status='ACTIVE' AND v.id=NEW.capability_version_id AND v.version_status='ACTIVE') THEN RAISE EXCEPTION 'Capability or capability version is not active'; END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER capability_installation_validate BEFORE INSERT OR UPDATE ON catalog.capability_installations FOR EACH ROW EXECUTE FUNCTION catalog.validate_capability_installation();

ALTER TABLE enterprise.installation_ownership_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE enterprise.installation_dependencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.capability_installations ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON enterprise.installation_ownership_assignments,enterprise.installation_dependencies,catalog.capability_installations FROM PUBLIC,anon,authenticated;
GRANT ALL ON enterprise.installation_ownership_assignments,enterprise.installation_dependencies,catalog.capability_installations TO service_role;
REVOKE ALL ON FUNCTION enterprise.assert_installation_target(uuid,uuid,text,uuid) FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION enterprise.validate_ownership_assignment() FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION enterprise.validate_installation_dependency() FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION catalog.validate_capability_installation() FROM PUBLIC,anon,authenticated;

ALTER TABLE enterprise.structure_installation_events DROP CONSTRAINT structure_installation_events_event_type_check;
ALTER TABLE enterprise.structure_installation_events ADD CONSTRAINT structure_installation_events_event_type_check CHECK (event_type = ANY (ARRAY['WORKSPACE_CREATED','DOMAIN_INSTALLED','DEPARTMENT_INSTALLED','HOLON_INSTALLED','INSTALLATION_REPLAYED','OWNERSHIP_ASSIGNED','OWNERSHIP_REVOKED','DEPENDENCY_ADDED','DEPENDENCY_REMOVED','CAPABILITY_INSTALLED','CAPABILITY_REMOVED']));
ALTER TABLE enterprise.structure_installation_events DROP CONSTRAINT structure_installation_events_entity_type_check;
ALTER TABLE enterprise.structure_installation_events ADD CONSTRAINT structure_installation_events_entity_type_check CHECK (entity_type = ANY (ARRAY['WORKSPACE','DOMAIN','DEPARTMENT','HOLON','OWNERSHIP','DEPENDENCY','CAPABILITY']));

COMMIT;