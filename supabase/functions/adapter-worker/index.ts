import postgres from 'npm:postgres@3.4.5';

const url = Deno.env.get('SUPABASE_URL') ?? '';
const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '';
const dbUrl = Deno.env.get('SUPABASE_DB_URL') ?? '';
if (!url || !serviceRoleKey || !dbUrl) throw new Error('Required private worker environment is missing');

const db = postgres(dbUrl, { max: 1, prepare: false });
type Job = {
  id: string; organization_id: string; workspace_id: string; connection_id: string;
  provider_key: string; manifest_version: string; operation_key: string;
  request_payload: Record<string, unknown>; attempt_count: number; max_attempts: number;
};

function response(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}
function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
async function withServiceRole<T>(work: (tx: any) => Promise<T>): Promise<T> {
  return await db.begin(async (tx) => {
    await tx`SET LOCAL ROLE service_role`;
    return await work(tx);
  });
}
function sanitize(value: unknown, depth = 0, secretValues: string[] = []): unknown {
  if (depth > 6) return '[DEPTH_LIMIT]';
  if (value === null || typeof value === 'boolean' || typeof value === 'number') return value;
  if (typeof value === 'string') {
    let safe = value;
    for (const secret of secretValues) if (secret.length > 3) safe = safe.split(secret).join('[REDACTED]');
    return safe.length > 8000 ? safe.slice(0,8000) : safe;
  }
  if (Array.isArray(value)) return value.slice(0,100).map((v) => sanitize(v,depth+1,secretValues));
  if (typeof value === 'object') {
    const out: Record<string, unknown> = {};
    const entries = Object.entries(value as Record<string, unknown>).slice(0,100);
    for (const [key, child] of entries) {
      if (/(token|secret|password|api[_-]?key|authorization|cookie|private[_-]?key)/i.test(key)) {
        out[key] = '[REDACTED]';
      } else {
        out[key] = sanitize(child,depth+1,secretValues);
      }
    }
    return out;
  }
  return String(value).slice(0,1000);
}
async function readLimited(response: Response, maxBytes = 1_048_576): Promise<Uint8Array> {
  if (!response.body) return new Uint8Array();
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done || !value) break;
    const remaining = maxBytes - total;
    if (remaining <= 0) {
      await reader.cancel();
      break;
    }
    const chunk = value.byteLength > remaining ? value.slice(0,remaining) : value;
    chunks.push(chunk);
    total += chunk.byteLength;
    if (value.byteLength > remaining) {
      await reader.cancel();
      break;
    }
  }
  const output = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { output.set(chunk,offset); offset += chunk.byteLength; }
  return output;
}
function retryDelay(response: Response): number {
  const value = response.headers.get('retry-after');
  if (!value) return 30;
  const seconds = Number(value);
  if (Number.isFinite(seconds)) return Math.max(1,Math.min(3600,Math.floor(seconds)));
  const date = Date.parse(value);
  if (Number.isFinite(date)) return Math.max(1,Math.min(3600,Math.floor((date-Date.now())/1000)));
  return 30;
}
function safeHeaderName(value: unknown): string {
  if (typeof value !== 'string' || !/^(accept|content-type|x-[a-z0-9-]+)$/i.test(value)) {
    throw new Error('INVALID_MANIFEST_HEADER');
  }
  return value;
}
function buildTarget(baseUrl: string, allowedHosts: string[], path: string): URL {
  if (!path.startsWith('/') || path.includes('..') || path.includes('\\') || /%(?:2e|2f|5c|00)/i.test(path) || path.includes('?') || path.includes('#')) {
    throw new Error('INVALID_MANIFEST_PATH');
  }
  const base = new URL(baseUrl);
  if (base.protocol !== 'https:' || base.username || base.password || base.search || base.hash ||
      !allowedHosts.includes(base.hostname.toLowerCase())) {
    throw new Error('MANIFEST_HOST_NOT_ALLOWED');
  }
  const target = new URL(path,base);
  if (target.protocol !== 'https:' || target.origin !== base.origin ||
      !allowedHosts.includes(target.hostname.toLowerCase())) {
    throw new Error('MANIFEST_TARGET_NOT_ALLOWED');
  }
  return target;
}
async function loadJob(job: Job) {
  return await withServiceRole(async (tx) => {
    const rows = await tx`
      SELECT c.id AS connection_id,c.connection_status,c.auth_method,c.secret_id,
        m.base_url,m.allowed_hosts,m.auth_method AS manifest_auth_method,
        m.auth_config,m.operations,m.timeout_ms,m.manifest_status
      FROM integration.tenant_connections c
      JOIN integration.provider_adapter_manifests m
        ON m.provider_key=c.provider_key AND m.manifest_version=c.manifest_version
      WHERE c.id=${job.connection_id}::uuid
        AND c.organization_id=${job.organization_id}::uuid
        AND c.workspace_id=${job.workspace_id}::uuid
        AND c.provider_key=${job.provider_key}
        AND c.manifest_version=${job.manifest_version}
      LIMIT 1
    `;
    if (!rows.length) throw new Error('CONNECTION_OR_MANIFEST_NOT_FOUND');
    const config = rows[0];
    if (config.manifest_status !== 'ACTIVE') throw new Error('MANIFEST_NOT_ACTIVE');
    if (config.connection_status === 'REVOKED') throw new Error('CONNECTION_REVOKED');
    if (job.operation_key !== 'health_check' && config.connection_status !== 'CONNECTED') {
      throw new Error('CONNECTION_NOT_CONNECTED');
    }
    if (job.operation_key === 'health_check' &&
        !['PENDING_AUTH','DEGRADED','ERROR','CONNECTED'].includes(config.connection_status)) {
      throw new Error('CONNECTION_NOT_TESTABLE');
    }
    const operation = config.operations?.[job.operation_key];
    if (!operation || typeof operation !== 'object') throw new Error('OPERATION_NOT_DECLARED');
    let secret: Record<string, unknown> | null = null;
    if (config.manifest_auth_method !== 'NONE') {
      if (!config.secret_id) throw new Error('CREDENTIAL_REFERENCE_MISSING');
      const secrets = await tx`
        SELECT decrypted_secret FROM vault.decrypted_secrets
        WHERE id=${config.secret_id}::uuid
        LIMIT 1
      `;
      if (!secrets.length || typeof secrets[0].decrypted_secret !== 'string') {
        throw new Error('VAULT_SECRET_NOT_FOUND');
      }
      try { secret = JSON.parse(secrets[0].decrypted_secret); }
      catch { throw new Error('VAULT_SECRET_FORMAT_INVALID'); }
    }
    return { config, operation, secret };
  });
}

