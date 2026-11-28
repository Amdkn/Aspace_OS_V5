CREATE OR REPLACE FUNCTION api.claim_adapter_execution_jobs(
  p_worker_id text,
  p_limit integer DEFAULT 10
)
RETURNS SETOF integration.adapter_execution_jobs
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, integration, api
AS $function$
BEGIN
  IF p_worker_id IS NULL OR length(btrim(p_worker_id)) NOT BETWEEN 1 AND 120 THEN
    RAISE EXCEPTION 'Invalid worker_id';
  END IF;
  IF p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 50 THEN
    RAISE EXCEPTION 'p_limit must be between 1 and 50';
  END IF;

  RETURN QUERY
  WITH candidates AS (
    SELECT j.id, j.job_status AS previous_status
    FROM integration.adapter_execution_jobs j
    WHERE (j.job_status IN ('QUEUED','RETRY_WAIT') AND j.scheduled_at <= now())
       OR (j.job_status = 'RUNNING' AND j.lease_expires_at <= now())
    ORDER BY j.scheduled_at, j.created_at
    FOR UPDATE SKIP LOCKED
    LIMIT p_limit
  ),
  claimed AS (
    UPDATE integration.adapter_execution_jobs j
    SET job_status = 'RUNNING',
        attempt_count = j.attempt_count + 1,
        locked_by = p_worker_id,
        locked_at = now(),
        lease_expires_at = now() + interval '3 minutes',
        started_at = coalesce(j.started_at, now()),
        updated_at = now()
    FROM candidates c
    WHERE j.id = c.id
      AND j.attempt_count < j.max_attempts
    RETURNING j.id
  ),
  logged AS (
    INSERT INTO integration.adapter_execution_events
      (job_id, organization_id, workspace_id, event_type, worker_id, event_payload)
    SELECT j.id, j.organization_id, j.workspace_id,
      CASE WHEN c.previous_status = 'RUNNING' THEN 'LEASE_RECLAIMED' ELSE 'CLAIMED' END,
      p_worker_id,
      jsonb_build_object('attempt', j.attempt_count)
    FROM claimed cl
    JOIN candidates c ON c.id = cl.id
    JOIN integration.adapter_execution_jobs j ON j.id = cl.id
    RETURNING id
  )
  SELECT j.*
  FROM integration.adapter_execution_jobs j
  JOIN claimed cl ON cl.id = j.id;
END
$function$;

REVOKE ALL ON FUNCTION api.claim_adapter_execution_jobs(text, integer) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION api.claim_adapter_execution_jobs(text, integer) TO service_role;
