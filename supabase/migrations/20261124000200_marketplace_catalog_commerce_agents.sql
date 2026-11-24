-- A'Space Marketplace Day 2 — persisted catalog, orders and agent principals
BEGIN;
CREATE TABLE identity.agent_principals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  agent_key text NOT NULL CHECK (agent_key ~ '^[A-Z0-9][A-Z0-9._-]{1,95}$'),
  display_name text NOT NULL CHECK (length(btrim(display_name)) > 0),
  agent_class text NOT NULL CHECK (agent_class IN ('GOVERNANCE','ORCHESTRATOR','AREA_OWNER','DEPARTMENT_OWNER','MANAGER','TECHNICIAN','SPECIALIST')),
  runtime text NOT NULL CHECK (length(btrim(runtime)) > 0),
  principal_status text NOT NULL DEFAULT 'ACTIVE' CHECK (principal_status IN ('ACTIVE','SUSPENDED','REVOKED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, agent_key),
  UNIQUE (id, organization_id)
);
CREATE INDEX agent_principals_org_status_idx ON identity.agent_principals (organization_id, principal_status);

CREATE TABLE identity.agent_delegations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  agent_principal_id uuid NOT NULL,
  delegator_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  scope_type text NOT NULL CHECK (scope_type IN ('PLATFORM','ORGANIZATION','AREA','ENTERPRISE','DEPARTMENT','PROJECT','RESOURCE')),
  scope_id uuid,
  permission_codes text[] NOT NULL CHECK (cardinality(permission_codes) > 0),
  delegation_status text NOT NULL DEFAULT 'ACTIVE' CHECK (delegation_status IN ('ACTIVE','REVOKED','EXPIRED')),
  starts_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT agent_delegation_agent_org_fk FOREIGN KEY (agent_principal_id, organization_id)
    REFERENCES identity.agent_principals (id, organization_id) ON DELETE RESTRICT,
  CONSTRAINT agent_delegation_scope_shape CHECK (
    (scope_type IN ('PLATFORM','ORGANIZATION') AND scope_id IS NULL)
    OR (scope_type IN ('AREA','ENTERPRISE','DEPARTMENT','PROJECT','RESOURCE') AND scope_id IS NOT NULL)),
  CONSTRAINT agent_delegation_time_window CHECK (expires_at IS NULL OR expires_at > starts_at),
  CONSTRAINT agent_delegation_revocation_shape CHECK (
    (delegation_status = 'REVOKED' AND revoked_at IS NOT NULL)
    OR delegation_status <> 'REVOKED')
);
CREATE INDEX agent_delegations_agent_status_idx ON identity.agent_delegations (agent_principal_id, delegation_status);
CREATE INDEX agent_delegations_delegator_idx ON identity.agent_delegations (organization_id, delegator_user_id, delegation_status);

