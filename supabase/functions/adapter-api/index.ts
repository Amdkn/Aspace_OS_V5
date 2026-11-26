import { createClient } from 'npm:@supabase/supabase-js@2.95.0';
import postgres from 'npm:postgres@3.4.5';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};
const url = Deno.env.get('SUPABASE_URL') ?? '';
const anonKey = Deno.env.get('SUPABASE_ANON_KEY') ?? '';
const dbUrl = Deno.env.get('SUPABASE_DB_URL') ?? '';
if (!url || !anonKey || !dbUrl) throw new Error('Required Supabase Edge Function environment is missing');

const authClient = createClient(url, anonKey, { auth: { persistSession: false, autoRefreshToken: false } });
const db = postgres(dbUrl, { max: 1, prepare: false });
type User = { id: string };

function response(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
}
function requiredString(value: unknown, field: string, max = 200): string {
  if (typeof value !== 'string' || !value.trim() || value.trim() !== value || value.length > max) {
    throw new Error(`Invalid ${field}`);
  }
  return value;
}
function uuid(value: unknown, field: string): string {
  const s = requiredString(value, field, 36);
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(s)) {
    throw new Error(`Invalid ${field}`);
  }
  return s;
}
async function authenticate(req: Request): Promise<User> {
  const header = req.headers.get('Authorization') ?? '';
  if (!header.startsWith('Bearer ')) throw new Error('Authentication required');
  const { data, error } = await authClient.auth.getUser(header.slice(7));
  if (error || !data.user) throw new Error('Invalid or expired session');
  return { id: data.user.id };
}
async function withServiceRole<T>(work: (tx: any) => Promise<T>): Promise<T> {
  return await db.begin(async (tx) => {
    await tx`SET LOCAL ROLE service_role`;
    return await work(tx);
  });
}
async function dispatchWorker() {
  const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '';
  if (!serviceRoleKey) {
    console.error('adapter-worker dispatch unavailable: service key is not configured');
    return;
  }
  try {
    const result = await fetch(`${url}/functions/v1/adapter-worker`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'apikey': anonKey,
        'Content-Type': 'application/json',
      },
      body: '{}',
    });
    if (!result.ok) console.error('adapter-worker dispatch failed', result.status);
  } catch (error) {
    console.error('adapter-worker dispatch failed', error instanceof Error ? error.message : 'unknown error');
  }
}

async function requireWorkspaceRole(
  tx: any, userId: string, orgId: string, workspaceId: string, allowed: string[],
) {
  const rows = await tx`
    SELECT wm.workspace_role
    FROM enterprise.workspace_memberships wm
    JOIN enterprise.workspaces w
      ON w.id=wm.workspace_id AND w.organization_id=wm.organization_id
    JOIN identity.organizations o ON o.id=w.organization_id
    WHERE wm.user_id=${userId}::uuid
      AND wm.organization_id=${orgId}::uuid
      AND wm.workspace_id=${workspaceId}::uuid
      AND wm.membership_status='ACTIVE'
      AND w.workspace_status='ACTIVE'
      AND o.status='ACTIVE'
    LIMIT 1
  `;
  if (!rows.length || !allowed.includes(rows[0].workspace_role)) {
    throw new Error('Workspace authorization denied');
  }
  return rows[0].workspace_role as string;
}

async function listManifests(user: User) {
  return await withServiceRole(async (tx) => await tx`
    SELECT m.provider_key, b.provider_name, m.manifest_version, m.family_key,
      f.family_name, m.auth_method, m.default_scopes,
      jsonb_object_keys(m.operations) AS operation_key
    FROM integration.provider_adapter_manifests m
    JOIN integration.provider_adapter_blueprints b USING (provider_key)
    JOIN integration.adapter_family_blueprints f USING (family_key)
    WHERE m.manifest_status='ACTIVE'
    ORDER BY f.sort_order, b.provider_name, m.manifest_version DESC
  `);
}

