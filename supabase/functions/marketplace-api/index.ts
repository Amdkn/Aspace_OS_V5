import { createClient } from 'npm:@supabase/supabase-js@2.95.0';
import postgres from 'npm:postgres@3.4.5';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
const url = Deno.env.get('SUPABASE_URL') ?? '';
const anonKey = Deno.env.get('SUPABASE_ANON_KEY') ?? '';
const dbUrl = Deno.env.get('SUPABASE_DB_URL') ?? '';
if (!url || !anonKey || !dbUrl) throw new Error('Required Supabase Edge Function environment is missing');

const authClient = createClient(url, anonKey, { auth: { persistSession: false, autoRefreshToken: false } });
const db = postgres(dbUrl, { max: 1, prepare: false });
type User = { id: string; email?: string };
type Tx = any;

function response(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
}
function requiredString(value: unknown, field: string, max = 200): string {
  if (typeof value !== 'string' || !value.trim() || value.trim() !== value || value.length > max) throw new Error(`Invalid ${field}`);
  return value;
}
async function authenticate(req: Request): Promise<User> {
  const header = req.headers.get('Authorization') ?? '';
  if (!header.startsWith('Bearer ')) throw new Error('Authentication required');
  const { data, error } = await authClient.auth.getUser(header.slice(7));
  if (error || !data.user) throw new Error('Invalid or expired session');
  return { id: data.user.id, email: data.user.email ?? undefined };
}
async function withServiceRole<T>(work: (tx: Tx) => Promise<T>): Promise<T> {
  return await db.begin(async (tx) => {
    await tx`SET LOCAL ROLE service_role`;
    return await work(tx);
  });
}
async function requireOrgRole(tx: Tx, userId: string, orgId: string) {
  const rows = await tx`
    SELECT rb.role_code
    FROM identity.organization_memberships m
    JOIN identity.role_bindings rb
      ON rb.organization_id = m.organization_id AND rb.subject_user_id = m.user_id
    WHERE m.organization_id = ${orgId}::uuid AND m.user_id = ${userId}::uuid
      AND m.membership_status = 'ACTIVE' AND rb.binding_status = 'ACTIVE'
      AND rb.starts_at <= now() AND (rb.expires_at IS NULL OR rb.expires_at > now())
      AND rb.role_code IN ('S0_SOVEREIGN','B1_CEO','A3_PICARD','B2_MANAGER')
    LIMIT 1
  `;
  if (!rows.length) throw new Error('Active organization role required');
}
async function listOrganizations(user: User) {
  return await withServiceRole(async (tx) => await tx`
    SELECT o.id,o.organization_key,o.name,o.organization_type,o.status
    FROM identity.organizations o
    JOIN identity.organization_memberships m ON m.organization_id=o.id
    WHERE m.user_id=${user.id}::uuid AND m.membership_status='ACTIVE'
    ORDER BY o.created_at ASC
  `);
}
async function listAdapterFamilies() {
  return await withServiceRole(async (tx) => {
    return await tx`
      SELECT family_key, family_name, provider_examples, icon_key, sort_order,
        taxonomy_version, implementation_status
      FROM integration.adapter_family_blueprints
      WHERE implementation_status <> 'DEPRECATED'
      ORDER BY sort_order
    `;
  });
}

async function listProviderAdapterBlueprints(familyKey: string | null) {
  return await withServiceRole(async (tx) => {
    if (familyKey) {
      return await tx`
        SELECT p.provider_key, p.family_key, f.family_name, p.provider_name,
          p.manifest_version, p.implementation_status, p.auth_contract_status,
          p.supported_operations, p.documentation_uri
        FROM integration.provider_adapter_blueprints p
        JOIN integration.adapter_family_blueprints f USING (family_key)
        WHERE p.implementation_status <> 'DEPRECATED' AND p.family_key = ${familyKey}
        ORDER BY p.provider_name
      `;
    }
    return await tx`
      SELECT p.provider_key, p.family_key, f.family_name, p.provider_name,
        p.manifest_version, p.implementation_status, p.auth_contract_status,
        p.supported_operations, p.documentation_uri
      FROM integration.provider_adapter_blueprints p
      JOIN integration.adapter_family_blueprints f USING (family_key)
      WHERE p.implementation_status <> 'DEPRECATED'
      ORDER BY f.sort_order, p.provider_name
    `;
  });
}

