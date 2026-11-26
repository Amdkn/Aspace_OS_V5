-- Structural regression for order-backed Marketplace capability entitlements.
DO $test$
DECLARE v_rls boolean; v_count integer; v_definer boolean;
BEGIN
  SELECT c.relrowsecurity INTO v_rls FROM pg_class c
  JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='commerce' AND c.relname='capability_entitlements';
  IF v_rls IS DISTINCT FROM true THEN RAISE EXCEPTION 'capability_entitlements must have RLS enabled'; END IF;
  IF has_table_privilege('anon','commerce.capability_entitlements','SELECT')
     OR has_table_privilege('authenticated','commerce.capability_entitlements','SELECT') THEN
    RAISE EXCEPTION 'Browser roles must not read capability_entitlements directly';
  END IF;
  SELECT count(*) INTO v_count FROM pg_trigger t
  JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='commerce' AND c.relname='orders'
    AND t.tgname='orders_grant_capability_entitlement_after_acceptance' AND NOT t.tgisinternal;
  IF v_count <> 1 THEN RAISE EXCEPTION 'Order acceptance entitlement trigger missing'; END IF;
  SELECT count(*) INTO v_count FROM pg_trigger t
  JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='commerce' AND c.relname='capability_entitlements'
    AND t.tgname='capability_entitlements_suspend_installations' AND NOT t.tgisinternal;
  IF v_count <> 1 THEN RAISE EXCEPTION 'Entitlement suspension trigger missing'; END IF;
  SELECT count(*) INTO v_count FROM pg_constraint
  WHERE conrelid='catalog.capability_installations'::regclass
    AND conname IN ('capability_installations_entitlement_fk','capability_installations_entitlement_owner_check');
  IF v_count <> 2 THEN RAISE EXCEPTION 'Capability installation entitlement constraints missing'; END IF;
  SELECT p.prosecdef INTO v_definer FROM pg_proc p
  WHERE p.oid='commerce.grant_capability_entitlement_after_acceptance()'::regprocedure;
  IF v_definer IS DISTINCT FROM true THEN RAISE EXCEPTION 'Entitlement grant function must be SECURITY DEFINER'; END IF;
  IF has_function_privilege('anon','commerce.grant_capability_entitlement_after_acceptance()','EXECUTE')
     OR has_function_privilege('authenticated','commerce.grant_capability_entitlement_after_acceptance()','EXECUTE') THEN
    RAISE EXCEPTION 'Browser roles must not execute entitlement grant function';
  END IF;
END
$test$;