async function listConnections(user: User, body: Record<string, unknown>) {
  const orgId = uuid(body.organization_id, 'organization_id');
  const workspaceId = uuid(body.workspace_id, 'workspace_id');
  return await withServiceRole(async (tx) => {
    await requireWorkspaceRole(tx, user.id, orgId, workspaceId, ['OWNER','ADMIN','MEMBER','VIEWER']);
    return await tx`
      SELECT id, organization_id, workspace_id, provider_key, manifest_version,
        connection_key, display_name, auth_method, granted_scopes,
        provider_account_ref, connection_status, safe_metadata,
        last_health_check_at, last_error_code, connected_at, revoked_at,
        created_at, updated_at
      FROM integration.tenant_connections
      WHERE organization_id=${orgId}::uuid AND workspace_id=${workspaceId}::uuid
      ORDER BY created_at DESC
    `;
  });
}

async function createConnection(user: User, body: Record<string, unknown>) {
  const orgId = uuid(body.organization_id, 'organization_id');
  const workspaceId = uuid(body.workspace_id, 'workspace_id');
  const providerKey = requiredString(body.provider_key, 'provider_key', 100);
  const manifestVersion = requiredString(body.manifest_version, 'manifest_version', 40);
  const key = requiredString(body.connection_key, 'connection_key', 96).toLowerCase();
  const name = requiredString(body.display_name, 'display_name', 160);
  if (!/^[a-z0-9][a-z0-9._-]{1,95}$/.test(key)) throw new Error('Invalid connection_key format');

  return await withServiceRole(async (tx) => {
    await requireWorkspaceRole(tx, user.id, orgId, workspaceId, ['OWNER','ADMIN']);
    const manifests = await tx`
      SELECT auth_method FROM integration.provider_adapter_manifests
      WHERE provider_key=${providerKey} AND manifest_version=${manifestVersion}
        AND manifest_status='ACTIVE'
      LIMIT 1
    `;
    if (!manifests.length) throw new Error('Active provider manifest not found');
    const authMethod = manifests[0].auth_method as string;
    const credentials = body.credentials && typeof body.credentials === 'object' && !Array.isArray(body.credentials)
      ? body.credentials as Record<string, unknown> : null;
    let secretJson: string | null = null;

    if (authMethod === 'NONE') {
      if (credentials) throw new Error('This provider manifest does not accept credentials');
    } else if (authMethod === 'BEARER') {
      if (!credentials || typeof credentials.token !== 'string' || !credentials.token.trim()) {
        throw new Error('credentials.token is required for BEARER authentication');
      }
      secretJson = JSON.stringify({ token: credentials.token });
    } else if (authMethod === 'API_KEY_HEADER') {
      if (!credentials || typeof credentials.api_key !== 'string' || !credentials.api_key.trim()) {
        throw new Error('credentials.api_key is required for API_KEY_HEADER authentication');
      }
      secretJson = JSON.stringify({ api_key: credentials.api_key });
    } else if (authMethod === 'BASIC') {
      if (!credentials || typeof credentials.username !== 'string' || !credentials.username.trim() ||
          typeof credentials.password !== 'string' || !credentials.password) {
        throw new Error('credentials.username and credentials.password are required for BASIC authentication');
      }
      secretJson = JSON.stringify({ username: credentials.username, password: credentials.password });
    } else {
      throw new Error('OAuth credential provisioning requires the OAuth callback lifecycle and is not enabled yet');
    }

    const existing = await tx`
      SELECT id,organization_id,workspace_id,provider_key,manifest_version,
        connection_key,display_name,auth_method,connection_status,secret_id,created_at
      FROM integration.tenant_connections
      WHERE workspace_id=${workspaceId}::uuid AND connection_key=${key}
      LIMIT 1
    `;
    if (existing.length) {
      const current = existing[0];
      if (current.organization_id !== orgId || current.provider_key !== providerKey ||
          current.manifest_version !== manifestVersion || current.display_name !== name) {
        throw new Error('connection_key already exists with a different payload');
      }
      if (current.connection_status === 'REVOKED') {
        throw new Error('Revoked connection keys cannot be reused; create a new connection_key');
      }
      if (secretJson && !current.secret_id) {
        const secret = await tx`
          SELECT vault.create_secret(
            ${secretJson},
            ${'aspace-adapter-' + orgId + '-' + workspaceId + '-' + key},
            ${'Aspace Marketplace provider credential reference; tenant-scoped'},
            NULL
          ) AS id
        `;
        await tx`
          UPDATE integration.tenant_connections
          SET secret_id=${secret[0].id}::uuid, updated_at=now()
          WHERE id=${current.id}::uuid
        `;
      }
      const safe = await tx`
        SELECT id,organization_id,workspace_id,provider_key,manifest_version,
          connection_key,display_name,auth_method,connection_status,created_at
        FROM integration.tenant_connections WHERE id=${current.id}::uuid
      `;
      return safe[0];
    }

    let secretId: string | null = null;
    if (secretJson) {
      const secret = await tx`
        SELECT vault.create_secret(
          ${secretJson},
          ${'aspace-adapter-' + orgId + '-' + workspaceId + '-' + key},
          ${'Aspace Marketplace provider credential reference; tenant-scoped'},
          NULL
        ) AS id
      `;
      secretId = secret[0].id;
    }
    const rows = await tx`
      INSERT INTO integration.tenant_connections
        (organization_id,workspace_id,provider_key,manifest_version,connection_key,
         display_name,auth_method,secret_id,connection_status,created_by_user_id)
      VALUES
        (${orgId}::uuid,${workspaceId}::uuid,${providerKey},${manifestVersion},${key},
         ${name},${authMethod},${secretId}::uuid,'PENDING_AUTH',${user.id}::uuid)
      RETURNING id,organization_id,workspace_id,provider_key,manifest_version,
        connection_key,display_name,auth_method,connection_status,created_at
    `;
    return rows[0];
  });
}

