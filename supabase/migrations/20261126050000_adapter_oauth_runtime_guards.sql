BEGIN;

-- A callback claims the transaction before exchanging the authorization code.
-- PROCESSING is intentionally terminal for state reuse: retries must restart authorization.
ALTER TABLE integration.adapter_oauth_transactions
  DROP CONSTRAINT adapter_oauth_transactions_transaction_status_check;

ALTER TABLE integration.adapter_oauth_transactions
  ADD CONSTRAINT adapter_oauth_transactions_transaction_status_check
  CHECK (transaction_status IN ('PENDING','PROCESSING','COMPLETED','FAILED','EXPIRED','REVOKED'));

ALTER TABLE integration.adapter_oauth_transactions
  DROP CONSTRAINT adapter_oauth_transactions_check1;

ALTER TABLE integration.adapter_oauth_transactions
  ADD CONSTRAINT adapter_oauth_transactions_consumption_state_check
  CHECK (
    (transaction_status IN ('PROCESSING','COMPLETED','FAILED') AND consumed_at IS NOT NULL)
    OR
    (transaction_status IN ('PENDING','EXPIRED','REVOKED') AND consumed_at IS NULL)
  );

CREATE INDEX adapter_oauth_transactions_pending_expiry_idx
  ON integration.adapter_oauth_transactions (expires_at)
  WHERE transaction_status = 'PENDING';

COMMENT ON COLUMN integration.adapter_oauth_transactions.consumed_at IS
  'Atomic one-time state claim timestamp. Set before any external token exchange; never cleared.';

COMMIT;