async function listTaxonomyBlueprints() {
  return await withServiceRole(async (tx) => {
    const areasDomains = await tx`
      SELECT domain_code AS code, domain_name AS name, description, mission AS responsibility,
        sort_order, taxonomy_version
      FROM areas.domain_blueprints
      WHERE status = 'ACTIVE'
      ORDER BY sort_order
    `;
    const businessDepartments = await tx`
      SELECT department_key AS key, department_name AS name, description, mandate AS responsibility,
        sort_order, taxonomy_version
      FROM enterprise.department_blueprints
      WHERE status = 'ACTIVE'
      ORDER BY sort_order
    `;
    return { areas_domains: areasDomains, business_departments: businessDepartments };
  });
}

async function listCapabilities(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    return await tx`
      SELECT c.id,c.capability_key,c.current_version,c.capability_status,
        json_build_object('id',cv.id,'version',cv.version,'name',cv.name) AS version
      FROM catalog.capabilities c
      JOIN LATERAL (
        SELECT id,version,name FROM catalog.capability_versions
        WHERE capability_id=c.id ORDER BY version DESC LIMIT 1
      ) cv ON true
      WHERE c.owner_organization_id=${orgId}::uuid
      ORDER BY c.created_at DESC
    `;
  });
}
async function listOrders(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  return await withServiceRole(async (tx) => {
    const membership = await tx`
      SELECT 1 FROM identity.organization_memberships
      WHERE organization_id=${orgId}::uuid AND user_id=${user.id}::uuid AND membership_status='ACTIVE'
    `;
    if (!membership.length) throw new Error('Active organization membership required');
    return await tx`
      SELECT * FROM commerce.orders
      WHERE buyer_organization_id=${orgId}::uuid OR seller_organization_id=${orgId}::uuid
      ORDER BY created_at DESC LIMIT 100
    `;
  });
}

