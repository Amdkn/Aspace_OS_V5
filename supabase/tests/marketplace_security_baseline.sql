-- A'Space Marketplace — read-only security baseline assertions.
-- Run against the target Supabase project after applying migrations.
-- This script makes no persistent changes; it fails closed if the private-schema
-- gateway model or the identity read-policy boundary regresses.
DO $test$
DECLARE
  v_bad text;
BEGIN
  SELECT string_agg(format('%I.%I', schemaname, tablename), ', ')
    INTO v_bad
  FROM pg_tables
  WHERE schemaname IN ('identity','enterprise','catalog','commerce','integration','areas','content')
    AND NOT coalesce((SELECT c.relrowsecurity
                      FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                      WHERE n.nspname=pg_tables.schemaname AND c.relname=pg_tables.tablename
                      LIMIT 1), false);
  IF v_bad IS NOT NULL THEN
    RAISE EXCEPTION 'RLS is not enabled on: %', v_bad;
  END IF;

  SELECT string_agg(nspname, ', ')
    INTO v_bad
  FROM pg_namespace
  WHERE nspname IN ('areas','enterprise','catalog','commerce','integration','api')
    AND (has_schema_privilege('anon', nspname, 'USAGE')
      OR has_schema_privilege('authenticated', nspname, 'USAGE'));
  IF v_bad IS NOT NULL THEN
    RAISE EXCEPTION 'Private schemas exposed to browser roles: %', v_bad;
  END IF;

  SELECT string_agg(format('%I.%I', table_schema, table_name), ', ')
    INTO v_bad
  FROM information_schema.role_table_grants
  WHERE grantee IN ('anon','authenticated')
    AND table_schema IN ('areas','enterprise','catalog','commerce','integration','api');
  IF v_bad IS NOT NULL THEN
    RAISE EXCEPTION 'Private tables have browser-role grants: %', v_bad;
  END IF;

  SELECT string_agg(format('%I.%I(%s)', n.nspname, p.proname,
                           pg_get_function_identity_arguments(p.oid)), ', ')
    INTO v_bad
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname IN ('identity','enterprise','catalog','commerce','integration','areas','api')
    AND p.prosecdef
    AND (
      p.proconfig IS NULL
      OR NOT EXISTS (SELECT 1 FROM unnest(p.proconfig) cfg WHERE cfg LIKE 'search_path=%')
      OR has_function_privilege('anon', p.oid, 'EXECUTE')
      OR has_function_privilege('authenticated', p.oid, 'EXECUTE')
    );
  IF v_bad IS NOT NULL THEN
    RAISE EXCEPTION 'SECURITY DEFINER function has unsafe search_path or browser execution: %', v_bad;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='organizations' AND cmd='SELECT')
     OR NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='organization_memberships' AND cmd='SELECT')
     OR NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='delegations' AND cmd='SELECT')
     OR NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='role_bindings' AND cmd='SELECT') THEN
    RAISE EXCEPTION 'Expected scoped identity SELECT policies are missing';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='profiles' AND policyname='profiles_insert_self')
     OR NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='profiles' AND policyname='profiles_read_self')
     OR NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='identity' AND tablename='profiles' AND policyname='profiles_update_self') THEN
    RAISE EXCEPTION 'Coach-adopted profile self policies are missing';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='content' AND tablename='cms_collections' AND policyname='cms_collections_manage_active_org_members')
     OR NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='content' AND tablename='cms_items' AND policyname='cms_items_manage_active_org_members') THEN
    RAISE EXCEPTION 'Coach-adopted CMS tenant policies are missing';
  END IF;

  IF (SELECT count(*) FROM information_schema.tables
      WHERE table_schema='integration' AND table_name IN (
        'provider_adapter_manifests','tenant_connections','adapter_oauth_transactions',
        'adapter_execution_jobs','adapter_execution_events','adapter_webhook_receipts'
      )) <> 6 THEN
    RAISE EXCEPTION 'Adapter execution foundation tables are incomplete';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_trigger
                 WHERE tgrelid='integration.adapter_execution_events'::regclass
                   AND tgname='adapter_execution_events_no_truncate'
                   AND NOT tgisinternal) THEN
    RAISE EXCEPTION 'Adapter execution event TRUNCATE guard is missing';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint
                 WHERE conrelid='integration.provider_adapter_manifests'::regclass
                   AND conname='provider_adapter_manifests_auth_config_no_secrets_check') THEN
    RAISE EXCEPTION 'Provider manifest secret-key guard is missing';
  END IF;

  RAISE NOTICE 'PASS: RLS, private-schema grants, SECURITY DEFINER ACL/search_path and identity read policies';
END
$test$;
