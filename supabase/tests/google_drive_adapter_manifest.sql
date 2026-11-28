DO $test$
DECLARE
  v_manifest integration.provider_adapter_manifests%ROWTYPE;
  v_blueprint_status text;
  v_auth_contract_status text;
  v_supported_operations text[];
BEGIN
  SELECT * INTO v_manifest
  FROM integration.provider_adapter_manifests
  WHERE provider_key='files-knowledge-google-drive' AND manifest_version='1.0.0';
  IF NOT FOUND THEN RAISE EXCEPTION 'FAIL: Google Drive draft manifest missing'; END IF;
  IF v_manifest.manifest_status <> 'DRAFT' OR v_manifest.auth_method <> 'OAUTH2_AUTH_CODE' THEN
    RAISE EXCEPTION 'FAIL: Google Drive manifest must remain DRAFT with Authorization Code auth';
  END IF;
  SELECT implementation_status,auth_contract_status,supported_operations
  INTO v_blueprint_status,v_auth_contract_status,v_supported_operations
  FROM integration.provider_adapter_blueprints
  WHERE provider_key='files-knowledge-google-drive';
  IF v_blueprint_status <> 'PLANNED' OR v_auth_contract_status <> 'SPECIFIED'
     OR cardinality(v_supported_operations) <> 6 THEN
    RAISE EXCEPTION 'FAIL: Google Drive blueprint must be PLANNED with specified six-operation contract';
  END IF;
  IF v_manifest.base_url <> 'https://www.googleapis.com'
     OR v_manifest.allowed_hosts <> ARRAY['www.googleapis.com']::text[] THEN
    RAISE EXCEPTION 'FAIL: Google Drive API base host allowlist mismatch';
  END IF;
  IF v_manifest.auth_config->>'authorization_url' <> 'https://accounts.google.com/o/oauth2/v2/auth'
     OR v_manifest.auth_config->>'token_url' <> 'https://oauth2.googleapis.com/token'
     OR v_manifest.auth_config->>'revocation_url' <> 'https://oauth2.googleapis.com/revoke' THEN
    RAISE EXCEPTION 'FAIL: Google OAuth endpoint contract mismatch';
  END IF;
  IF v_manifest.auth_config ?| ARRAY['client_secret','secret','token','access_token','refresh_token','api_key'] THEN
    RAISE EXCEPTION 'FAIL: Google Drive manifest contains a credential field';
  END IF;
  IF cardinality(v_manifest.default_scopes) <> 2
     OR NOT ('https://www.googleapis.com/auth/drive.file'=ANY(v_manifest.default_scopes))
     OR NOT ('https://www.googleapis.com/auth/drive.readonly'=ANY(v_manifest.default_scopes)) THEN
    RAISE EXCEPTION 'FAIL: Google Drive scope profile is not the declared least-privilege pair';
  END IF;
  IF (SELECT count(*) FROM jsonb_object_keys(v_manifest.operations)) <> 6 THEN
    RAISE EXCEPTION 'FAIL: Google Drive v1.0.0 operation set is incomplete';
  END IF;
  IF v_manifest.operations->'get_file'->'path_parameters' <> '["fileId"]'::jsonb
     OR v_manifest.operations->'update_file_metadata'->'path_parameters' <> '["fileId"]'::jsonb
     OR v_manifest.operations->'delete_file'->'path_parameters' <> '["fileId"]'::jsonb THEN
    RAISE EXCEPTION 'FAIL: Google Drive file-id path parameter contract mismatch';
  END IF;
  RAISE NOTICE 'PASS: Google Drive draft manifest, endpoints, scopes, no-secret contract and six operations';
END
$test$;