function oauthEnvSuffix(providerKey: string): string {
  return providerKey.toUpperCase().replace(/[^A-Z0-9]/g,'_');
}
function oauthTokenEndpoint(config: any): URL {
  const auth = config.auth_config ?? {};
  const hosts = auth.oauth_allowed_hosts;
  if (typeof auth.token_url !== 'string' || !Array.isArray(hosts) ||
      !hosts.every((host: unknown) => typeof host === 'string')) throw new Error('OAUTH_MANIFEST_INVALID');
  const endpoint = new URL(auth.token_url);
  const normalizedHosts=hosts.map((host: string)=>host.toLowerCase());
  if (endpoint.protocol !== 'https:' || endpoint.username || endpoint.password ||
      endpoint.search || endpoint.hash || !normalizedHosts.includes(endpoint.hostname.toLowerCase())) {
    throw new Error('OAUTH_ENDPOINT_NOT_ALLOWED');
  }
  return endpoint;
}
async function refreshOAuthSecret(job: Job, config: any): Promise<Record<string, unknown>> {
  return await db.begin(async (tx) => {
    await tx`SET LOCAL ROLE service_role`;
    await tx`SELECT pg_advisory_xact_lock(hashtextextended(${job.connection_id},0))`;
    const rows = await tx`
      SELECT c.secret_id,s.decrypted_secret
      FROM integration.tenant_connections c
      JOIN vault.decrypted_secrets s ON s.id=c.secret_id
      WHERE c.id=${job.connection_id}::uuid
        AND c.organization_id=${job.organization_id}::uuid
        AND c.workspace_id=${job.workspace_id}::uuid
        AND c.connection_status<>'REVOKED'
      LIMIT 1
    `;
    if (!rows.length || typeof rows[0].decrypted_secret !== 'string') throw new Error('OAUTH_CREDENTIAL_REFERENCE_MISSING');
    let current: Record<string, unknown>;
    try { current = JSON.parse(rows[0].decrypted_secret); } catch { throw new Error('OAUTH_CREDENTIAL_FORMAT_INVALID'); }
    const expiresAt = typeof current.expires_at === 'string' ? Date.parse(current.expires_at) : 0;
    if (typeof current.access_token === 'string' && expiresAt > Date.now()+60000) return current;
    if (typeof current.refresh_token !== 'string' || !current.refresh_token) throw new Error('OAUTH_REAUTH_REQUIRED');
    const endpoint = oauthTokenEndpoint(config);
    const suffix = oauthEnvSuffix(job.provider_key);
    const clientId = Deno.env.get('OAUTH_'+suffix+'_CLIENT_ID') ?? '';
    const clientSecret = Deno.env.get('OAUTH_'+suffix+'_CLIENT_SECRET') ?? '';
    if (!clientId || !clientSecret) throw new Error('OAUTH_CLIENT_CONFIGURATION_MISSING');
    const form = new URLSearchParams({
      grant_type:'refresh_token',refresh_token:current.refresh_token,
      client_id:clientId,client_secret:clientSecret,
    });
    const upstream = await fetch(endpoint,{
      method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'},
      body:form,signal:AbortSignal.timeout(15000),redirect:'error',
    });
    const bytes = await readLimited(upstream,65536);
    if (!upstream.ok) throw new Error('OAUTH_REAUTH_REQUIRED');
    let tokens: any;
    try { tokens=JSON.parse(new TextDecoder().decode(bytes)); } catch { throw new Error('OAUTH_REFRESH_RESPONSE_INVALID'); }
    if (!tokens || typeof tokens.access_token!=='string' || !tokens.access_token ||
        tokens.access_token.length>8192 || String(tokens.token_type ?? 'Bearer').toLowerCase()!=='bearer') {
      throw new Error('OAUTH_REFRESH_RESPONSE_INVALID');
    }
    const expiresIn=Number(tokens.expires_in ?? 3600);
    if (!Number.isFinite(expiresIn) || expiresIn<1 || expiresIn>31536000) throw new Error('OAUTH_EXPIRY_INVALID');
    const nextScopes = typeof tokens.scope==='string' && tokens.scope.trim()
      ? tokens.scope.trim().split(/\\s+/) : (Array.isArray(current.scopes)?current.scopes:[]);
    const allowedScopes = Array.isArray(current.scopes)?current.scopes:[];
    if (nextScopes.some((scope: string)=>!allowedScopes.includes(scope))) throw new Error('OAUTH_SCOPE_ESCALATION_REJECTED');
    const next = {
      access_token:tokens.access_token,
      refresh_token:typeof tokens.refresh_token==='string' && tokens.refresh_token ? tokens.refresh_token : current.refresh_token,
      token_type:'Bearer',
      expires_at:new Date(Date.now()+expiresIn*1000).toISOString(),
      scopes:nextScopes,
    };
    await tx`
      SELECT vault.update_secret(
        ${rows[0].secret_id}::uuid,${JSON.stringify(next)},
        ${'aspace-oauth-' + job.organization_id + '-' + job.workspace_id + '-' + job.connection_id},
        'Tenant-scoped OAuth access and refresh tokens',NULL
      )
    `;
    return next;
  });
}

