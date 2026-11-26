-- Structural and privilege regression checks for the OAuth one-time state runtime.
DO $test$
DECLARE
  v_rls boolean;
  v_status_check text;
  v_consumption_check text;
BEGIN
  SELECT c.relrowsecurity INTO v_rls
  FROM pg_class c
  WHERE c.oid='integration.adapter_oauth_transactions'::regclass;
  IF v_rls IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'FAIL: OAuth transaction table must keep RLS enabled';
  END IF;

  IF has_table_privilege('anon','integration.adapter_oauth_transactions','SELECT')
     OR has_table_privilege('authenticated','integration.adapter_oauth_transactions','SELECT') THEN
    RAISE EXCEPTION 'FAIL: browser roles must not read OAuth transaction rows';
  END IF;

  SELECT pg_get_constraintdef(oid) INTO v_status_check
  FROM pg_constraint
  WHERE conrelid='integration.adapter_oauth_transactions'::regclass
    AND conname='adapter_oauth_transactions_transaction_status_check';
  IF v_status_check IS NULL OR
     position('PROCESSING' IN v_status_check)=0 OR
     position('COMPLETED' IN v_status_check)=0 OR
     position('EXPIRED' IN v_status_check)=0 THEN
    RAISE EXCEPTION 'FAIL: OAuth transaction status constraint is incomplete';
  END IF;

  SELECT pg_get_constraintdef(oid) INTO v_consumption_check
  FROM pg_constraint
  WHERE conrelid='integration.adapter_oauth_transactions'::regclass
    AND conname='adapter_oauth_transactions_consumption_state_check';
  IF v_consumption_check IS NULL OR
     position('consumed_at' IN v_consumption_check)=0 OR
     position('PROCESSING' IN v_consumption_check)=0 THEN
    RAISE EXCEPTION 'FAIL: consumed-state invariant is missing';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='integration'
      AND indexname='adapter_oauth_transactions_pending_expiry_idx'
  ) THEN
    RAISE EXCEPTION 'FAIL: pending OAuth expiry index is missing';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid='integration.adapter_oauth_transactions'::regclass
      AND contype='u'
      AND pg_get_constraintdef(oid) LIKE '%state_digest%'
  ) THEN
    RAISE EXCEPTION 'FAIL: state digest must remain unique';
  END IF;

  RAISE NOTICE 'PASS: OAuth runtime schema, one-time state constraints, expiry index and browser-role isolation';
END
$test$;
