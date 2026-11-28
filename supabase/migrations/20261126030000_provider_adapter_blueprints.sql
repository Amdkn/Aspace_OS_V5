-- Provider-level adapter blueprints derived from the canonical 20 family catalog.
-- These rows describe intended provider integrations only; no credentials or runtime connections exist.
BEGIN;

CREATE TABLE integration.provider_adapter_blueprints (
  provider_key text PRIMARY KEY CHECK (provider_key ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  family_key text NOT NULL REFERENCES integration.adapter_family_blueprints(family_key) ON DELETE RESTRICT,
  provider_name text NOT NULL CHECK (length(btrim(provider_name)) > 0),
  manifest_version text NOT NULL DEFAULT '0.1.0',
  implementation_status text NOT NULL DEFAULT 'PLANNED'
    CHECK (implementation_status IN ('PLANNED','IN_PROGRESS','AVAILABLE','DEPRECATED')),
  auth_contract_status text NOT NULL DEFAULT 'UNSPECIFIED'
    CHECK (auth_contract_status IN ('UNSPECIFIED','SPECIFIED','IMPLEMENTED','VERIFIED')),
  supported_operations text[] NOT NULL DEFAULT ARRAY[]::text[],
  documentation_uri text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (family_key, provider_name)
);

ALTER TABLE integration.provider_adapter_blueprints ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE integration.provider_adapter_blueprints FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE integration.provider_adapter_blueprints TO service_role;

CREATE INDEX provider_adapter_blueprints_family_status_idx
  ON integration.provider_adapter_blueprints (family_key, implementation_status);

INSERT INTO integration.provider_adapter_blueprints
  (provider_key, family_key, provider_name, manifest_version, implementation_status, auth_contract_status)
SELECT
  f.family_key || '-' || regexp_replace(lower(btrim(provider_name)), '[^a-z0-9]+', '-', 'g'),
  f.family_key,
  btrim(provider_name),
  '0.1.0',
  'PLANNED',
  'UNSPECIFIED'
FROM integration.adapter_family_blueprints AS f
CROSS JOIN LATERAL unnest(f.provider_examples) AS provider_name
WHERE f.implementation_status <> 'DEPRECATED';

COMMENT ON TABLE integration.provider_adapter_blueprints IS
  'Provider-level adapter design records generated from the 20 family blueprints. PLANNED rows are not executable adapters or tenant connections.';
COMMENT ON COLUMN integration.provider_adapter_blueprints.auth_contract_status IS
  'UNSPECIFIED until a provider-specific auth and scope contract is reviewed and documented; no auth method is inferred from provider name.';
COMMENT ON COLUMN integration.provider_adapter_blueprints.supported_operations IS
  'Empty until provider operations are explicitly specified and tested.';

COMMIT;
