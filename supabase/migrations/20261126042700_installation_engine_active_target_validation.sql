CREATE OR REPLACE FUNCTION enterprise.assert_installation_target(p_org uuid,p_workspace uuid,p_type text,p_id uuid)
RETURNS boolean LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,enterprise,areas AS $$
BEGIN
 IF p_type='DOMAIN' THEN RETURN EXISTS(SELECT 1 FROM areas.domain_installations WHERE id=p_id AND organization_id=p_org AND workspace_id=p_workspace AND installation_status='ACTIVE');
 ELSIF p_type='DEPARTMENT' THEN RETURN EXISTS(SELECT 1 FROM enterprise.department_installations WHERE id=p_id AND organization_id=p_org AND workspace_id=p_workspace AND installation_status='ACTIVE');
 ELSIF p_type='HOLON' THEN RETURN EXISTS(SELECT 1 FROM areas.holon_installations WHERE id=p_id AND organization_id=p_org AND workspace_id=p_workspace AND installation_status='ACTIVE');
 END IF;
 RETURN false;
END; $$;
REVOKE ALL ON FUNCTION enterprise.assert_installation_target(uuid,uuid,text,uuid) FROM PUBLIC,anon,authenticated;