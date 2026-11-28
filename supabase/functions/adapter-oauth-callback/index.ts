import postgres from 'npm:postgres@3.4.5';

const dbUrl = Deno.env.get('SUPABASE_DB_URL') ?? '';
if (!dbUrl) throw new Error('Private database environment is missing');
const db = postgres(dbUrl,{ max: 1, prepare: false });

function response(status: number, message: string) {
  return new Response(message,{status,headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'}});
}
function envSuffix(providerKey: string): string {
  return providerKey.toUpperCase().replace(/[^A-Z0-9]/g,'_');
}
function validateEndpoint(value: unknown, hosts: unknown): URL {
  if (typeof value !== 'string' || !Array.isArray(hosts) ||
      !hosts.every((host) => typeof host === 'string')) throw new Error('OAUTH_MANIFEST_INVALID');
  const endpoint = new URL(value);
  const normalizedHosts=hosts.map((host:string)=>host.toLowerCase());
  if (endpoint.protocol !== 'https:' || endpoint.username || endpoint.password ||
      endpoint.search || endpoint.hash || !normalizedHosts.includes(endpoint.hostname.toLowerCase())) {
    throw new Error('OAUTH_ENDPOINT_NOT_ALLOWED');
  }
  return endpoint;
}
async function withServiceRole<T>(work: (tx: any) => Promise<T>): Promise<T> {
  return await db.begin(async (tx) => {
    await tx`SET LOCAL ROLE service_role`;
    return await work(tx);
  });
}
async function digestHex(value: string): Promise<string> {
  const bytes = new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)));
  return Array.from(bytes).map((b) => b.toString(16).padStart(2,'0')).join('');
}
async function readLimited(res: Response,maxBytes=65536): Promise<string> {
  if (!res.body) return '';
  const reader=res.body.getReader(),chunks:Uint8Array[]=[];
  let total=0;
  while(true) {
    const {done,value}=await reader.read();
    if(done || !value) break;
    if(total+value.byteLength>maxBytes) { await reader.cancel(); throw new Error('OAUTH_TOKEN_RESPONSE_TOO_LARGE'); }
    chunks.push(value); total+=value.byteLength;
  }
  const out=new Uint8Array(total); let offset=0;
  for(const chunk of chunks){out.set(chunk,offset);offset+=chunk.byteLength;}
  return new TextDecoder().decode(out);
}
async function failTransaction(transactionId: string,pkceSecretId: string | null) {
  await withServiceRole(async (tx) => {
    await tx`
      UPDATE integration.adapter_oauth_transactions
      SET transaction_status='FAILED'
      WHERE id=${transactionId}::uuid AND transaction_status='PROCESSING'
    `;
    if(pkceSecretId) await tx`DELETE FROM vault.secrets WHERE id=${pkceSecretId}::uuid`;
  });
}

