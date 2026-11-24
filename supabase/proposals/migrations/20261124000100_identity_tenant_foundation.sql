-- A'Space Marketplace — identity / tenant foundation
-- Proposal ID: D1-09 / W23
-- Status: PROPOSAL ONLY. This file is intentionally outside supabase/migrations/.
-- Do not execute against the connected Supabase project or production.
-- Promote to supabase/migrations/ only after D1-09 arbitrations and D1-EXIT gates pass.
--
-- Preconditions:
--   * Supabase-managed roles anon, authenticated, service_role exist.
--   * auth.users and auth.uid() are available.
--   * Migration is executed by postgres in a disposable/local Supabase database.
--
-- Scope:
--   * Establish private domain schemas.
--   * Establish organization, membership, scoped role-binding and delegation records.
--   * Enable RLS explicitly on every table created here.
--   * Grant authenticated users read-only access, filtered by RLS.
--   * Keep all writes behind trusted server-side operations for this first foundation.
--
-- Non-goals: no Auth configuration, no REST exposed-schema changes, no Storage,
-- no Stripe/payment/ledger, no API RPCs, no service-role key distribution.

BEGIN;

DO $guard$
BEGIN
  IF current_user <> 'postgres' THEN
    RAISE EXCEPTION 'D1-09 proposal requires migration owner postgres; current_user=%', current_user;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
     OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated')
     OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
    RAISE EXCEPTION 'Expected Supabase roles anon, authenticated and service_role';
  END IF;
END
$guard$;

-- D1-02 domain topology. All schemas remain private; PostgREST exposure is
-- deliberately unchanged (D1-08 currently reports public, graphql_public).
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

-- The trusted backend role remains server-side only. This is not an agent,
-- browser or customer credential and must never be distributed.
GRANT USAGE ON SCHEMA identity, areas, enterprise, catalog, commerce,
  operations, trust, integration, finance, api TO service_role;

-- Remove broad future-object defaults observed in D1-08 for postgres-owned
-- public objects, then establish least-privilege defaults for private schemas.
-- This affects future objects only; it does not delete or rewrite objects.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA identity
  REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA identity
  REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA identity
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA identity
  GRANT ALL ON TABLES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA identity
  GRANT ALL ON SEQUENCES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA identity
  GRANT EXECUTE ON FUNCTIONS TO service_role;

CREATE TABLE identity.organizations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_key text NOT NULL UNIQUE,
  name text NOT NULL CHECK (length(btrim(name)) > 0),
  organization_type text NOT NULL CHECK (organization_type IN (
    'MARKETPLACE_OPERATOR',
    'INTERNAL_VENTURE',
    'EXTERNAL_ENTERPRISE',
    'SUPPLIER',
    'CUSTOMER',
    'PARTNER'
  )),
  status text NOT NULL DEFAULT 'ACTIVE'
    CHECK (status IN ('ACTIVE', 'SUSPENDED', 'CLOSED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT organizations_key_format CHECK (
    organization_key ~ '^[A-Z0-9][A-Z0-9_-]{2,63}$'
  )
);

CREATE TABLE identity.organization_memberships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL
    REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  membership_status text NOT NULL DEFAULT 'ACTIVE'
    CHECK (membership_status IN ('INVITED', 'ACTIVE', 'SUSPENDED', 'REVOKED')),
  joined_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, user_id),
  CONSTRAINT membership_joined_state CHECK (
    (membership_status = 'ACTIVE' AND joined_at IS NOT NULL)
    OR (membership_status <> 'ACTIVE')
  )
);

CREATE INDEX organization_memberships_user_idx
  ON identity.organization_memberships (user_id, membership_status);
CREATE INDEX organization_memberships_org_idx
  ON identity.organization_memberships (organization_id, membership_status);

CREATE TABLE identity.delegations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL
    REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  grantor_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  grantee_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  role_code text NOT NULL CHECK (role_code ~ '^[A-Z][A-Z0-9_]{1,63}$'),
  scope_type text NOT NULL CHECK (scope_type IN (
    'PLATFORM', 'ORGANIZATION', 'AREA', 'ENTERPRISE',
    'DEPARTMENT', 'PROJECT', 'RESOURCE'
  )),
  scope_id uuid,
  permission_codes text[] NOT NULL CHECK (cardinality(permission_codes) > 0),
  delegation_status text NOT NULL DEFAULT 'ACTIVE'
    CHECK (delegation_status IN ('ACTIVE', 'REVOKED', 'EXPIRED')),
  starts_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT delegation_scope_shape CHECK (
    (scope_type IN ('PLATFORM', 'ORGANIZATION') AND scope_id IS NULL)
    OR (scope_type IN ('AREA', 'ENTERPRISE', 'DEPARTMENT', 'PROJECT', 'RESOURCE')
        AND scope_id IS NOT NULL)
  ),
  CONSTRAINT delegation_time_window CHECK (
    expires_at IS NULL OR expires_at > starts_at
  ),
  CONSTRAINT delegation_revocation_shape CHECK (
    (delegation_status = 'REVOKED' AND revoked_at IS NOT NULL)
    OR (delegation_status <> 'REVOKED')
  ),
  CONSTRAINT delegation_parties_differ CHECK (grantor_user_id <> grantee_user_id)
);