async function revokeConnection(user: User, body: Record<string, unknown>) {
  const orgId = uuid(body.organization_id, 'organization_id');
  const workspaceId = uuid(body.workspace_id, 'workspace_id');
  const connectionId = uuid(body.connection_id, 'connection_id');
  return await withServiceRole(async (tx) => {
    await requireWorkspaceRole(tx, user.id, orgId, workspaceId, ['OWNER','ADMIN']);
    const rows = await tx`
      UPDATE integration.tenant_connections
      SET connection_status='REVOKED', revoked_at=coalesce(revoked_at,now()), updated_at=now()
      WHERE id=${connectionId}::uuid AND organization_id=${orgId}::uuid
        AND workspace_id=${workspaceId}::uuid
      RETURNING id,organization_id,workspace_id,provider_key,connection_key,connection_status,revoked_at
    `;
    if (!rows.length) throw new Error('Active connection not found');
    const cancelled = await tx`
      UPDATE integration.adapter_execution_jobs
      SET job_status='CANCELLED', completed_at=now(), updated_at=now(),
          error_code='CONNECTION_REVOKED', error_message='Connection revoked by workspace administrator'
      WHERE connection_id=${connectionId}::uuid
        AND job_status IN ('QUEUED','RETRY_WAIT')
      RETURNING id,organization_id,workspace_id,attempt_count
    `;
    for (const job of cancelled) {
      await tx`
        INSERT INTO integration.adapter_execution_events
          (job_id,organization_id,workspace_id,event_type,event_payload)
        VALUES (${job.id}::uuid,${job.organization_id}::uuid,${job.workspace_id}::uuid,
          'CANCELLED',${JSON.stringify({ reason: 'CONNECTION_REVOKED', attempt: job.attempt_count })}::jsonb)
      `;
    }
    return { connection: rows[0], cancelled_jobs: cancelled.length };
  });
}