async function listProviderListings(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    return await tx`
      SELECT id, listing_key, title, description, price_amount, currency,
        listing_status, created_at, published_at
      FROM catalog.listings
      WHERE owner_organization_id=${orgId}::uuid
      ORDER BY created_at DESC
    `;
  });
}
async function createOrganization(user: User, body: Record<string, unknown>) {
  const name = requiredString(body.name, 'name', 160);
  const key = requiredString(body.organization_key, 'organization_key', 64).toUpperCase();
  const type = requiredString(body.organization_type, 'organization_type', 40);
  if (!/^[A-Z0-9][A-Z0-9_-]{2,63}$/.test(key)) throw new Error('Invalid organization_key format');
  const allowed = ['MARKETPLACE_OPERATOR','INTERNAL_VENTURE','EXTERNAL_ENTERPRISE','SUPPLIER','CUSTOMER','PARTNER'];
  if (!allowed.includes(type)) throw new Error('Invalid organization_type');
  return await withServiceRole(async (tx) => {
    const rows = await tx`
      INSERT INTO identity.organizations (organization_key,name,organization_type,created_by_user_id)
      VALUES (${key},${name},${type},${user.id}::uuid)
      RETURNING id,organization_key,name,organization_type,status,created_at
    `;
    const org = rows[0];
    await tx`
      INSERT INTO identity.organization_memberships (organization_id,user_id,membership_status,joined_at)
      VALUES (${org.id}::uuid,${user.id}::uuid,'ACTIVE',now())
    `;
    await tx`
      INSERT INTO identity.role_bindings
        (organization_id,subject_user_id,role_code,scope_type,scope_id,granted_by_user_id)
      VALUES (
        ${org.id}::uuid,${user.id}::uuid,
        ${type === 'MARKETPLACE_OPERATOR' ? 'S0_SOVEREIGN' : 'B1_CEO'},
        'ORGANIZATION',NULL,${user.id}::uuid
      )
    `;
    return org;
  });
}
async function registerAgent(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const agentKey = requiredString(body.agent_key, 'agent_key', 96);
  const displayName = requiredString(body.display_name, 'display_name', 160);
  const agentClass = requiredString(body.agent_class, 'agent_class', 40);
  const runtime = requiredString(body.runtime, 'runtime', 120);
  const scopeType = requiredString(body.scope_type, 'scope_type', 24);
  const scopeId = body.scope_id == null ? null : requiredString(body.scope_id, 'scope_id');
  const permissions = Array.isArray(body.permission_codes) ? body.permission_codes.map((x) => requiredString(x, 'permission_code', 100)) : [];
  if (!permissions.length) throw new Error('At least one permission_code is required');
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    const rows = await tx`
      INSERT INTO identity.agent_principals
        (organization_id,agent_key,display_name,agent_class,runtime,created_by_user_id)
      VALUES (${orgId}::uuid,${agentKey},${displayName},${agentClass},${runtime},${user.id}::uuid)
      RETURNING id,organization_id,agent_key,display_name,agent_class,runtime,principal_status,created_at
    `;
    const agent = rows[0];
    await tx`
      INSERT INTO identity.agent_delegations
        (organization_id,agent_principal_id,delegator_user_id,scope_type,scope_id,permission_codes)
      VALUES (${orgId}::uuid,${agent.id}::uuid,${user.id}::uuid,${scopeType},${scopeId}::uuid,${permissions})
    `;
    return agent;
  });
}
async function createCapability(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const key = requiredString(body.capability_key, 'capability_key', 96).toLowerCase();
  const name = requiredString(body.name, 'name', 160);
  const purpose = requiredString(body.purpose, 'purpose', 2000);
  const input = body.input_contract && typeof body.input_contract === 'object' ? body.input_contract : {};
  const output = body.output_contract && typeof body.output_contract === 'object' ? body.output_contract : {};
  const permissions = Array.isArray(body.permission_codes) ? body.permission_codes.map((x) => requiredString(x, 'permission_code', 100)) : [];
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    const rows = await tx`
      INSERT INTO catalog.capabilities (owner_organization_id,capability_key,created_by_user_id)
      VALUES (${orgId}::uuid,${key},${user.id}::uuid)
      RETURNING id,owner_organization_id,capability_key,current_version,capability_status,created_at
    `;
    const capability = rows[0];
    const versions = await tx`
      INSERT INTO catalog.capability_versions
        (capability_id,version,name,purpose,input_contract,output_contract,permission_codes,created_by_user_id)
      VALUES (${capability.id}::uuid,1,${name},${purpose},${JSON.stringify(input)}::jsonb,${JSON.stringify(output)}::jsonb,${permissions},${user.id}::uuid)
      RETURNING id,capability_id,version,name,purpose,input_contract,output_contract,permission_codes,version_status
    `;
    return { ...capability, version: versions[0] };
  });
}
async function createListing(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const key = requiredString(body.listing_key, 'listing_key', 96).toLowerCase();
  const capabilityId = requiredString(body.capability_id, 'capability_id');
  const versionId = requiredString(body.capability_version_id, 'capability_version_id');
  const title = requiredString(body.title, 'title', 160);
  const description = requiredString(body.description, 'description', 4000);
  const amount = Number(body.price_amount);
  const currency = requiredString(body.currency, 'currency', 3).toUpperCase();
  const criteria = Array.isArray(body.acceptance_criteria) ? body.acceptance_criteria.map((x) => requiredString(x, 'acceptance_criterion', 500)) : [];
  if (!Number.isFinite(amount) || amount < 0 || !/^[A-Z]{3}$/.test(currency) || !criteria.length) throw new Error('Invalid price, currency or acceptance_criteria');
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    const rows = await tx`
      INSERT INTO catalog.listings
        (listing_key,owner_organization_id,capability_id,capability_version_id,version,title,description,price_amount,currency,acceptance_criteria,created_by_user_id)
      SELECT ${key},c.owner_organization_id,c.id,cv.id,1,${title},${description},${amount},${currency},${criteria},${user.id}::uuid
      FROM catalog.capabilities c
      JOIN catalog.capability_versions cv ON cv.capability_id=c.id AND cv.id=${versionId}::uuid
      WHERE c.id=${capabilityId}::uuid AND c.owner_organization_id=${orgId}::uuid
        AND c.capability_status='ACTIVE' AND cv.version_status='ACTIVE'
      RETURNING id,listing_key,owner_organization_id,capability_id,capability_version_id,version,title,description,price_amount,currency,acceptance_criteria,listing_status,created_at
    `;
    if (!rows.length) throw new Error('Active capability version not found for this organization');
    return rows[0];
  });
}
async function publishListing(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const listingId = requiredString(body.listing_id, 'listing_id');
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    const rows = await tx`
      UPDATE catalog.listings SET listing_status='PUBLISHED',published_at=now()
      WHERE id=${listingId}::uuid AND owner_organization_id=${orgId}::uuid AND listing_status='DRAFT'
      RETURNING id,listing_key,title,listing_status,published_at
    `;
    if (!rows.length) throw new Error('Draft listing not found or already published');
    return rows[0];
  });
}
async function browseListings() {
  return await withServiceRole(async (tx) => await tx`
    SELECT l.id,l.listing_key,l.title,l.description,l.price_amount,l.currency,
      l.acceptance_criteria,l.created_at,o.name AS seller_name,
      c.capability_key,cv.version AS capability_version,cv.name AS capability_name
    FROM catalog.listings l
    JOIN identity.organizations o ON o.id=l.owner_organization_id
    JOIN catalog.capabilities c ON c.id=l.capability_id
    JOIN catalog.capability_versions cv ON cv.id=l.capability_version_id
    WHERE l.listing_status='PUBLISHED' AND c.capability_status='ACTIVE' AND cv.version_status='ACTIVE'
    ORDER BY l.created_at DESC LIMIT 100
  `);
}
async function createOrder(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.buyer_organization_id, 'buyer_organization_id');
  const listingId = requiredString(body.listing_id, 'listing_id');
  const idempotencyKey = requiredString(body.idempotency_key, 'idempotency_key', 200);
  return await withServiceRole(async (tx) => {
    const rows = await tx`SELECT * FROM api.create_marketplace_order(${user.id}::uuid,${orgId}::uuid,${listingId}::uuid,${idempotencyKey})`;
    return rows[0];
  });
}
async function transitionOrder(user: User, body: Record<string, unknown>) {
  const orderId = requiredString(body.order_id, 'order_id');
  const orgId = requiredString(body.actor_organization_id, 'actor_organization_id');
  const target = requiredString(body.target_status, 'target_status', 40);
  const reason = requiredString(body.reason, 'reason', 1000);
  return await withServiceRole(async (tx) => {
    const rows = await tx`SELECT * FROM api.transition_marketplace_order(${user.id}::uuid,${orderId}::uuid,${orgId}::uuid,${target},${reason})`;
    return rows[0];
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });
  try {
    if (req.method === 'GET') {
      const health = await withServiceRole(async (tx) => (await tx`SELECT current_database() AS database_name, now() AS checked_at`)[0]);
      return response({ status: 'ok', service: 'marketplace-api', version: '0.6.0', persistence: 'supabase-cloud', database: health });
    }
    if (req.method !== 'POST') return response({ error: 'Method not allowed' }, 405);
    const body = await req.json() as Record<string, unknown>;
    const action = requiredString(body.action, 'action', 60);
    if (action === 'browse_listings') return response({ data: await browseListings() });
    // Global reference taxonomies are intentionally public, read-only catalog data.
    // They contain no tenant records or secrets; the private schemas remain server-only.
    if (action === 'list_taxonomy_blueprints') return response({ data: await listTaxonomyBlueprints() });
    if (action === 'list_adapter_families') return response({ data: await listAdapterFamilies() });
    if (action === 'list_provider_adapter_blueprints') {
      const familyKey = body.family_key === undefined ? null : requiredString(body.family_key, 'family_key', 100);
      return response({ data: await listProviderAdapterBlueprints(familyKey) });
    }
    const user = await authenticate(req);
    let data: unknown;
    switch (action) {
      case 'list_organizations': data = await listOrganizations(user); break;
      case 'list_capabilities': data = await listCapabilities(user, body); break;
      case 'list_orders': data = await listOrders(user, body); break;
      case 'list_provider_listings': data = await listProviderListings(user, body); break;
      case 'create_organization': data = await createOrganization(user, body); break;
      case 'register_agent': data = await registerAgent(user, body); break;
      case 'create_capability': data = await createCapability(user, body); break;
      case 'create_listing': data = await createListing(user, body); break;
      case 'publish_listing': data = await publishListing(user, body); break;
      case 'create_order': data = await createOrder(user, body); break;
      case 'transition_order': data = await transitionOrder(user, body); break;
      default: return response({ error: 'Unknown action', action }, 404);
    }
    return response({ data, actor_user_id: user.id });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const status = message.includes('Authentication') || message.includes('session') ? 401 : 400;
    console.error('marketplace-api', message);
    return response({ error: message }, status);
  }
});