CREATE INDEX delegations_grantor_idx
  ON identity.delegations (organization_id, grantor_user_id, delegation_status);
CREATE INDEX delegations_grantee_idx
  ON identity.delegations (organization_id, grantee_user_id, delegation_status);

CREATE TABLE identity.role_bindings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL
    REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  subject_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  role_code text NOT NULL CHECK (role_code ~ '^[A-Z][A-Z0-9_]{1,63}$'),
  scope_type text NOT NULL CHECK (scope_type IN (
    'PLATFORM', 'ORGANIZATION', 'AREA', 'ENTERPRISE',
    'DEPARTMENT', 'PROJECT', 'RESOURCE'
  )),
  scope_id uuid,
  granted_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  source_delegation_id uuid
    REFERENCES identity.delegations(id) ON DELETE RESTRICT,
  binding_status text NOT NULL DEFAULT 'ACTIVE'
    CHECK (binding_status IN ('ACTIVE', 'SUSPENDED', 'REVOKED', 'EXPIRED')),
  starts_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT role_binding_scope_shape CHECK (
    (scope_type IN ('PLATFORM', 'ORGANIZATION') AND scope_id IS NULL)
    OR (scope_type IN ('AREA', 'ENTERPRISE', 'DEPARTMENT', 'PROJECT', 'RESOURCE')
        AND scope_id IS NOT NULL)
  ),
  CONSTRAINT role_binding_time_window CHECK (
    expires_at IS NULL OR expires_at > starts_at
  )
);

CREATE INDEX role_bindings_subject_idx
  ON identity.role_bindings (organization_id, subject_user_id, binding_status);
CREATE INDEX role_bindings_scope_idx
  ON identity.role_bindings (organization_id, scope_type, scope_id, binding_status);

-- Explicit RLS: the existing ensure_rls event trigger only covers public.
ALTER TABLE identity.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.organization_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.delegations ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.role_bindings ENABLE ROW LEVEL SECURITY;

-- Read policies only. Writes are intentionally server-mediated until a
-- separately reviewed API contract and authorization workflow exists.
CREATE POLICY organizations_read_active_member
  ON identity.organizations
  FOR SELECT TO authenticated
  USING (
    status = 'ACTIVE'
    AND EXISTS (
      SELECT 1
      FROM identity.organization_memberships AS membership
      WHERE membership.organization_id = organizations.id
        AND membership.user_id = (SELECT auth.uid())
        AND membership.membership_status = 'ACTIVE'
    )
  );

CREATE POLICY memberships_read_self
  ON identity.organization_memberships
  FOR SELECT TO authenticated
  USING (user_id = (SELECT auth.uid()));

CREATE POLICY delegations_read_party
  ON identity.delegations
  FOR SELECT TO authenticated
  USING (
    grantor_user_id = (SELECT auth.uid())
    OR grantee_user_id = (SELECT auth.uid())
  );

CREATE POLICY role_bindings_read_subject
  ON identity.role_bindings
  FOR SELECT TO authenticated
  USING (subject_user_id = (SELECT auth.uid()));

REVOKE ALL ON ALL TABLES IN SCHEMA identity FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA identity FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA identity TO authenticated;
GRANT SELECT ON identity.organizations,
  identity.organization_memberships,
  identity.delegations,
  identity.role_bindings TO authenticated;

GRANT ALL ON ALL TABLES IN SCHEMA identity TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA identity TO service_role;

COMMENT ON SCHEMA identity IS
  'Private A''Space identity and tenant authority domain. Not exposed through PostgREST by default.';
COMMENT ON TABLE identity.organizations IS
  'Tenant and ownership root. Internal ventures and external enterprises remain distinct organizations.';
COMMENT ON TABLE identity.organization_memberships IS
  'Authoritative human-to-organization membership. Supabase Auth authenticates; this table does not replace auth.users.';
COMMENT ON TABLE identity.role_bindings IS
  'Scoped role appointments. Role codes preserve S0/A0/A1/A2/A3/B1/B2/B3 distinctions; no user-metadata authorization.';
COMMENT ON TABLE identity.delegations IS
  'Explicit grantor/grantee mandate with organization, scope, permission set and validity window.';

COMMIT;