function buildHeaders(config: any, operation: any, secret: Record<string, unknown> | null): Headers {
  const headers = new Headers();
  headers.set('Accept','application/json');
  const staticHeaders = operation.headers && typeof operation.headers === 'object' ? operation.headers : {};
  for (const [key,value] of Object.entries(staticHeaders)) {
    if (typeof value !== 'string') throw new Error('INVALID_MANIFEST_HEADER_VALUE');
    if (/(authorization|cookie|token|secret|api[_-]?key|password)/i.test(key)) {
      throw new Error('SENSITIVE_STATIC_HEADER_FORBIDDEN');
    }
    headers.set(safeHeaderName(key),value);
  }
  const authConfig = config.auth_config ?? {};
  switch (config.manifest_auth_method) {
    case 'NONE': break;
    case 'BEARER': {
      const token = secret?.token;
      if (typeof token !== 'string' || !token) throw new Error('BEARER_TOKEN_MISSING');
      headers.set('Authorization',`Bearer ${token}`);
      break;
    }
    case 'API_KEY_HEADER': {
      const token = secret?.api_key;
      if (typeof token !== 'string' || !token) throw new Error('API_KEY_MISSING');
      const name = safeHeaderName(authConfig.header_name);
      const prefix = typeof authConfig.prefix === 'string' ? authConfig.prefix : '';
      headers.set(name,`${prefix}${token}`);
      break;
    }
    case 'BASIC': {
      const username = secret?.username, password = secret?.password;
      if (typeof username !== 'string' || typeof password !== 'string') throw new Error('BASIC_CREDENTIALS_MISSING');
      const bytes = new TextEncoder().encode(`${username}:${password}`);
      let binary = '';
      for (const byte of bytes) binary += String.fromCharCode(byte);
      headers.set('Authorization',`Basic ${btoa(binary)}`);
      break;
    }
    case 'OAUTH2_AUTH_CODE': {
      const token = secret?.access_token;
      if (typeof token !== 'string' || !token) throw new Error('OAUTH_ACCESS_TOKEN_MISSING');
      headers.set('Authorization',`Bearer ${token}`);
      break;
    }
    default:
      throw new Error('UNSUPPORTED_AUTH_METHOD');
  }
  return headers;
}
async function execute(job: Job, workerId: string) {
  let isHealthCheck = job.operation_key === 'health_check';
  try {
    const loaded = await loadJob(job);
    const { config, operation } = loaded;
    let secret = loaded.secret;
    if (config.manifest_auth_method === 'OAUTH2_AUTH_CODE') {
      secret = await refreshOAuthSecret(job,config);
    }
    const method = typeof operation.method === 'string' ? operation.method.toUpperCase() : '';
    if (!['GET','POST','PUT','PATCH','DELETE'].includes(method)) throw new Error('INVALID_MANIFEST_METHOD');
    let path = typeof operation.path === 'string' ? operation.path : '';
    const payload: Record<string,unknown> = { ...(job.request_payload ?? {}) };
    const pathParameters = operation.path_parameters ?? [];
    if (!Array.isArray(pathParameters) || !pathParameters.every((name: unknown) =>
        typeof name === 'string' && /^[A-Za-z][A-Za-z0-9_]{0,39}$/.test(name))) {
      throw new Error('INVALID_MANIFEST_PATH_PARAMETERS');
    }
    for (const name of pathParameters as string[]) {
      const placeholder = '{' + name + '}';
      const value = payload[name];
      if (!path.includes(placeholder) || typeof value !== 'string' ||
          !/^[A-Za-z0-9_-]{1,256}$/.test(value)) {
        throw new Error('INVALID_PATH_PARAMETER');
      }
      path = path.replace(placeholder,encodeURIComponent(value));
      delete payload[name];
    }
    if (/[{}]/.test(path)) throw new Error('INVALID_MANIFEST_PATH_PARAMETERS');
    const target = buildTarget(config.base_url,config.allowed_hosts,path);
    const inputMode = operation.input_mode ?? (method === 'GET' || method === 'DELETE' ? 'query' : 'body');
    if (!['query','body','none'].includes(inputMode)) throw new Error('INVALID_MANIFEST_INPUT_MODE');
    if (inputMode === 'query') {
      const allowed = operation.allowed_query_params;
      if (!Array.isArray(allowed) || !allowed.every((name: unknown) =>
          typeof name === 'string' && /^[A-Za-z][A-Za-z0-9_.-]{0,63}$/.test(name))) {
        throw new Error('INVALID_MANIFEST_QUERY_ALLOWLIST');
      }
      const defaults = operation.query_defaults && typeof operation.query_defaults === 'object'
        ? operation.query_defaults : {};
      for (const [key,value] of Object.entries(defaults)) {
        if (!allowed.includes(key)) throw new Error('INVALID_MANIFEST_QUERY_DEFAULT');
        target.searchParams.set(key,typeof value === 'string' ? value : JSON.stringify(value));
      }
      for (const [key,value] of Object.entries(payload)) {
        if (!allowed.includes(key)) throw new Error('QUERY_PARAMETER_NOT_ALLOWED');
        target.searchParams.set(key,typeof value === 'string' ? value : JSON.stringify(value));
      }
    }
    const headers = buildHeaders(config,operation,secret);
    let body: string | undefined;
    if (inputMode === 'body') {
      const allowed = operation.allowed_body_fields;
      if (!Array.isArray(allowed) || !allowed.every((name: unknown) =>
          typeof name === 'string' && /^[A-Za-z][A-Za-z0-9_.-]{0,63}$/.test(name))) {
        throw new Error('INVALID_MANIFEST_BODY_ALLOWLIST');
      }
      const defaults = operation.body_defaults && typeof operation.body_defaults === 'object'
        ? operation.body_defaults : {};
      for (const key of Object.keys(payload)) if (!allowed.includes(key)) {
        throw new Error('BODY_FIELD_NOT_ALLOWED');
      }
      for (const key of Object.keys(defaults)) if (!allowed.includes(key)) {
        throw new Error('INVALID_MANIFEST_BODY_DEFAULT');
      }
      headers.set('Content-Type','application/json');
      body = JSON.stringify({ ...payload, ...defaults });
    } else if (inputMode === 'none' && Object.keys(payload).length) {
      throw new Error('REQUEST_PAYLOAD_NOT_ALLOWED');
    }
    const timeout = Math.max(1000,Math.min(120000,Number(config.timeout_ms)||30000));
    const upstream = await fetch(target,{
      method,headers,body,signal:AbortSignal.timeout(timeout),redirect:'error',
    });
    const bytes = await readLimited(upstream);
    const contentType = upstream.headers.get('content-type') ?? '';
    let data: unknown = null;
    if (contentType.toLowerCase().includes('application/json') && bytes.byteLength) {
      const secretValues = Object.values(secret ?? {}).filter((value): value is string => typeof value === 'string');
      try { data = sanitize(JSON.parse(new TextDecoder().decode(bytes)),0,secretValues); }
      catch { data = { body_omitted: true, reason: 'invalid_json_response', bytes: bytes.byteLength }; }
    } else if (bytes.byteLength) {
      data = { body_omitted: true, reason: 'non_json_response', bytes: bytes.byteLength };
    }
    if (upstream.status >= 200 && upstream.status < 300) {
      const finished = await withServiceRole(async (tx) => {
        const rows = await tx`
          SELECT * FROM api.finish_adapter_execution_job(
            ${job.id}::uuid,${workerId},'SUCCEEDED',
            ${JSON.stringify({ http_status: upstream.status, content_type: contentType, data })}::jsonb,
            NULL,NULL,30
          )
        `;
        if (isHealthCheck) {
          await tx`
            UPDATE integration.tenant_connections
            SET connection_status='CONNECTED',connected_at=coalesce(connected_at,now()),
                last_health_check_at=now(),last_error_code=NULL,updated_at=now()
            WHERE id=${job.connection_id}::uuid
          `;
        }
        return rows[0];
      });
      return { status: finished.job_status };
    }
    const retryable = upstream.status === 429 || upstream.status >= 500;
    const outcome = retryable ? 'RETRY_WAIT' : 'FAILED';
    const code = retryable ? 'UPSTREAM_RETRYABLE' : 'UPSTREAM_REJECTED';
    const finished = await withServiceRole(async (tx) => {
      const rows = await tx`
        SELECT * FROM api.finish_adapter_execution_job(
          ${job.id}::uuid,${workerId},${outcome},
          NULL,${code},${'Provider returned HTTP ' + upstream.status},${retryDelay(upstream)}
        )
      `;
      if (isHealthCheck && rows[0]?.job_status === 'FAILED') {
        await tx`
          UPDATE integration.tenant_connections
          SET connection_status='ERROR',last_health_check_at=now(),
              last_error_code=${code},updated_at=now()
          WHERE id=${job.connection_id}::uuid
        `;
      }
      return rows[0];
    });
    return { status: finished.job_status };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'WORKER_EXECUTION_ERROR';
    const retryable = ['CONNECTION_NOT_CONNECTED','CONNECTION_REVOKED','MANIFEST_NOT_ACTIVE',
      'OPERATION_NOT_DECLARED','INVALID_MANIFEST_PATH','MANIFEST_HOST_NOT_ALLOWED',
      'MANIFEST_TARGET_NOT_ALLOWED','INVALID_MANIFEST_METHOD','INVALID_MANIFEST_INPUT_MODE',
      'INVALID_MANIFEST_HEADER','INVALID_MANIFEST_HEADER_VALUE','SENSITIVE_STATIC_HEADER_FORBIDDEN',
      'INVALID_MANIFEST_PATH_PARAMETERS','INVALID_PATH_PARAMETER','INVALID_MANIFEST_QUERY_ALLOWLIST',
      'INVALID_MANIFEST_QUERY_DEFAULT','QUERY_PARAMETER_NOT_ALLOWED','INVALID_MANIFEST_BODY_ALLOWLIST',
      'BODY_FIELD_NOT_ALLOWED','INVALID_MANIFEST_BODY_DEFAULT','REQUEST_PAYLOAD_NOT_ALLOWED','OAUTH_REAUTH_REQUIRED','OAUTH_ENDPOINT_NOT_ALLOWED','OAUTH_MANIFEST_INVALID',
      'OAUTH_CLIENT_CONFIGURATION_MISSING','OAUTH_CREDENTIAL_REFERENCE_MISSING','OAUTH_CREDENTIAL_FORMAT_INVALID',
      'OAUTH_ACCESS_TOKEN_MISSING','OAUTH_TOKEN_RESPONSE_INVALID','OAUTH_REFRESH_RESPONSE_INVALID',
      'OAUTH_EXPIRY_INVALID','OAUTH_SCOPE_ESCALATION_REJECTED',
      'CREDENTIAL_REFERENCE_MISSING','VAULT_SECRET_NOT_FOUND','VAULT_SECRET_FORMAT_INVALID',
      'BEARER_TOKEN_MISSING','API_KEY_MISSING','BASIC_CREDENTIALS_MISSING'].includes(message) ? false : true;
    try {
      const finished = await withServiceRole(async (tx) => {
        const rows = await tx`
          SELECT * FROM api.finish_adapter_execution_job(
            ${job.id}::uuid,${workerId},${retryable ? 'RETRY_WAIT' : 'FAILED'},
            NULL,${message.replace(/[^A-Z0-9_]/gi,'_').toUpperCase().slice(0,80)},
            ${retryable ? 'Provider execution failed; details withheld' : 'Provider manifest or connection validation failed'},
            30
          )
        `;
        if (isHealthCheck && rows[0]?.job_status === 'FAILED') {
          await tx`
            UPDATE integration.tenant_connections
            SET connection_status='ERROR',last_health_check_at=now(),
                last_error_code=${rows[0].error_code},updated_at=now()
            WHERE id=${job.connection_id}::uuid
          `;
        } else if (message === 'OAUTH_REAUTH_REQUIRED') {
          await tx`
            UPDATE integration.tenant_connections
            SET connection_status='ERROR',last_error_code='OAUTH_REAUTH_REQUIRED',updated_at=now()
            WHERE id=${job.connection_id}::uuid AND connection_status<>'REVOKED'
          `;
        }
        return rows[0];
      });
      return { status: finished.job_status };
    } catch {
      console.error('adapter-worker could not finalize a leased job');
      return { status: 'LEASE_FINALIZATION_FAILED' };
    }
  }
}

Deno.serve(async (req: Request) => {
  if (req.method !== 'POST') return response({ error: 'Method not allowed' },405);
  const authorization = req.headers.get('Authorization') ?? '';
  if (!safeEqual(authorization,`Bearer ${serviceRoleKey}`)) {
    return response({ error: 'Unauthorized' },401);
  }
  try {
    const workerId = `adapter-worker:${crypto.randomUUID()}`;
    let claimed = 0, succeeded = 0, failed = 0, retrying = 0;
    for (let batch = 0; batch < 5; batch++) {
      const jobs = await withServiceRole(async (tx) =>
        await tx`SELECT * FROM api.claim_adapter_execution_jobs(${workerId},10)`
      );
      claimed += jobs.length;
      for (const job of jobs as Job[]) {
        const result = await execute(job,workerId);
        if (result.status === 'SUCCEEDED') succeeded++;
        else if (result.status === 'RETRY_WAIT') retrying++;
        else failed++;
      }
      if (jobs.length < 10) break;
    }
    return response({ claimed, succeeded, failed, retrying });
  } catch (error) {
    console.error('adapter-worker run failed',error instanceof Error ? error.message : 'unknown error');
    return response({ error: 'Worker execution failed' },500);
  }
});