async function testConnection(user: User, body: Record<string, unknown>) {
  const orgId = uuid(body.organization_id, 'organization_id');
  const workspaceId = uuid(body.workspace_id, 'workspace_id');
  const connectionId = uuid(body.connection_id, 'connection_id');
  const idempotencyKey = requiredString(body.idempotency_key, 'idempotency_key', 200);
  if (idempotencyKey.length < 8) throw new Error('idempotency_key must contain at least 8 characters');

  const result = await withServiceRole(async (tx) => {
    await requireWorkspaceRole(tx, user.id, orgId, workspaceId, ['OWNER','ADMIN']);
    const connections = await tx`
      SELECT c.id,c.connection_status,m.operations
      FROM integration.tenant_connections c
      JOIN integration.provider_adapter_manifests m
        ON m.provider_key=c.provider_key AND m.manifest_version=c.manifest_version
      WHERE c.id=${connectionId}::uuid AND c.organization_id=${orgId}::uuid
        AND c.workspace_id=${workspaceId}::uuid AND m.manifest_status='ACTIVE'
      LIMIT 1
    `;
    if (!connections.length) throw new Error('Tenant connection or active manifest not found');
    if (!['PENDING_AUTH','DEGRADED','ERROR'].includes(connections[0].connection_status)) {
      throw new Error('Connection is not in a testable state');
    }
    if (!connections[0].operations || !Object.prototype.hasOwnProperty.call(connections[0].operations,'health_check')) {
      throw new Error('Provider manifest does not declare health_check');
    }
    const jobs = await tx`
      INSERT INTO integration.adapter_execution_jobs
        (organization_id,workspace_id,connection_id,provider_key,manifest_version,
         operation_key,idempotency_key,request_payload,created_by_user_id)
      SELECT c.organization_id,c.workspace_id,c.id,c.provider_key,c.manifest_version,
        'health_check',${idempotencyKey},'{}'::jsonb,${user.id}::uuid
      FROM integration.tenant_connections c
      WHERE c.id=${connectionId}::uuid
      ON CONFLICT (connection_id,idempotency_key) DO NOTHING
      RETURNING id,organization_id,workspace_id,connection_id,operation_key,
        job_status,attempt_count,max_attempts,correlation_id,created_at
    `;
    if (jobs.length) {
      await tx`
        INSERT INTO integration.adapter_execution_events
          (job_id,organization_id,workspace_id,event_type,event_payload)
        VALUES (${jobs[0].id}::uuid,${orgId}::uuid,${workspaceId}::uuid,
          'ENQUEUED','{"operation_key":"health_check"}'::jsonb)
      `;
      return jobs[0];
    }
    const previous = await tx`
      SELECT id,organization_id,workspace_id,connection_id,operation_key,
        job_status,attempt_count,max_attempts,correlation_id,created_at
      FROM integration.adapter_execution_jobs
      WHERE connection_id=${connectionId}::uuid AND idempotency_key=${idempotencyKey}
      LIMIT 1
    `;
    if (!previous.length || previous[0].operation_key !== 'health_check') {
      throw new Error('Idempotency key already used for another operation');
    }
    return previous[0];
  });
  await dispatchWorker();
  return result;
}

