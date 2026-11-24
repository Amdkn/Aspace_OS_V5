-- D1-09 tenant / RLS assertions — LOCAL DATABASE ONLY
-- Run only against a disposable local Supabase database after applying the
-- proposal migration manually. Never point this script at production.
-- The entire fixture and test run is rolled back.
\set ON_ERROR_STOP on
BEGIN;

DO $guard$
BEGIN
  IF current_user <> 'postgres' THEN
    RAISE EXCEPTION 'Run this assertion script as postgres on a disposable local database';
  END IF;
END
$guard$;

-- Synthetic Auth identities exist only inside this transaction.
INSERT INTO auth.users
  (id, aud, role, email, encrypted_password, email_confirmed_at,
   raw_app_meta_data, raw_user_meta_data, created_at, updated_at)
VALUES
  ('a1000000-0000-4000-8000-000000000001', 'authenticated', 'authenticated',
   'd1-09-tenant-a@example.test', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now()),
  ('b2000000-0000-4000-8000-000000000002', 'authenticated', 'authenticated',
   'd1-09-tenant-b@example.test', '', now(), '{}'::jsonb, '{}'::jsonb, now(), now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO identity.organizations
  (id, organization_key, name, organization_type, created_by_user_id)
VALUES
  ('a1000000-0000-4000-8000-000000000010', 'TEST-TENANT-A', 'Test Tenant A',
   'EXTERNAL_ENTERPRISE', 'a1000000-0000-4000-8000-000000000001'),
  ('b2000000-0000-4000-8000-000000000020', 'TEST-TENANT-B', 'Test Tenant B',
   'EXTERNAL_ENTERPRISE', 'b2000000-0000-4000-8000-000000000002');

INSERT INTO identity.organization_memberships
  (id, organization_id, user_id, membership_status, joined_at)
VALUES
  ('a1000000-0000-4000-8000-000000000011',
   'a1000000-0000-4000-8000-000000000010',
   'a1000000-0000-4000-8000-000000000001', 'ACTIVE', now()),
  ('b2000000-0000-4000-8000-000000000021',
   'b2000000-0000-4000-8000-000000000020',
   'b2000000-0000-4000-8000-000000000002', 'ACTIVE', now());

INSERT INTO identity.delegations
  (id, organization_id, grantor_user_id, grantee_user_id, role_code,
   scope_type, scope_id, permission_codes)
VALUES
  ('a1000000-0000-4000-8000-000000000012',
   'a1000000-0000-4000-8000-000000000010',
   'a1000000-0000-4000-8000-000000000001',
   'b2000000-0000-4000-8000-000000000002',
   'B2_MANAGER', 'DEPARTMENT',
   'a1000000-0000-4000-8000-000000000013',
   ARRAY['department.read']::text[]);

INSERT INTO identity.role_bindings
  (id, organization_id, subject_user_id, role_code, scope_type, scope_id,
   granted_by_user_id, source_delegation_id)
VALUES
  ('a1000000-0000-4000-8000-000000000014',
   'a1000000-0000-4000-8000-000000000010',
   'a1000000-0000-4000-8000-000000000001',
   'A3_PICARD', 'ENTERPRISE',
   'a1000000-0000-4000-8000-000000000015',
   'a1000000-0000-4000-8000-000000000001', NULL),
  ('b2000000-0000-4000-8000-000000000022',
   'b2000000-0000-4000-8000-000000000020',
   'b2000000-0000-4000-8000-000000000002',
   'B1_CEO', 'ENTERPRISE',
   'b2000000-0000-4000-8000-000000000023',
   'b2000000-0000-4000-8000-000000000002', NULL);

-- Static privilege and RLS assertions as database owner.
DO $assertions$
BEGIN
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'identity.organizations'::regclass) THEN
    RAISE EXCEPTION 'RLS missing on identity.organizations';
  END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'identity.organization_memberships'::regclass) THEN
    RAISE EXCEPTION 'RLS missing on identity.organization_memberships';
  END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'identity.delegations'::regclass) THEN
    RAISE EXCEPTION 'RLS missing on identity.delegations';
  END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid = 'identity.role_bindings'::regclass) THEN
    RAISE EXCEPTION 'RLS missing on identity.role_bindings';
  END IF;
  IF has_table_privilege('anon', 'identity.organizations', 'SELECT') THEN
    RAISE EXCEPTION 'anon unexpectedly has SELECT on organizations';
  END IF;
  IF has_table_privilege('authenticated', 'identity.organizations', 'INSERT') THEN
    RAISE EXCEPTION 'authenticated unexpectedly has INSERT on organizations';
  END IF;
  IF has_table_privilege('authenticated', 'identity.organizations', 'UPDATE') THEN
    RAISE EXCEPTION 'authenticated unexpectedly has UPDATE on organizations';
  END IF;
