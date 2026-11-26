BEGIN;

CREATE TABLE integration.provider_adapter_manifests (
  provider_key text NOT NULL REFERENCES integration.provider_adapter_blueprints(provider_key) ON DELETE RESTRICT,
  manifest_version text NOT NULL CHECK (manifest_version ~ '^[0-9]+\\\\.[0-9]+\\\\.[0-9]+([+-][A-Za-z0-9.-]+)?$'),
  family_key text NOT NULL REFERENCES integration.adapter_family_blueprints(family_key) ON DELETE RESTRICT,
  base_url text NOT NULL CHECK (base_url ~ '^https://[^[:space:]]+$'),
  allowed_hosts text[] NOT NULL CHECK (cardinality(allowed_hosts) > 0),
  auth_method text NOT NULL CHECK (auth_method IN ('NONE','BEARER','API_KEY_HEADER','BASIC','OAUTH2_AUTH_CODE','OAUTH2_CLIENT_CREDENTIALS')),
  auth_config jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(auth_config) = 'object'),
  default_scopes text[] NOT NULL DEFAULT ARRAY[]::text[],
  operations jsonb NOT NULL CHECK (jsonb_typeof(operations) = 'object'),
  timeout_ms integer NOT NULL DEFAULT 30000 CHECK (timeout_ms BETWEEN 1000 AND 120000),
  manifest_status text NOT NULL DEFAULT 'DRAFT' CHECK (manifest_status IN ('DRAFT','ACTIVE','DEPRECATED')),
  created_by_user_id uuid REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (provider_key, manifest_version),
  CHECK (array_position(allowed_hosts, lower(split_part(split_part(base_url, '://', 2), '/', 1))) IS NOT NULL)
);

CREATE INDEX provider_adapter_manifests_family_status_idx
  ON integration.provider_adapter_manifests (family_key, manifest_status);

CREATE TABLE integration.tenant_connections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  workspace_id uuid NOT NULL,
  provider_key text NOT NULL,
  manifest_version text NOT NULL,
  connection_key text NOT NULL CHECK (connection_key ~ '^[a-z0-9][a-z0-9._-]{1,95}$'),
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 160),
  auth_method text NOT NULL CHECK (auth_method IN ('NONE','BEARER','API_KEY_HEADER','BASIC','OAUTH2_AUTH_CODE','OAUTH2_CLIENT_CREDENTIALS')),
  secret_id uuid,
  granted_scopes text[] NOT NULL DEFAULT ARRAY[]::text[],
  provider_account_ref text,
  connection_status text NOT NULL DEFAULT 'PENDING_AUTH'
    CHECK (connection_status IN ('PENDING_AUTH','CONNECTED','DEGRADED','REVOKED','ERROR')),
  safe_metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(safe_metadata) = 'object'),
  last_health_check_at timestamptz,
  last_error_code text,
  connected_at timestamptz,
  revoked_at timestamptz,
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  FOREIGN KEY (provider_key, manifest_version)
    REFERENCES integration.provider_adapter_manifests(provider_key, manifest_version) ON DELETE RESTRICT,
  UNIQUE (workspace_id, connection_key),
  UNIQUE (id, organization_id, workspace_id),
  CHECK (connection_status <> 'CONNECTED' OR auth_method = 'NONE' OR secret_id IS NOT NULL),
  CHECK ((connection_status = 'REVOKED' AND revoked_at IS NOT NULL) OR connection_status <> 'REVOKED')
);

CREATE INDEX tenant_connections_org_workspace_status_idx
  ON integration.tenant_connections (organization_id, workspace_id, connection_status);
CREATE INDEX tenant_connections_provider_status_idx
  ON integration.tenant_connections (provider_key, connection_status);

CREATE TABLE integration.adapter_oauth_transactions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  workspace_id uuid NOT NULL,
  provider_key text NOT NULL,
  manifest_version text NOT NULL,
  connection_id uuid,
  initiated_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  state_digest bytea NOT NULL UNIQUE CHECK (octet_length(state_digest) = 32),
  pkce_secret_id uuid,
  redirect_uri text NOT NULL CHECK (redirect_uri ~ '^https://[^[:space:]]+$'),
  transaction_status text NOT NULL DEFAULT 'PENDING'
    CHECK (transaction_status IN ('PENDING','COMPLETED','FAILED','EXPIRED','REVOKED')),
  expires_at timestamptz NOT NULL DEFAULT (now() + interval '10 minutes'),
  consumed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  FOREIGN KEY (provider_key, manifest_version)
    REFERENCES integration.provider_adapter_manifests(provider_key, manifest_version) ON DELETE RESTRICT,
  FOREIGN KEY (connection_id, organization_id, workspace_id)
    REFERENCES integration.tenant_connections(id, organization_id, workspace_id) ON DELETE RESTRICT,
  CHECK (expires_at > created_at),
  CHECK ((transaction_status = 'COMPLETED' AND consumed_at IS NOT NULL) OR transaction_status <> 'COMPLETED')
);