Deno.serve(async (req: Request) => {
  if(req.method!=='GET') return response(405,'Method not allowed');
  const url=new URL(req.url);
  const state=url.searchParams.get('state') ?? '';
  const code=url.searchParams.get('code') ?? '';
  const providerError=url.searchParams.get('error');
  if(!/^[A-Za-z0-9_-]{43}$/.test(state)) return response(400,'Invalid or expired authorization response. You may close this window.');
  const digest=await digestHex(state);
  let txn:any;
  try {
    txn=await withServiceRole(async (tx) => {
      const rows=await tx`
        UPDATE integration.adapter_oauth_transactions
        SET transaction_status='PROCESSING',consumed_at=now()
        WHERE state_digest=decode(${digest},'hex')
          AND transaction_status='PENDING' AND expires_at>now()
        RETURNING id,organization_id,workspace_id,provider_key,manifest_version,
          connection_id,pkce_secret_id,redirect_uri
      `;
      if(rows.length) return rows[0];
      await tx`
        UPDATE integration.adapter_oauth_transactions
        SET transaction_status='EXPIRED'
        WHERE state_digest=decode(${digest},'hex')
          AND transaction_status='PENDING' AND expires_at<=now()
      `;
      return null;
    });
    if(!txn) return response(400,'Invalid, expired, or already-used authorization response. You may close this window.');
    if(providerError || !code || code.length>4096) {
      await failTransaction(txn.id,txn.pkce_secret_id);
      return response(400,'Authorization was not completed. You may close this window and restart the connection flow.');
    }

    const context=await withServiceRole(async (tx) => {
      const rows=await tx`
        SELECT m.auth_config,m.default_scopes,m.auth_method,c.connection_status,
          s.decrypted_secret
        FROM integration.provider_adapter_manifests m
        JOIN integration.tenant_connections c
          ON c.provider_key=m.provider_key AND c.manifest_version=m.manifest_version
        LEFT JOIN vault.decrypted_secrets s ON s.id=${txn.pkce_secret_id}::uuid
        WHERE m.provider_key=${txn.provider_key} AND m.manifest_version=${txn.manifest_version}
          AND c.id=${txn.connection_id}::uuid AND c.organization_id=${txn.organization_id}::uuid
          AND c.workspace_id=${txn.workspace_id}::uuid AND m.manifest_status='ACTIVE'
        LIMIT 1
      `;
      if(!rows.length || rows[0].auth_method!=='OAUTH2_AUTH_CODE' ||
          rows[0].connection_status==='REVOKED' || typeof rows[0].decrypted_secret!=='string') {
        throw new Error('OAUTH_TRANSACTION_CONTEXT_INVALID');
      }
      return rows[0];
    });
    const config=context.auth_config ?? {};
    const tokenEndpoint=validateEndpoint(config.token_url,config.oauth_allowed_hosts);
    const suffix=envSuffix(txn.provider_key);
    const clientId=Deno.env.get('OAUTH_'+suffix+'_CLIENT_ID') ?? '';
    const clientSecret=Deno.env.get('OAUTH_'+suffix+'_CLIENT_SECRET') ?? '';
    if(!clientId || !clientSecret) throw new Error('OAUTH_CLIENT_CONFIGURATION_MISSING');
    const pkce=JSON.parse(context.decrypted_secret);
    if(typeof pkce.verifier!=='string' || pkce.verifier.length<43) throw new Error('OAUTH_PKCE_VERIFIER_INVALID');

    const form=new URLSearchParams({
      grant_type:'authorization_code',code,client_id:clientId,client_secret:clientSecret,
      redirect_uri:txn.redirect_uri,code_verifier:pkce.verifier,
    });
    const tokenResponse=await fetch(tokenEndpoint,{
      method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'},
      body:form,signal:AbortSignal.timeout(15000),redirect:'error',
    });
    const raw=await readLimited(tokenResponse);
    if(!tokenResponse.ok) throw new Error('OAUTH_TOKEN_EXCHANGE_REJECTED');
    let tokens:any;
    try { tokens=JSON.parse(raw); } catch { throw new Error('OAUTH_TOKEN_RESPONSE_INVALID'); }
    if(!tokens || typeof tokens.access_token!=='string' || !tokens.access_token ||
       tokens.access_token.length>8192 || String(tokens.token_type ?? '').toLowerCase()!=='bearer') {
      throw new Error('OAUTH_TOKEN_RESPONSE_INVALID');
    }
    if(tokens.refresh_token!==undefined &&
       (typeof tokens.refresh_token!=='string' || tokens.refresh_token.length>8192)) {
      throw new Error('OAUTH_REFRESH_TOKEN_INVALID');
    }
    const expiresIn=Number(tokens.expires_in ?? 3600);
    if(!Number.isFinite(expiresIn) || expiresIn<1 || expiresIn>31536000) throw new Error('OAUTH_EXPIRY_INVALID');
    const requested=Array.isArray(context.default_scopes)?context.default_scopes:[];
    const granted=typeof tokens.scope==='string' && tokens.scope.trim()
      ? tokens.scope.trim().split(/\\s+/) : requested;
    if(granted.some((scope:string)=>!requested.includes(scope))) throw new Error('OAUTH_SCOPE_ESCALATION_REJECTED');
    const secretJson=JSON.stringify({
      access_token:tokens.access_token,
      refresh_token:tokens.refresh_token ?? null,
      token_type:'Bearer',
      expires_at:new Date(Date.now()+expiresIn*1000).toISOString(),
      scopes:granted,
    });
    await withServiceRole(async (tx) => {
      const secret=await tx`
        SELECT vault.create_secret(
          ${secretJson},
          ${'aspace-oauth-' + txn.organization_id + '-' + txn.workspace_id + '-' + txn.connection_id},
          'Tenant-scoped OAuth access and refresh tokens',
          NULL
        ) AS id
      `;
      const updated=await tx`
        UPDATE integration.tenant_connections
        SET secret_id=${secret[0].id}::uuid,granted_scopes=${granted}::text[],
          connection_status='PENDING_AUTH',connected_at=NULL,last_health_check_at=NULL,
          last_error_code=NULL,updated_at=now()
        WHERE id=${txn.connection_id}::uuid AND organization_id=${txn.organization_id}::uuid
          AND workspace_id=${txn.workspace_id}::uuid AND connection_status<>'REVOKED'
        RETURNING id
      `;
      if(!updated.length) throw new Error('OAUTH_CONNECTION_REVOKED_DURING_CALLBACK');
      await tx`
        UPDATE integration.adapter_oauth_transactions
        SET transaction_status='COMPLETED'
        WHERE id=${txn.id}::uuid AND transaction_status='PROCESSING'
      `;
      if(txn.pkce_secret_id) await tx`DELETE FROM vault.secrets WHERE id=${txn.pkce_secret_id}::uuid`;
    });
    return response(200,'Authorization received. The connection is awaiting its provider health check. You may close this window.');
  } catch(error) {
    if(txn?.id) {
      try { await failTransaction(txn.id,txn.pkce_secret_id); } catch { /* state remains consumed; no replay */ }
    }
    console.error('adapter-oauth-callback failed',error instanceof Error?error.message:'unknown');
    return response(400,'Authorization could not be completed. Restart the connection flow from A’Space Marketplace.');
  }
});