END
$assertions$;

-- Tenant A: can see only its own organization and own identity grants.
SET LOCAL ROLE authenticated;
SELECT set_config('request.jwt.claim.sub', 'a1000000-0000-4000-8000-000000000001', true);

DO $tenant_a$
DECLARE
  visible_orgs integer;
  visible_memberships integer;
  visible_roles integer;
  visible_delegations integer;
BEGIN
  SELECT count(*) INTO visible_orgs FROM identity.organizations;
  SELECT count(*) INTO visible_memberships FROM identity.organization_memberships;
  SELECT count(*) INTO visible_roles FROM identity.role_bindings;
  SELECT count(*) INTO visible_delegations FROM identity.delegations;

  IF visible_orgs <> 1 THEN RAISE EXCEPTION 'Tenant A expected 1 organization, saw %', visible_orgs; END IF;
  IF visible_memberships <> 1 THEN RAISE EXCEPTION 'Tenant A expected 1 membership, saw %', visible_memberships; END IF;
  IF visible_roles <> 1 THEN RAISE EXCEPTION 'Tenant A expected 1 role binding, saw %', visible_roles; END IF;
  IF visible_delegations <> 1 THEN RAISE EXCEPTION 'Tenant A expected 1 delegation party record, saw %', visible_delegations; END IF;

  BEGIN
    INSERT INTO identity.organizations
      (organization_key, name, organization_type, created_by_user_id)
    VALUES ('SHOULD-BE-DENIED-A', 'Should Be Denied', 'CUSTOMER',
      'a1000000-0000-4000-8000-000000000001');
    RAISE EXCEPTION 'Tenant A unexpectedly inserted an organization';
  EXCEPTION WHEN insufficient_privilege THEN
    NULL;
  END;
END
$tenant_a$;

-- Tenant B: sees its own organization only. It is a delegate in Tenant A,
-- but delegation visibility does not itself grant tenant membership.
SELECT set_config('request.jwt.claim.sub', 'b2000000-0000-4000-8000-000000000002', true);

DO $tenant_b$
DECLARE
  visible_orgs integer;
  visible_memberships integer;
  visible_roles integer;
  visible_delegations integer;
BEGIN
  SELECT count(*) INTO visible_orgs FROM identity.organizations;
  SELECT count(*) INTO visible_memberships FROM identity.organization_memberships;
  SELECT count(*) INTO visible_roles FROM identity.role_bindings;
  SELECT count(*) INTO visible_delegations FROM identity.delegations;

  IF visible_orgs <> 1 THEN RAISE EXCEPTION 'Tenant B expected 1 organization, saw %', visible_orgs; END IF;
  IF visible_memberships <> 1 THEN RAISE EXCEPTION 'Tenant B expected 1 membership, saw %', visible_memberships; END IF;
  IF visible_roles <> 1 THEN RAISE EXCEPTION 'Tenant B expected 1 role binding, saw %', visible_roles; END IF;
  IF visible_delegations <> 1 THEN RAISE EXCEPTION 'Tenant B expected its delegation record, saw %', visible_delegations; END IF;

  BEGIN
    UPDATE identity.organizations
      SET name = 'Cross-tenant mutation'
      WHERE id = 'a1000000-0000-4000-8000-000000000010';
    RAISE EXCEPTION 'Tenant B unexpectedly updated Tenant A organization';
  EXCEPTION WHEN insufficient_privilege THEN
    NULL;
  END;
END
$tenant_b$;

RESET ROLE;
ROLLBACK;

-- Success is reaching this line without an exception. All synthetic data is rolled back.
SELECT 'D1-09 tenant/RLS assertions passed; fixture transaction rolled back.' AS result;