CREATE INDEX adapter_oauth_transactions_workspace_status_idx
  ON integration.adapter_oauth_transactions (workspace_id, transaction_status, expires_at);

CREATE TABLE integration.adapter_execution_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  workspace_id uuid NOT NULL,
  connection_id uuid NOT NULL,
  provider_key text NOT NULL,
  manifest_version text NOT NULL,
  operation_key text NOT NULL CHECK (operation_key ~ '^[a-z][a-z0-9._-]{1,95}$'),
  idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 8 AND 200),
  request_payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(request_payload) = 'object'),
  result_payload jsonb CHECK (result_payload IS NULL OR jsonb_typeof(result_payload) = 'object'),
  job_status text NOT NULL DEFAULT 'QUEUED'
    CHECK (job_status IN ('QUEUED','RUNNING','RETRY_WAIT','SUCCEEDED','FAILED','CANCELLED')),
  attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  max_attempts integer NOT NULL DEFAULT 5 CHECK (max_attempts BETWEEN 1 AND 12),
  scheduled_at timestamptz NOT NULL DEFAULT now(),
  locked_by text,
  locked_at timestamptz,
  lease_expires_at timestamptz,
  correlation_id uuid NOT NULL DEFAULT gen_random_uuid(),
  error_code text,
  error_message text CHECK (error_message IS NULL OR length(error_message) <= 500),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  started_at timestamptz,
  completed_at timestamptz,
  FOREIGN KEY (workspace_id, organization_id)
    REFERENCES enterprise.workspaces(id, organization_id) ON DELETE RESTRICT,
  FOREIGN KEY (connection_id, organization_id, workspace_id)
    REFERENCES integration.tenant_connections(id, organization_id, workspace_id) ON DELETE RESTRICT,
  FOREIGN KEY (provider_key, manifest_version)
    REFERENCES integration.provider_adapter_manifests(provider_key, manifest_version) ON DELETE RESTRICT,
  UNIQUE (connection_id, idempotency_key),
  UNIQUE (id, organization_id, workspace_id),
  CHECK ((job_status = 'RUNNING' AND locked_by IS NOT NULL AND lease_expires_at IS NOT NULL)
      OR job_status <> 'RUNNING'),
  CHECK ((job_status IN ('SUCCEEDED','FAILED','CANCELLED') AND completed_at IS NOT NULL)
      OR job_status NOT IN ('SUCCEEDED','FAILED','CANCELLED'))
);

CREATE INDEX adapter_execution_jobs_claim_idx
  ON integration.adapter_execution_jobs (job_status, scheduled_at, created_at);
CREATE INDEX adapter_execution_jobs_connection_idx
  ON integration.adapter_execution_jobs (connection_id, created_at DESC);
CREATE INDEX adapter_execution_jobs_workspace_idx
  ON integration.adapter_execution_jobs (organization_id, workspace_id, created_at DESC);

CREATE TABLE integration.adapter_execution_events (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  job_id uuid NOT NULL,
  organization_id uuid NOT NULL,
  workspace_id uuid NOT NULL,
  event_type text NOT NULL CHECK (event_type IN (
    'ENQUEUED','CLAIMED','LEASE_RECLAIMED','SUCCEEDED','FAILED','RETRY_SCHEDULED','CANCELLED'
  )),
  worker_id text,
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(event_payload) = 'object'),
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (job_id, organization_id, workspace_id)
    REFERENCES integration.adapter_execution_jobs(id, organization_id, workspace_id) ON DELETE RESTRICT
);

CREATE INDEX adapter_execution_events_job_idx
  ON integration.adapter_execution_events (job_id, created_at);

CREATE TABLE integration.adapter_webhook_receipts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  connection_id uuid NOT NULL REFERENCES integration.tenant_connections(id) ON DELETE RESTRICT,
  provider_event_id text NOT NULL CHECK (length(provider_event_id) BETWEEN 1 AND 240),
  payload_sha256 bytea NOT NULL CHECK (octet_length(payload_sha256) = 32),
  signature_verified boolean NOT NULL DEFAULT false,
  receipt_status text NOT NULL DEFAULT 'RECEIVED'
    CHECK (receipt_status IN ('RECEIVED','PROCESSED','REJECTED','FAILED')),
  received_at timestamptz NOT NULL DEFAULT now(),
  processed_at timestamptz,
  safe_metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(safe_metadata) = 'object'),
  UNIQUE (connection_id, provider_event_id),
  CHECK ((receipt_status = 'PROCESSED' AND processed_at IS NOT NULL) OR receipt_status <> 'PROCESSED')
);

