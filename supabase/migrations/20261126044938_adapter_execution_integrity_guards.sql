BEGIN;

ALTER TABLE integration.provider_adapter_manifests
  DROP CONSTRAINT provider_adapter_manifests_manifest_version_check;
ALTER TABLE integration.provider_adapter_manifests
  ADD CONSTRAINT provider_adapter_manifests_manifest_version_check
  CHECK (manifest_version ~ '^[0-9]+[.][0-9]+[.][0-9]+([+-][A-Za-z0-9.-]+)?$');

ALTER TABLE integration.provider_adapter_manifests
  ADD CONSTRAINT provider_adapter_manifests_auth_config_no_secrets_check
  CHECK (NOT (auth_config ?| ARRAY[
    'client_secret','api_key','secret','token','password','private_key',
    'access_token','refresh_token'
  ]));

CREATE TRIGGER adapter_execution_events_no_truncate
BEFORE TRUNCATE ON integration.adapter_execution_events
FOR EACH STATEMENT EXECUTE FUNCTION api.reject_adapter_execution_event_mutation();

CREATE OR REPLACE FUNCTION api.finish_adapter_execution_job(
  p_job_id uuid,
  p_worker_id text,
  p_outcome text,
  p_result_payload jsonb DEFAULT NULL,
  p_error_code text DEFAULT NULL,
  p_error_message text DEFAULT NULL,
  p_retry_delay_seconds integer DEFAULT 30
)
RETURNS integration.adapter_execution_jobs
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, integration, api
AS $function$
DECLARE
  v_job integration.adapter_execution_jobs%ROWTYPE;
  v_status text;
  v_event text;
BEGIN
  IF p_job_id IS NULL OR p_worker_id IS NULL OR length(btrim(p_worker_id)) NOT BETWEEN 1 AND 120 THEN
    RAISE EXCEPTION 'Invalid job or worker identity';
  END IF;
  IF p_outcome IS NULL OR p_outcome NOT IN ('SUCCEEDED','FAILED','RETRY_WAIT') THEN
    RAISE EXCEPTION 'Invalid execution outcome';
  END IF;
  IF p_result_payload IS NOT NULL AND jsonb_typeof(p_result_payload) <> 'object' THEN
    RAISE EXCEPTION 'result_payload must be a JSON object';
  END IF;
  IF p_error_code IS NOT NULL AND (length(p_error_code) > 80 OR p_error_code !~ '^[A-Z0-9_]+$') THEN
    RAISE EXCEPTION 'Invalid error_code';
  END IF;
  IF p_error_message IS NOT NULL AND length(p_error_message) > 500 THEN
    RAISE EXCEPTION 'error_message exceeds 500 characters';
  END IF;

  SELECT * INTO v_job
  FROM integration.adapter_execution_jobs
  WHERE id = p_job_id AND job_status = 'RUNNING'
    AND locked_by = p_worker_id AND lease_expires_at > now()
  FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Active job lease not found for this worker';
  END IF;

  v_status := p_outcome;
  IF p_outcome = 'RETRY_WAIT' AND v_job.attempt_count >= v_job.max_attempts THEN
    v_status := 'FAILED';
  END IF;

  UPDATE integration.adapter_execution_jobs
  SET job_status = v_status,
      result_payload = CASE WHEN v_status = 'SUCCEEDED' THEN p_result_payload ELSE NULL END,
      error_code = CASE
        WHEN v_status = 'FAILED' THEN coalesce(p_error_code,'RETRY_LIMIT_EXCEEDED')
        WHEN v_status = 'RETRY_WAIT' THEN p_error_code
        ELSE NULL
      END,
      error_message = CASE WHEN v_status IN ('FAILED','RETRY_WAIT') THEN p_error_message ELSE NULL END,
      scheduled_at = CASE WHEN v_status = 'RETRY_WAIT'
        THEN now() + make_interval(secs => greatest(1, least(coalesce(p_retry_delay_seconds,30),3600)))
        ELSE scheduled_at END,
      locked_by = NULL,
      locked_at = NULL,
      lease_expires_at = NULL,
      completed_at = CASE WHEN v_status IN ('SUCCEEDED','FAILED') THEN now() ELSE NULL END,
      updated_at = now()
  WHERE id = p_job_id
  RETURNING * INTO v_job;

  v_event := CASE v_status
    WHEN 'SUCCEEDED' THEN 'SUCCEEDED'
    WHEN 'RETRY_WAIT' THEN 'RETRY_SCHEDULED'
    ELSE 'FAILED'
  END;

  INSERT INTO integration.adapter_execution_events
    (job_id, organization_id, workspace_id, event_type, worker_id, event_payload)
  VALUES (
    v_job.id, v_job.organization_id, v_job.workspace_id, v_event, p_worker_id,
    jsonb_build_object('attempt', v_job.attempt_count, 'error_code', p_error_code)
  );

  RETURN v_job;
END
$function$;

REVOKE ALL ON FUNCTION api.finish_adapter_execution_job(uuid, text, text, jsonb, text, text, integer) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION api.finish_adapter_execution_job(uuid, text, text, jsonb, text, text, integer) TO service_role;

COMMIT;
