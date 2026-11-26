-- A'Space Marketplace Day 2 — order-backed capability entitlement lifecycle
BEGIN;
CREATE TABLE commerce.capability_entitlements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL UNIQUE REFERENCES commerce.orders(id) ON DELETE RESTRICT,
  buyer_organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  seller_organization_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  listing_id uuid NOT NULL REFERENCES catalog.listings(id) ON DELETE RESTRICT,
  capability_id uuid NOT NULL,
  capability_version_id uuid NOT NULL,
  entitlement_status text NOT NULL DEFAULT 'ACTIVE',
  granted_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT capability_entitlements_distinct_parties CHECK (buyer_organization_id <> seller_organization_id),
  CONSTRAINT capability_entitlements_status_check CHECK (entitlement_status IN ('ACTIVE','SUSPENDED','REVOKED','EXPIRED')),
  CONSTRAINT capability_entitlements_revoked_at_check CHECK (
    (entitlement_status = 'REVOKED' AND revoked_at IS NOT NULL) OR entitlement_status <> 'REVOKED'
  ),
  CONSTRAINT capability_entitlements_expiry_check CHECK (expires_at IS NULL OR expires_at > granted_at),
  CONSTRAINT capability_entitlements_id_buyer_capability_version_key UNIQUE (id,buyer_organization_id,capability_id,capability_version_id),
  CONSTRAINT capability_entitlements_capability_version_fk
    FOREIGN KEY (capability_version_id,capability_id)
    REFERENCES catalog.capability_versions(id,capability_id) ON DELETE RESTRICT
);
CREATE INDEX capability_entitlements_buyer_status_idx
  ON commerce.capability_entitlements (buyer_organization_id,entitlement_status,granted_at DESC);
CREATE INDEX capability_entitlements_seller_idx
  ON commerce.capability_entitlements (seller_organization_id,granted_at DESC);
ALTER TABLE commerce.capability_entitlements ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON commerce.capability_entitlements FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON commerce.capability_entitlements TO service_role;

ALTER TABLE catalog.capability_installations
  ADD COLUMN entitlement_id uuid,
  ADD CONSTRAINT capability_installations_entitlement_fk
    FOREIGN KEY (entitlement_id,organization_id,capability_id,capability_version_id)
    REFERENCES commerce.capability_entitlements (id,buyer_organization_id,capability_id,capability_version_id)
    ON DELETE RESTRICT,
  ADD CONSTRAINT capability_installations_entitlement_owner_check CHECK (
    (capability_owner_organization_id = organization_id AND entitlement_id IS NULL)
    OR (capability_owner_organization_id <> organization_id AND entitlement_id IS NOT NULL)
  );
CREATE INDEX capability_installations_entitlement_idx
  ON catalog.capability_installations (entitlement_id) WHERE entitlement_id IS NOT NULL;

CREATE OR REPLACE FUNCTION commerce.grant_capability_entitlement_after_acceptance()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, commerce, catalog
AS $function$
BEGIN
  INSERT INTO commerce.capability_entitlements (
    order_id,buyer_organization_id,seller_organization_id,listing_id,capability_id,capability_version_id
  ) VALUES (
    NEW.id,NEW.buyer_organization_id,NEW.seller_organization_id,NEW.listing_id,NEW.capability_id,NEW.capability_version_id
  ) ON CONFLICT (order_id) DO NOTHING;
  RETURN NEW;
END
$function$;
REVOKE ALL ON FUNCTION commerce.grant_capability_entitlement_after_acceptance() FROM PUBLIC, anon, authenticated;
CREATE TRIGGER orders_grant_capability_entitlement_after_acceptance
AFTER UPDATE OF order_status ON commerce.orders
FOR EACH ROW
WHEN (OLD.order_status IS DISTINCT FROM NEW.order_status AND NEW.order_status = 'ACCEPTED_BY_BUYER')
EXECUTE FUNCTION commerce.grant_capability_entitlement_after_acceptance();

CREATE OR REPLACE FUNCTION commerce.suspend_entitled_capability_installations()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, commerce, catalog
AS $function$
BEGIN
  IF OLD.entitlement_status = 'ACTIVE'
     AND NEW.entitlement_status IN ('SUSPENDED','REVOKED','EXPIRED') THEN
    UPDATE catalog.capability_installations
    SET installation_status = 'SUSPENDED'
    WHERE entitlement_id = NEW.id AND installation_status = 'ACTIVE';
  END IF;
  RETURN NEW;
END
$function$;
REVOKE ALL ON FUNCTION commerce.suspend_entitled_capability_installations() FROM PUBLIC, anon, authenticated;
CREATE TRIGGER capability_entitlements_suspend_installations
AFTER UPDATE OF entitlement_status ON commerce.capability_entitlements
FOR EACH ROW
WHEN (OLD.entitlement_status IS DISTINCT FROM NEW.entitlement_status)
EXECUTE FUNCTION commerce.suspend_entitled_capability_installations();

CREATE OR REPLACE FUNCTION catalog.validate_capability_installation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, enterprise, areas, catalog, commerce
AS $function$
BEGIN
  IF NEW.installation_status <> 'ACTIVE' THEN RETURN NEW; END IF;
  IF NOT enterprise.assert_installation_target(
    NEW.organization_id,NEW.workspace_id,NEW.target_entity_type,NEW.target_installation_id
  ) THEN
    RAISE EXCEPTION 'Capability target does not belong to this organization/workspace';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM catalog.capabilities c
    JOIN catalog.capability_versions v ON v.capability_id=c.id
    WHERE c.id=NEW.capability_id
      AND c.owner_organization_id=NEW.capability_owner_organization_id
      AND c.capability_status='ACTIVE'
      AND v.id=NEW.capability_version_id
      AND v.version_status='ACTIVE'
  ) THEN
    RAISE EXCEPTION 'Capability or capability version is not active';
  END IF;
  IF NEW.capability_owner_organization_id = NEW.organization_id THEN
    IF NEW.entitlement_id IS NOT NULL THEN
      RAISE EXCEPTION 'First-party capability installation must not reference a marketplace entitlement';
    END IF;
  ELSIF NEW.entitlement_id IS NULL OR NOT EXISTS (
    SELECT 1 FROM commerce.capability_entitlements e
    WHERE e.id=NEW.entitlement_id
      AND e.buyer_organization_id=NEW.organization_id
      AND e.seller_organization_id=NEW.capability_owner_organization_id
      AND e.capability_id=NEW.capability_id
      AND e.capability_version_id=NEW.capability_version_id
      AND e.entitlement_status='ACTIVE'
      AND (e.expires_at IS NULL OR e.expires_at > now())
  ) THEN
    RAISE EXCEPTION 'Active marketplace entitlement required for external capability installation';
  END IF;
  RETURN NEW;
END
$function$;
REVOKE ALL ON FUNCTION catalog.validate_capability_installation() FROM PUBLIC, anon, authenticated;
COMMIT;
