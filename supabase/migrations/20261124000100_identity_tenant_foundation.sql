-- A'Space Marketplace — identity / tenant foundation
-- Applied to Supabase Cloud project swegnrvaxxgfrnshdpxx on 2026-11-24.
-- Canonical source for the deployed identity/tenant baseline.
BEGIN;
DO $guard$
BEGIN
  IF current_user <> 'postgres' THEN
    RAISE EXCEPTION 'Migration requires postgres; current_user=%', current_user;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
     OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated')
     OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
    RAISE EXCEPTION 'Expected Supabase roles anon, authenticated and service_role';
  END IF;
END
$guard$;

CREATE SCHEMA IF NOT EXISTS identity AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS areas AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS enterprise AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS catalog AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS commerce AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS operations AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS trust AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS integration AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS finance AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS api AUTHORIZATION postgres;

REVOKE ALL ON SCHEMA identity, areas, enterprise, catalog, commerce,
  operations, trust, integration, finance, api FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA identity, areas, enterprise, catalog, commerce,
  operations, trust, integration, finance, api TO service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;

DO $default_acl$
DECLARE schema_name text;
BEGIN
  FOREACH schema_name IN ARRAY ARRAY[
    'identity', 'areas', 'enterprise', 'catalog', 'commerce',
    'operations', 'trust', 'integration', 'finance', 'api'
  ] LOOP
    EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA %I REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated', schema_name);
    EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA %I REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated', schema_name);
    EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA %I REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated', schema_name);
    EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA %I GRANT ALL ON TABLES TO service_role', schema_name);
    EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA %I GRANT ALL ON SEQUENCES TO service_role', schema_name);
    EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA %I GRANT EXECUTE ON FUNCTIONS TO service_role', schema_name);
  END LOOP;
END
$default_acl$;

CREATE TABLE identity.organizations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_key text NOT NULL UNIQUE,
  name text NOT NULL CHECK (length(btrim(name)) > 0),
  organization_type text NOT NULL CHECK (organization_type IN (
    'MARKETPLACE_OPERATOR','INTERNAL_VENTURE','EXTERNAL_ENTERPRISE',
    'SUPPLIER','CUSTOMER','PARTNER')),
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','SUSPENDED','CLOSED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT organizations_key_format CHECK (organization_key ~ '^[A-Z0-9][A-Z0-9_-]{2,63}$')
);

CREATE TABLE identity.organization_memberships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  membership_status text NOT NULL DEFAULT 'ACTIVE' CHECK (membership_status IN ('INVITED','ACTIVE','SUSPENDED','REVOKED')),
  joined_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, user_id),
  CONSTRAINT membership_joined_state CHECK (
    (membership_status = 'ACTIVE' AND joined_at IS NOT NULL)
    OR membership_status <> 'ACTIVE')
);
CREATE INDEX organization_memberships_user_idx ON identity.organization_memberships (user_id, membership_status);
CREATE INDEX organization_memberships_org_idx ON identity.organization_memberships (organization_id, membership_status);

CREATE TABLE identity.delegations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  grantor_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  grantee_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  role_code text NOT NULL CHECK (role_code ~ '^[A-Z][A-Z0-9_]{1,63}$'),
  scope_type text NOT NULL CHECK (scope_type IN ('PLATFORM','ORGANIZATION','AREA','ENTERPRISE','DEPARTMENT','PROJECT','RESOURCE')),
  scope_id uuid,
  permission_codes text[] NOT NULL CHECK (cardinality(permission_codes) > 0),
  delegation_status text NOT NULL DEFAULT 'ACTIVE' CHECK (delegation_status IN ('ACTIVE','REVOKED','EXPIRED')),
  starts_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT delegation_scope_shape CHECK (
    (scope_type IN ('PLATFORM','ORGANIZATION') AND scope_id IS NULL)
    OR (scope_type IN ('AREA','ENTERPRISE','DEPARTMENT','PROJECT','RESOURCE') AND scope_id IS NOT NULL)),
  CONSTRAINT delegation_time_window CHECK (expires_at IS NULL OR expires_at > starts_at),
  CONSTRAINT delegation_revocation_shape CHECK (
    (delegation_status = 'REVOKED' AND revoked_at IS NOT NULL)
    OR delegation_status <> 'REVOKED'),
  CONSTRAINT delegation_parties_differ CHECK (grantor_user_id <> grantee_user_id),
  CONSTRAINT delegations_id_org_grantee_unique UNIQUE (id, organization_id, grantee_user_id)
);
CREATE INDEX delegations_grantor_idx ON identity.delegations (organization_id, grantor_user_id, delegation_status);
CREATE INDEX delegations_grantee_idx ON identity.delegations (organization_id, grantee_user_id, delegation_status);