CREATE INDEX adapter_webhook_receipts_status_idx
  ON integration.adapter_webhook_receipts (receipt_status, received_at);

ALTER TABLE integration.provider_adapter_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration.tenant_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration.adapter_oauth_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration.adapter_execution_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration.adapter_execution_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration.adapter_webhook_receipts ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE
  integration.provider_adapter_manifests,
  integration.tenant_connections,
  integration.adapter_oauth_transactions,
  integration.adapter_execution_jobs,
  integration.adapter_execution_events,
  integration.adapter_webhook_receipts
FROM PUBLIC, anon, authenticated;

GRANT ALL ON TABLE
  integration.provider_adapter_manifests,
  integration.tenant_connections,
  integration.adapter_oauth_transactions,
  integration.adapter_execution_jobs,
  integration.adapter_execution_events,
  integration.adapter_webhook_receipts
TO service_role;

GRANT USAGE, SELECT ON SEQUENCE integration.adapter_execution_events_id_seq TO service_role;

CREATE OR REPLACE FUNCTION api.reject_adapter_execution_event_mutation()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $function$
BEGIN
  RAISE EXCEPTION 'integration.adapter_execution_events is append-only';
END
$function$;

REVOKE ALL ON FUNCTION api.reject_adapter_execution_event_mutation() FROM PUBLIC, anon, authenticated;
CREATE TRIGGER adapter_execution_events_append_only
BEFORE UPDATE OR DELETE ON integration.adapter_execution_events
FOR EACH ROW EXECUTE FUNCTION api.reject_adapter_execution_event_mutation();

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
    RETURNING j.*, c.previous_status
  ),
  logged AS (
    INSERT INTO integration.adapter_execution_events
      (job_id, organization_id, workspace_id, event_type, worker_id, event_payload)
    SELECT id, organization_id, workspace_id,
      CASE WHEN previous_status = 'RUNNING' THEN 'LEASE_RECLAIMED' ELSE 'CLAIMED' END,
      p_worker_id,
      jsonb_build_object('attempt', attempt_count)
    FROM claimed
    RETURNING id
  )
  SELECT (claimed).* FROM claimed;
END
$function$;

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
  IF p_outcome NOT IN ('SUCCEEDED','FAILED','RETRY_WAIT') THEN
    RAISE EXCEPTION 'Invalid execution outcome';
  END IF;
  IF p_result_payload IS NOT NULL AND jsonb_typeof(p_result_payload) <> 'object' THEN
    RAISE EXCEPTION 'result_payload must be a JSON object';
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
      error_code = CASE WHEN v_status IN ('FAILED','RETRY_WAIT') THEN p_error_code ELSE NULL END,
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

REVOKE ALL ON FUNCTION api.claim_adapter_execution_jobs(text, integer) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION api.finish_adapter_execution_job(uuid, text, text, jsonb, text, text, integer) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION api.claim_adapter_execution_jobs(text, integer) TO service_role;
GRANT EXECUTE ON FUNCTION api.finish_adapter_execution_job(uuid, text, text, jsonb, text, text, integer) TO service_role;

COMMENT ON TABLE integration.provider_adapter_manifests IS
  'Versioned provider execution manifests. Only reviewed, provider-specific manifests may be ACTIVE; no credentials belong here.';
COMMENT ON TABLE integration.tenant_connections IS
  'Tenant/workspace-scoped provider connections. secret_id is a reference to Supabase Vault; secret material is never stored in this table.';
COMMENT ON TABLE integration.adapter_oauth_transactions IS
  'Short-lived OAuth state ledger. Stores only a SHA-256 state digest and Vault references, never raw OAuth state, codes or tokens.';
COMMENT ON TABLE integration.adapter_execution_jobs IS
  'Durable, idempotent adapter execution queue with bounded leases and retry lifecycle.';
COMMENT ON TABLE integration.adapter_execution_events IS
  'Append-only audit events for adapter execution claims, lease recovery and outcomes.';
COMMENT ON TABLE integration.adapter_webhook_receipts IS
  'Webhook deduplication receipts; stores payload hashes and safe metadata, never raw provider secrets.';

COMMIT;