CREATE TABLE catalog.capabilities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  capability_key text NOT NULL CHECK (capability_key ~ '^[a-z0-9][a-z0-9._-]{1,95}$'),
  current_version integer NOT NULL DEFAULT 1 CHECK (current_version > 0),
  capability_status text NOT NULL DEFAULT 'ACTIVE' CHECK (capability_status IN ('ACTIVE','SUSPENDED','ARCHIVED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_organization_id, capability_key),
  UNIQUE (id, owner_organization_id)
);
CREATE INDEX capabilities_owner_status_idx ON catalog.capabilities (owner_organization_id, capability_status);

CREATE TABLE catalog.capability_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  capability_id uuid NOT NULL REFERENCES catalog.capabilities(id) ON DELETE RESTRICT,
  version integer NOT NULL CHECK (version > 0),
  name text NOT NULL CHECK (length(btrim(name)) > 0),
  purpose text NOT NULL CHECK (length(btrim(purpose)) > 0),
  input_contract jsonb NOT NULL DEFAULT '{}'::jsonb,
  output_contract jsonb NOT NULL DEFAULT '{}'::jsonb,
  permission_codes text[] NOT NULL DEFAULT ARRAY[]::text[],
  version_status text NOT NULL DEFAULT 'ACTIVE' CHECK (version_status IN ('ACTIVE','DEPRECATED','RETIRED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (capability_id, version),
  UNIQUE (id, capability_id)
);

CREATE TABLE catalog.listings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  listing_key text NOT NULL CHECK (listing_key ~ '^[a-z0-9][a-z0-9._-]{1,95}$'),
  owner_organization_id uuid NOT NULL,
  capability_id uuid NOT NULL,
  capability_version_id uuid NOT NULL,
  version integer NOT NULL DEFAULT 1 CHECK (version > 0),
  title text NOT NULL CHECK (length(btrim(title)) > 0),
  description text NOT NULL CHECK (length(btrim(description)) > 0),
  price_amount numeric(14,2) NOT NULL CHECK (price_amount >= 0),
  currency char(3) NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
  acceptance_criteria text[] NOT NULL CHECK (cardinality(acceptance_criteria) > 0),
  listing_status text NOT NULL DEFAULT 'DRAFT' CHECK (listing_status IN ('DRAFT','PUBLISHED','SUSPENDED','ARCHIVED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz,
  CONSTRAINT listing_owner_capability_fk FOREIGN KEY (capability_id, owner_organization_id)
    REFERENCES catalog.capabilities (id, owner_organization_id) ON DELETE RESTRICT,
  CONSTRAINT listing_capability_version_fk FOREIGN KEY (capability_version_id, capability_id)
    REFERENCES catalog.capability_versions (id, capability_id) ON DELETE RESTRICT,
  UNIQUE (owner_organization_id, listing_key, version),
  UNIQUE (id, owner_organization_id)
);
CREATE INDEX listings_discovery_idx ON catalog.listings (listing_status, created_at DESC);
CREATE INDEX listings_owner_idx ON catalog.listings (owner_organization_id, listing_status);

CREATE TABLE commerce.orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_number text NOT NULL UNIQUE,
  idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 8 AND 200),
  buyer_organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  seller_organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  listing_id uuid NOT NULL REFERENCES catalog.listings(id) ON DELETE RESTRICT,
  listing_version integer NOT NULL CHECK (listing_version > 0),
  capability_id uuid NOT NULL REFERENCES catalog.capabilities(id) ON DELETE RESTRICT,
  capability_version_id uuid NOT NULL REFERENCES catalog.capability_versions(id) ON DELETE RESTRICT,
  listing_title_snapshot text NOT NULL,
  price_amount_snapshot numeric(14,2) NOT NULL CHECK (price_amount_snapshot >= 0),
  currency_snapshot char(3) NOT NULL CHECK (currency_snapshot ~ '^[A-Z]{3}$'),
  acceptance_criteria_snapshot text[] NOT NULL,
  order_status text NOT NULL DEFAULT 'PLACED' CHECK (order_status IN ('PLACED','ACCEPTED','REJECTED','IN_PROGRESS','DELIVERED','ACCEPTED_BY_BUYER','CANCELLED','DISPUTED')),
  created_by_user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT order_parties_differ CHECK (buyer_organization_id <> seller_organization_id),
  UNIQUE (buyer_organization_id, idempotency_key)
);
CREATE INDEX orders_buyer_idx ON commerce.orders (buyer_organization_id, created_at DESC);
CREATE INDEX orders_seller_idx ON commerce.orders (seller_organization_id, created_at DESC);
CREATE INDEX orders_status_idx ON commerce.orders (order_status, updated_at DESC);

CREATE TABLE commerce.order_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL REFERENCES commerce.orders(id) ON DELETE RESTRICT,
  sequence_number integer NOT NULL CHECK (sequence_number > 0),
  from_status text,
  to_status text NOT NULL CHECK (to_status IN ('PLACED','ACCEPTED','REJECTED','IN_PROGRESS','DELIVERED','ACCEPTED_BY_BUYER','CANCELLED','DISPUTED')),
  actor_type text NOT NULL CHECK (actor_type IN ('HUMAN','AGENT','SYSTEM')),
  actor_user_id uuid REFERENCES auth.users(id) ON DELETE RESTRICT,
  actor_agent_principal_id uuid REFERENCES identity.agent_principals(id) ON DELETE RESTRICT,
  actor_organization_id uuid REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  reason text NOT NULL CHECK (length(btrim(reason)) > 0),
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT order_event_actor_shape CHECK (
    (actor_type = 'HUMAN' AND actor_user_id IS NOT NULL AND actor_agent_principal_id IS NULL)
    OR (actor_type = 'AGENT' AND actor_user_id IS NULL AND actor_agent_principal_id IS NOT NULL)
    OR (actor_type = 'SYSTEM' AND actor_user_id IS NULL AND actor_agent_principal_id IS NULL)),
  UNIQUE (order_id, sequence_number)
);
CREATE INDEX order_events_order_idx ON commerce.order_events (order_id, sequence_number);

ALTER TABLE identity.agent_principals ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.agent_delegations ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.capability_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.order_events ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON ALL TABLES IN SCHEMA identity FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA identity FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA catalog FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA catalog FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA commerce FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA commerce FROM PUBLIC, anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA identity TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA identity TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA catalog TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA catalog TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA commerce TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA commerce TO service_role;

REVOKE UPDATE, DELETE, TRUNCATE ON commerce.order_events FROM service_role;
CREATE OR REPLACE FUNCTION api.reject_order_event_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
  RAISE EXCEPTION 'commerce.order_events is append-only';
END;
$$;
REVOKE ALL ON FUNCTION api.reject_order_event_mutation() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION api.reject_order_event_mutation() TO service_role;
CREATE TRIGGER order_events_append_only
  BEFORE UPDATE OR DELETE ON commerce.order_events
  FOR EACH ROW EXECUTE FUNCTION api.reject_order_event_mutation();

COMMENT ON TABLE identity.agent_principals IS 'Agent identities are service principals, not synthetic auth.users.';
COMMENT ON TABLE identity.agent_delegations IS 'Explicit human-to-agent delegation with organization, scope, permissions and validity.';
COMMENT ON TABLE catalog.capabilities IS 'Stable provider-owned capability identity; versions are immutable contract snapshots.';
COMMENT ON TABLE catalog.capability_versions IS 'Versioned capability contract: inputs, outputs and permission codes.';
COMMENT ON TABLE catalog.listings IS 'Commercial offer referencing an exact capability version and immutable listing version.';
COMMENT ON TABLE commerce.orders IS 'Buyer/seller transaction record with immutable commercial snapshots and idempotency.';
COMMENT ON TABLE commerce.order_events IS 'Append-only order lifecycle event stream; UPDATE/DELETE are blocked.';
COMMIT;