CREATE TABLE identity.role_bindings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  subject_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  role_code text NOT NULL CHECK (role_code ~ '^[A-Z][A-Z0-9_]{1,63}$'),
  scope_type text NOT NULL CHECK (scope_type IN ('PLATFORM','ORGANIZATION','AREA','ENTERPRISE','DEPARTMENT','PROJECT','RESOURCE')),
  scope_id uuid,
  granted_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  source_delegation_id uuid,
  binding_status text NOT NULL DEFAULT 'ACTIVE' CHECK (binding_status IN ('ACTIVE','SUSPENDED','REVOKED','EXPIRED')),
  starts_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT role_binding_source_delegation_scope_fk
    FOREIGN KEY (source_delegation_id, organization_id, subject_user_id)
    REFERENCES identity.delegations (id, organization_id, grantee_user_id) ON DELETE RESTRICT,
  CONSTRAINT role_binding_scope_shape CHECK (
    (scope_type IN ('PLATFORM','ORGANIZATION') AND scope_id IS NULL)
    OR (scope_type IN ('AREA','ENTERPRISE','DEPARTMENT','PROJECT','RESOURCE') AND scope_id IS NOT NULL)),
  CONSTRAINT role_binding_time_window CHECK (expires_at IS NULL OR expires_at > starts_at)
);
CREATE INDEX role_bindings_subject_idx ON identity.role_bindings (organization_id, subject_user_id, binding_status);
CREATE INDEX role_bindings_scope_idx ON identity.role_bindings (organization_id, scope_type, scope_id, binding_status);

ALTER TABLE identity.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.organization_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.delegations ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.role_bindings ENABLE ROW LEVEL SECURITY;

CREATE POLICY organizations_read_active_member ON identity.organizations
  FOR SELECT TO authenticated
  USING (status = 'ACTIVE' AND EXISTS (
    SELECT 1 FROM identity.organization_memberships AS membership
    WHERE membership.organization_id = organizations.id
      AND membership.user_id = (SELECT auth.uid())
      AND membership.membership_status = 'ACTIVE'));

CREATE POLICY memberships_read_self ON identity.organization_memberships
  FOR SELECT TO authenticated USING (user_id = (SELECT auth.uid()));

CREATE POLICY delegations_read_party ON identity.delegations
  FOR SELECT TO authenticated
  USING (grantor_user_id = (SELECT auth.uid()) OR grantee_user_id = (SELECT auth.uid()));

CREATE POLICY role_bindings_read_subject ON identity.role_bindings
  FOR SELECT TO authenticated USING (subject_user_id = (SELECT auth.uid()));

REVOKE ALL ON ALL TABLES IN SCHEMA identity FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA identity FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA identity TO authenticated;
GRANT SELECT ON identity.organizations, identity.organization_memberships,
  identity.delegations, identity.role_bindings TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA identity TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA identity TO service_role;

COMMENT ON SCHEMA identity IS 'Private A''Space identity and tenant authority domain; not exposed through PostgREST by default.';
COMMENT ON TABLE identity.organizations IS 'Tenant and ownership root. Internal ventures and external enterprises remain distinct organizations.';
COMMENT ON TABLE identity.organization_memberships IS 'Authoritative human-to-organization membership. Supabase Auth authenticates; this table does not replace auth.users.';
COMMENT ON TABLE identity.role_bindings IS 'Scoped role appointments. Role codes preserve S0/A0/A1/A2/A3/B1/B2/B3 distinctions; no user-metadata authorization.';
COMMENT ON TABLE identity.delegations IS 'Explicit grantor/grantee mandate with organization, scope, permission set and validity window.';
COMMIT;