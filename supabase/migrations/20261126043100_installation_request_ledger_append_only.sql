CREATE OR REPLACE FUNCTION api.reject_structure_installation_request_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog
AS $$
BEGIN
  RAISE EXCEPTION 'enterprise.structure_installation_requests is append-only';
END;
$$;
REVOKE ALL ON FUNCTION api.reject_structure_installation_request_mutation() FROM PUBLIC,anon,authenticated;
CREATE TRIGGER structure_installation_requests_append_only
BEFORE UPDATE OR DELETE ON enterprise.structure_installation_requests
FOR EACH ROW EXECUTE FUNCTION api.reject_structure_installation_request_mutation();