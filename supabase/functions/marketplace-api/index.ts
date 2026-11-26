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
    JOIN identity.organizations o ON o.id = m.organization_id
    WHERE o.status = 'ACTIVE' AND m.organization_id = ${orgId}::uuid AND m.user_id = ${userId}::uuid
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
    WHERE o.status='ACTIVE' AND m.user_id=${user.id}::uuid AND m.membership_status='ACTIVE'
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

async function listHolonBlueprints(areaCode: string | null) {
  return await withServiceRole(async (tx) => {
    if (areaCode) {
      return await tx`
        SELECT h.holon_code, h.area_code, d.domain_name AS area_name,
          h.holon_level, h.holon_type, h.display_name, h.mandate,
          h.parent_holon_code, h.specialist_count, h.runbook_required,
          h.source_path, h.sort_order, h.taxonomy_version, h.status
        FROM areas.holon_blueprints h
        JOIN areas.domain_blueprints d ON d.domain_code = h.area_code
        WHERE h.status = 'ACTIVE' AND h.area_code = ${areaCode}
        ORDER BY h.sort_order
      `;
    }
    return await tx`
      SELECT h.holon_code, h.area_code, d.domain_name AS area_name,
        h.holon_level, h.holon_type, h.display_name, h.mandate,
        h.parent_holon_code, h.specialist_count, h.runbook_required,
        h.source_path, h.sort_order, h.taxonomy_version, h.status
      FROM areas.holon_blueprints h
      JOIN areas.domain_blueprints d ON d.domain_code = h.area_code
      WHERE h.status = 'ACTIVE'
      ORDER BY d.sort_order, h.sort_order
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

async function requireWorkspaceMember(tx: Tx, userId: string, orgId: string, workspaceId: string) {
  const rows = await tx`
    SELECT w.id
    FROM enterprise.workspaces w
    JOIN identity.organization_memberships m ON m.organization_id=w.organization_id
    JOIN identity.organizations o ON o.id=w.organization_id
    WHERE o.status='ACTIVE' AND w.id=${workspaceId}::uuid AND w.organization_id=${orgId}::uuid
      AND w.workspace_status='ACTIVE' AND m.user_id=${userId}::uuid
      AND m.membership_status='ACTIVE'
  `;
  if (!rows.length) throw new Error('Active workspace membership required');
}
function stringArray(value: unknown, field: string, pattern: RegExp, maxItems = 32): string[] {
  if (!Array.isArray(value) || value.length > maxItems) throw new Error(`Invalid ${field}`);
  const values = value.map((item) => requiredString(item, field, 100));
  if (values.some((item) => !pattern.test(item)) || new Set(values).size !== values.length) throw new Error(`Invalid or duplicate ${field}`);
  return values;
}
async function listWorkspaces(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  return await withServiceRole(async (tx) => {
    const rows = await tx`
      SELECT w.id,w.organization_id,w.workspace_key,w.name,w.description,w.workspace_status,w.created_at
      FROM enterprise.workspaces w
      JOIN identity.organization_memberships m ON m.organization_id=w.organization_id
      JOIN identity.organizations o ON o.id=w.organization_id
      WHERE o.status='ACTIVE' AND w.organization_id=${orgId}::uuid AND m.user_id=${user.id}::uuid
        AND m.membership_status='ACTIVE'
      ORDER BY w.created_at ASC
    `;
    return rows;
  });
}
async function listWorkspaceStructure(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const workspaceId = requiredString(body.workspace_id, 'workspace_id');
  return await withServiceRole(async (tx) => {
    await requireWorkspaceMember(tx, user.id, orgId, workspaceId);
    const domains = await tx`
      SELECT i.id,i.domain_code,b.domain_name,b.description,i.parent_installation_id,
        i.owner_user_id,i.installation_status,i.installed_at
      FROM areas.domain_installations i
      JOIN areas.domain_blueprints b ON b.domain_code=i.domain_code
      WHERE i.organization_id=${orgId}::uuid AND i.workspace_id=${workspaceId}::uuid
      ORDER BY b.sort_order
    `;
    const departments = await tx`
      SELECT i.id,i.department_key,b.department_name,b.description,i.owner_user_id,
        i.installation_status,i.installed_at
      FROM enterprise.department_installations i
      JOIN enterprise.department_blueprints b USING (department_key)
      WHERE i.organization_id=${orgId}::uuid AND i.workspace_id=${workspaceId}::uuid
      ORDER BY b.sort_order
    `;
    const holons = await tx`
      SELECT i.id,i.holon_code,b.display_name,b.holon_level,b.holon_type,
        b.parent_holon_code,i.parent_installation_id,i.owner_user_id,
        i.installation_status,i.installed_at
      FROM areas.holon_installations i
      JOIN areas.holon_blueprints b USING (holon_code)
      WHERE i.organization_id=${orgId}::uuid AND i.workspace_id=${workspaceId}::uuid
      ORDER BY b.sort_order
    `;
    return { organization_id: orgId, workspace_id: workspaceId, domains, departments, holons };
  });
}
async function createWorkspace(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const key = requiredString(body.workspace_key, 'workspace_key', 96).toLowerCase();
  const name = requiredString(body.name, 'name', 160);
  const description = body.description === undefined ? '' : requiredString(body.description, 'description', 2000);
  if (!/^[a-z0-9][a-z0-9._-]{1,95}$/.test(key)) throw new Error('Invalid workspace_key format');
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    const rows = await tx`
      INSERT INTO enterprise.workspaces (organization_id,workspace_key,name,description,created_by_user_id)
      VALUES (${orgId}::uuid,${key},${name},${description},${user.id}::uuid)
      RETURNING id,organization_id,workspace_key,name,description,workspace_status,created_at
    `;
    const workspace = rows[0];
    await tx`
      INSERT INTO enterprise.structure_installation_events
        (organization_id,workspace_id,event_type,entity_type,entity_id,actor_user_id,event_payload)
      VALUES (${orgId}::uuid,${workspace.id}::uuid,'WORKSPACE_CREATED','WORKSPACE',${workspace.id}::uuid,${user.id}::uuid,
        ${JSON.stringify({ workspace_key: key })}::jsonb)
    `;
    return workspace;
  });
}
async function installStructure(user: User, body: Record<string, unknown>) {
  const orgId = requiredString(body.organization_id, 'organization_id');
  const workspaceId = requiredString(body.workspace_id, 'workspace_id');
  const idempotencyKey = requiredString(body.idempotency_key, 'idempotency_key', 200);
  if (idempotencyKey.length < 8) throw new Error('idempotency_key must contain at least 8 characters');
  const domainCodes = stringArray(body.domain_codes, 'domain_codes', /^LD0[1-8]$/, 8);
  const departmentKeys = stringArray(body.department_keys, 'department_keys', /^[a-z0-9]+(-[a-z0-9]+)*$/, 8);
  const includeLd01Holarchy = body.include_ld01_holarchy === true;
  if (!domainCodes.length && !departmentKeys.length) throw new Error('Select at least one domain or department');
  if (includeLd01Holarchy && !domainCodes.includes('LD01')) throw new Error('LD01 must be selected before installing its holarchy');
  const payload = { domain_codes: [...domainCodes].sort(), department_keys: [...departmentKeys].sort(), include_ld01_holarchy: includeLd01Holarchy };
  return await withServiceRole(async (tx) => {
    await requireOrgRole(tx, user.id, orgId);
    await requireWorkspaceMember(tx, user.id, orgId, workspaceId);
    await tx`SELECT pg_advisory_xact_lock(hashtextextended(${orgId + ':' + workspaceId + ':' + idempotencyKey}, 0))`;
    const previous = await tx`
      SELECT id,request_payload,result_payload,(request_payload = ${JSON.stringify(payload)}::jsonb) AS payload_matches FROM enterprise.structure_installation_requests
      WHERE organization_id=${orgId}::uuid AND workspace_id=${workspaceId}::uuid AND idempotency_key=${idempotencyKey}
      LIMIT 1
    `;
    if (previous.length) {
      if (!previous[0].payload_matches) throw new Error('Idempotency key already used with a different installation payload');
      await tx`
        INSERT INTO enterprise.structure_installation_events
          (organization_id,workspace_id,request_id,event_type,entity_type,entity_id,actor_user_id,event_payload)
        VALUES (${orgId}::uuid,${workspaceId}::uuid,${previous[0].id}::uuid,'INSTALLATION_REPLAYED','WORKSPACE',${workspaceId}::uuid,${user.id}::uuid,
          ${JSON.stringify({ idempotency_key: idempotencyKey })}::jsonb)
      `;
      return previous[0].result_payload;
    }

    const domains = domainCodes.length ? await tx`
      SELECT domain_code FROM areas.domain_blueprints
      WHERE domain_code = ANY(${domainCodes}) AND status='ACTIVE'
      ORDER BY sort_order
    ` : [];
    if (domains.length !== domainCodes.length) throw new Error('One or more selected domain blueprints are unavailable');
    const departments = departmentKeys.length ? await tx`
      SELECT department_key FROM enterprise.department_blueprints
      WHERE department_key = ANY(${departmentKeys}) AND status='ACTIVE'
      ORDER BY sort_order
    ` : [];
    if (departments.length !== departmentKeys.length) throw new Error('One or more selected department blueprints are unavailable');

    const installedDomains: Array<{ id: string; domain_code: string; created: boolean }> = [];
    for (const item of domains) {
      const rows = await tx`
        INSERT INTO areas.domain_installations
          (organization_id,workspace_id,domain_code,installed_by_user_id)
        VALUES (${orgId}::uuid,${workspaceId}::uuid,${item.domain_code},${user.id}::uuid)
        ON CONFLICT (workspace_id,domain_code) DO NOTHING
        RETURNING id,domain_code
      `;
      const created = rows.length > 0;
      const installed = rows[0] ?? (await tx`
        SELECT id,domain_code FROM areas.domain_installations
        WHERE organization_id=${orgId}::uuid AND workspace_id=${workspaceId}::uuid AND domain_code=${item.domain_code}
      `)[0];
      installedDomains.push({ ...installed, created });
    }
    const installedDepartments: Array<{ id: string; department_key: string; created: boolean }> = [];
    for (const item of departments) {
      const rows = await tx`
        INSERT INTO enterprise.department_installations
          (organization_id,workspace_id,department_key,installed_by_user_id)
        VALUES (${orgId}::uuid,${workspaceId}::uuid,${item.department_key},${user.id}::uuid)
        ON CONFLICT (workspace_id,department_key) DO NOTHING
        RETURNING id,department_key
      `;
      const created = rows.length > 0;
      const installed = rows[0] ?? (await tx`
        SELECT id,department_key FROM enterprise.department_installations
        WHERE organization_id=${orgId}::uuid AND workspace_id=${workspaceId}::uuid AND department_key=${item.department_key}
      `)[0];
      installedDepartments.push({ ...installed, created });
    }

    const installedHolons: Array<{ id: string; holon_code: string; created: boolean }> = [];
    if (includeLd01Holarchy) {
      const ld01 = installedDomains.find((item) => item.domain_code === 'LD01');
      if (!ld01) throw new Error('LD01 installation is required for its holarchy');
      const blueprints = await tx`
        SELECT holon_code,parent_holon_code FROM areas.holon_blueprints
        WHERE area_code='LD01' AND status='ACTIVE' ORDER BY sort_order
      `;
      if (blueprints.length !== 17) throw new Error('Canonical LD01 holarchy blueprint is incomplete');
      const parentIds = new Map<string, string>();
      for (const item of blueprints) {
        const parentId = item.parent_holon_code ? parentIds.get(item.parent_holon_code) ?? null : null;
        if (item.parent_holon_code && !parentId) throw new Error('LD01 holon parent blueprint is unresolved');
        const rows = await tx`
          INSERT INTO areas.holon_installations
            (organization_id,workspace_id,domain_installation_id,holon_code,parent_installation_id,installed_by_user_id)
          VALUES (${orgId}::uuid,${workspaceId}::uuid,${ld01.id}::uuid,${item.holon_code},${parentId}::uuid,${user.id}::uuid)
          ON CONFLICT (domain_installation_id,holon_code) DO NOTHING
          RETURNING id,holon_code
        `;
        const created = rows.length > 0;
        const installed = rows[0] ?? (await tx`
          SELECT id,holon_code FROM areas.holon_installations
          WHERE domain_installation_id=${ld01.id}::uuid AND holon_code=${item.holon_code}
        `)[0];
        parentIds.set(item.holon_code, installed.id);
        installedHolons.push({ ...installed, created });
      }
    }

    const result = {
      organization_id: orgId, workspace_id: workspaceId, idempotency_key: idempotencyKey,
      installed_domains: installedDomains.map(({ id, domain_code }) => ({ id, domain_code })),
      installed_departments: installedDepartments.map(({ id, department_key }) => ({ id, department_key })),
      installed_holons: installedHolons.map(({ id, holon_code }) => ({ id, holon_code })),
      counts: { domains: installedDomains.length, departments: installedDepartments.length, holons: installedHolons.length },
    };
    const requests = await tx`
      INSERT INTO enterprise.structure_installation_requests
        (organization_id,workspace_id,idempotency_key,request_payload,result_payload,created_by_user_id)
      VALUES (${orgId}::uuid,${workspaceId}::uuid,${idempotencyKey},${JSON.stringify(payload)}::jsonb,${JSON.stringify(result)}::jsonb,${user.id}::uuid)
      RETURNING id
    `;
    const requestId = requests[0].id;
    for (const item of installedDomains) if (item.created) await tx`
      INSERT INTO enterprise.structure_installation_events
        (organization_id,workspace_id,request_id,event_type,entity_type,entity_id,actor_user_id,event_payload)
      VALUES (${orgId}::uuid,${workspaceId}::uuid,${requestId}::uuid,'DOMAIN_INSTALLED','DOMAIN',${item.id}::uuid,${user.id}::uuid,
        ${JSON.stringify({ domain_code: item.domain_code })}::jsonb)
    `;
    for (const item of installedDepartments) if (item.created) await tx`
      INSERT INTO enterprise.structure_installation_events
        (organization_id,workspace_id,request_id,event_type,entity_type,entity_id,actor_user_id,event_payload)
      VALUES (${orgId}::uuid,${workspaceId}::uuid,${requestId}::uuid,'DEPARTMENT_INSTALLED','DEPARTMENT',${item.id}::uuid,${user.id}::uuid,
        ${JSON.stringify({ department_key: item.department_key })}::jsonb)
    `;
    for (const item of installedHolons) if (item.created) await tx`
      INSERT INTO enterprise.structure_installation_events
        (organization_id,workspace_id,request_id,event_type,entity_type,entity_id,actor_user_id,event_payload)
      VALUES (${orgId}::uuid,${workspaceId}::uuid,${requestId}::uuid,'HOLON_INSTALLED','HOLON',${item.id}::uuid,${user.id}::uuid,
        ${JSON.stringify({ holon_code: item.holon_code })}::jsonb)
    `;
    return result;
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
      return response({ status: 'ok', service: 'marketplace-api', version: '0.8.0', persistence: 'supabase-cloud', database: health });
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
    if (action === 'list_holon_blueprints') {
      const areaCode = body.area_code === undefined ? null : requiredString(body.area_code, 'area_code', 4);
      return response({ data: await listHolonBlueprints(areaCode) });
    }
    const user = await authenticate(req);
    let data: unknown;
    switch (action) {
      case 'list_organizations': data = await listOrganizations(user); break;
      case 'list_workspaces': data = await listWorkspaces(user, body); break;
      case 'list_workspace_structure': data = await listWorkspaceStructure(user, body); break;
      case 'create_workspace': data = await createWorkspace(user, body); break;
      case 'install_structure': data = await installStructure(user, body); break;
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
