CREATE OR REPLACE FUNCTION api.reject_structure_installation_event_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog
AS $$
BEGIN
  RAISE EXCEPTION 'enterprise.structure_installation_events is append-only' USING ERRCODE='55000';
END;
$$;
CREATE OR REPLACE FUNCTION api.reject_structure_installation_request_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog
AS $$
BEGIN
  RAISE EXCEPTION 'enterprise.structure_installation_requests is append-only' USING ERRCODE='55000';
END;
$$;
REVOKE ALL ON FUNCTION api.reject_structure_installation_event_mutation() FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION api.reject_structure_installation_request_mutation() FROM PUBLIC,anon,authenticated;
DROP TRIGGER structure_installation_events_append_only ON enterprise.structure_installation_events;
DROP TRIGGER structure_installation_requests_append_only ON enterprise.structure_installation_requests;
CREATE TRIGGER structure_installation_events_append_only
BEFORE UPDATE OR DELETE ON enterprise.structure_installation_events
FOR EACH STATEMENT EXECUTE FUNCTION api.reject_structure_installation_event_mutation();
CREATE TRIGGER structure_installation_requests_append_only
BEFORE UPDATE OR DELETE ON enterprise.structure_installation_requests
FOR EACH STATEMENT EXECUTE FUNCTION api.reject_structure_installation_request_mutation();