async function enqueueExecution(user: User, body: Record<string, unknown>) {
  const orgId = uuid(body.organization_id, 'organization_id');
  const workspaceId = uuid(body.workspace_id, 'workspace_id');
  const connectionId = uuid(body.connection_id, 'connection_id');
  const operationKey = requiredString(body.operation_key, 'operation_key', 96);
  const idempotencyKey = requiredString(body.idempotency_key, 'idempotency_key', 200);
  if (body.request_payload !== undefined &&
      (!body.request_payload || typeof body.request_payload !== 'object' || Array.isArray(body.request_payload))) {
    throw new Error('request_payload must be a JSON object');
  }
  const payload = (body.request_payload ?? {}) as Record<string, unknown>;
  const payloadJson = JSON.stringify(payload);
  if (payloadJson.length > 65536) throw new Error('request_payload exceeds 64 KB');
  if (idempotencyKey.length < 8) throw new Error('idempotency_key must contain at least 8 characters');
  if (!/^[a-z][a-z0-9._-]{1,95}$/.test(operationKey)) throw new Error('Invalid operation_key');

  return await withServiceRole(async (tx) => {
    await requireWorkspaceRole(tx, user.id, orgId, workspaceId, ['OWNER','ADMIN','MEMBER']);
    const rows = await tx`
      SELECT c.provider_key,c.manifest_version,m.operations
      FROM integration.tenant_connections c
      JOIN integration.provider_adapter_manifests m
        ON m.provider_key=c.provider_key AND m.manifest_version=c.manifest_version
      WHERE c.id=${connectionId}::uuid AND c.organization_id=${orgId}::uuid
        AND c.workspace_id=${workspaceId}::uuid
        AND c.connection_status='CONNECTED' AND m.manifest_status='ACTIVE'
      LIMIT 1
    `;
    if (!rows.length) throw new Error('Connected tenant adapter not found');
    if (!rows[0].operations || !Object.prototype.hasOwnProperty.call(rows[0].operations, operationKey)) {
      throw new Error('Operation is not declared by the active provider manifest');
    }
    const inserted = await tx`
      INSERT INTO integration.adapter_execution_jobs
        (organization_id,workspace_id,connection_id,provider_key,manifest_version,
         operation_key,idempotency_key,request_payload,created_by_user_id)
      VALUES
        (${orgId}::uuid,${workspaceId}::uuid,${connectionId}::uuid,${rows[0].provider_key},
         ${rows[0].manifest_version},${operationKey},${idempotencyKey},
         ${JSON.stringify(payload)}::jsonb,${user.id}::uuid)
      ON CONFLICT (connection_id,idempotency_key) DO NOTHING
      RETURNING id,organization_id,workspace_id,connection_id,provider_key,
        manifest_version,operation_key,idempotency_key,job_status,attempt_count,
        max_attempts,correlation_id,created_at
    `;
    if (inserted.length) {
      await tx`
        INSERT INTO integration.adapter_execution_events
          (job_id,organization_id,workspace_id,event_type,event_payload)
        VALUES (${inserted[0].id}::uuid,${orgId}::uuid,${workspaceId}::uuid,
          'ENQUEUED',${JSON.stringify({ operation_key: operationKey })}::jsonb)
      `;
      await dispatchWorker();
      return inserted[0];
    }
    const existing = await tx`
      SELECT id,organization_id,workspace_id,connection_id,provider_key,
        manifest_version,operation_key,idempotency_key,request_payload,job_status,
        attempt_count,max_attempts,correlation_id,created_at,
        (request_payload=${payloadJson}::jsonb) AS payload_matches
      FROM integration.adapter_execution_jobs
      WHERE connection_id=${connectionId}::uuid AND idempotency_key=${idempotencyKey}
      LIMIT 1
    `;
    if (!existing.length || existing[0].operation_key !== operationKey || !existing[0].payload_matches) {
      throw new Error('Idempotency key already used with a different execution payload');
    }
    const { request_payload: _discard, ...safe } = existing[0];
    return safe;
  });
}

async function listExecutions(user: User, body: Record<string, unknown>) {
  const orgId = uuid(body.organization_id, 'organization_id');
  const workspaceId = uuid(body.workspace_id, 'workspace_id');
  return await withServiceRole(async (tx) => {
    await requireWorkspaceRole(tx, user.id, orgId, workspaceId, ['OWNER','ADMIN','MEMBER','VIEWER']);
    return await tx`
      SELECT id,connection_id,provider_key,manifest_version,operation_key,
        job_status,attempt_count,max_attempts,scheduled_at,correlation_id,
        error_code,created_at,started_at,completed_at
      FROM integration.adapter_execution_jobs
      WHERE organization_id=${orgId}::uuid AND workspace_id=${workspaceId}::uuid
      ORDER BY created_at DESC LIMIT 100
    `;
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });
  if (req.method !== 'POST') return response({ error: 'Method not allowed' }, 405);
  try {
    const user = await authenticate(req);
    const body = await req.json() as Record<string, unknown>;
    const action = requiredString(body.action, 'action', 60);
    let data: unknown;
    switch (action) {
      case 'list_manifests': data = await listManifests(user); break;
      case 'list_connections': data = await listConnections(user, body); break;
      case 'create_connection': data = await createConnection(user, body); break;
      case 'test_connection': data = await testConnection(user, body); break;
      case 'revoke_connection': data = await revokeConnection(user, body); break;
      case 'enqueue_execution': data = await enqueueExecution(user, body); break;
      case 'list_executions': data = await listExecutions(user, body); break;
      default: return response({ error: 'Unknown action', action }, 404);
    }
    return response({ data, actor_user_id: user.id });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const status = message.includes('Authentication') || message.includes('session') ? 401
      : message.includes('authorization denied') ? 403 : 400;
    console.error('adapter-api', message);
    return response({ error: message }, status);
  }
});
