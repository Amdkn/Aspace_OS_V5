CREATE OR REPLACE FUNCTION enterprise.validate_ownership_assignment()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,enterprise,identity,areas AS $$
BEGIN
 IF NEW.assignment_status<>'ACTIVE' THEN RETURN NEW; END IF;
 IF NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.entity_type,NEW.installation_id) THEN RAISE EXCEPTION 'Ownership target does not belong to this organization/workspace'; END IF;
 IF NEW.principal_type='USER' THEN
  IF NOT EXISTS(SELECT 1 FROM enterprise.workspace_memberships wm WHERE wm.organization_id=NEW.organization_id AND wm.workspace_id=NEW.workspace_id AND wm.user_id=NEW.user_id AND wm.membership_status='ACTIVE') THEN RAISE EXCEPTION 'Assigned user must be an active workspace member'; END IF;
 ELSE
  IF NOT EXISTS(SELECT 1 FROM identity.agent_principals ap WHERE ap.id=NEW.agent_principal_id AND ap.organization_id=NEW.organization_id AND ap.principal_status='ACTIVE') THEN RAISE EXCEPTION 'Assigned agent must be an active principal in this organization'; END IF;
 END IF;
 RETURN NEW;
END; $$;
CREATE OR REPLACE FUNCTION enterprise.validate_installation_dependency()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,enterprise,areas AS $$
DECLARE cycle_found boolean;
BEGIN
 IF NEW.dependency_status<>'ACTIVE' THEN RETURN NEW; END IF;
 IF NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.source_entity_type,NEW.source_installation_id)
 OR NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.depends_on_entity_type,NEW.depends_on_installation_id) THEN RAISE EXCEPTION 'Dependency endpoints must belong to the same organization/workspace'; END IF;
 WITH RECURSIVE reachable(entity_type,installation_id) AS (
  SELECT d.depends_on_entity_type,d.depends_on_installation_id FROM enterprise.installation_dependencies d
  WHERE d.workspace_id=NEW.workspace_id AND d.source_entity_type=NEW.depends_on_entity_type AND d.source_installation_id=NEW.depends_on_installation_id AND d.dependency_status='ACTIVE' AND d.id IS DISTINCT FROM NEW.id
  UNION
  SELECT d.depends_on_entity_type,d.depends_on_installation_id FROM enterprise.installation_dependencies d
  JOIN reachable r ON d.source_entity_type=r.entity_type AND d.source_installation_id=r.installation_id
  WHERE d.workspace_id=NEW.workspace_id AND d.dependency_status='ACTIVE' AND d.id IS DISTINCT FROM NEW.id
 ) SELECT EXISTS(SELECT 1 FROM reachable WHERE entity_type=NEW.source_entity_type AND installation_id=NEW.source_installation_id) INTO cycle_found;
 IF cycle_found THEN RAISE EXCEPTION 'Dependency would create a cycle'; END IF;
 RETURN NEW;
END; $$;
CREATE OR REPLACE FUNCTION catalog.validate_capability_installation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,enterprise,areas,catalog AS $$
BEGIN
 IF NEW.installation_status<>'ACTIVE' THEN RETURN NEW; END IF;
 IF NOT enterprise.assert_installation_target(NEW.organization_id,NEW.workspace_id,NEW.target_entity_type,NEW.target_installation_id) THEN RAISE EXCEPTION 'Capability target does not belong to this organization/workspace'; END IF;
 IF NEW.capability_owner_organization_id<>NEW.organization_id THEN RAISE EXCEPTION 'External capability installation requires a completed marketplace entitlement'; END IF;
 IF NOT EXISTS(SELECT 1 FROM catalog.capabilities c JOIN catalog.capability_versions v ON v.capability_id=c.id WHERE c.id=NEW.capability_id AND c.owner_organization_id=NEW.capability_owner_organization_id AND c.capability_status='ACTIVE' AND v.id=NEW.capability_version_id AND v.version_status='ACTIVE') THEN RAISE EXCEPTION 'Capability or capability version is not active'; END IF;
 RETURN NEW;
END; $$;
REVOKE ALL ON FUNCTION enterprise.validate_ownership_assignment() FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION enterprise.validate_installation_dependency() FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION catalog.validate_capability_installation() FROM PUBLIC,anon,authenticated;