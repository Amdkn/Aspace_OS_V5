-- A'Space Marketplace — Coach OS schema adoption (2026-11-24).
--
-- RECONSTRUCTED CANONICAL SOURCE:
-- The original migration body was not present in the repository branch during
-- the 2026-11-26 reconciliation. This source was reconstructed from the live
-- Marketplace catalog (columns, constraints, policies, grants, indexes and
-- comments) and the recorded adoption scope. It is committed under the exact
-- cloud migration version/name so the repository can represent the deployed
-- baseline. It was NOT re-applied to the live project during reconstruction.
--
-- Adoption scope: identity.profiles, content.cms_collections,
-- content.cms_items. No Coach Auth users or CMS records were transferred.
-- Coach-specific sign-up-organization function/OAuth/Storage artifacts were
-- not copied into Marketplace.

BEGIN;

CREATE SCHEMA content AUTHORIZATION postgres;
REVOKE ALL ON SCHEMA content FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA content TO authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  GRANT ALL ON TABLES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;

CREATE TABLE identity.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name text,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE identity.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY profiles_insert_self ON identity.profiles
  FOR INSERT TO authenticated
  WITH CHECK ((SELECT auth.uid()) = id);

CREATE POLICY profiles_read_self ON identity.profiles
  FOR SELECT TO authenticated
  USING ((SELECT auth.uid()) = id);

CREATE POLICY profiles_update_self ON identity.profiles
  FOR UPDATE TO authenticated
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

GRANT USAGE ON SCHEMA identity TO authenticated;
GRANT SELECT, INSERT, UPDATE ON identity.profiles TO authenticated;
GRANT ALL ON identity.profiles TO service_role;

CREATE TABLE content.cms_collections (
  id text NOT NULL,
  org_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  name text NOT NULL,
  singular text NOT NULL,
  accent text NOT NULL,
  title_field text NOT NULL,
  subtitle_field text,
  badge_field text,
  fields jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (org_id, id)
);

CREATE TABLE content.cms_items (
  id text NOT NULL,
  collection_id text NOT NULL,
  org_id uuid NOT NULL REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  data jsonb NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (org_id, collection_id, id),
  CONSTRAINT cms_items_collection_org_fk
    FOREIGN KEY (org_id, collection_id)
    REFERENCES content.cms_collections(org_id, id) ON DELETE CASCADE
);

ALTER TABLE content.cms_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE content.cms_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY cms_collections_manage_active_org_members ON content.cms_collections
  FOR ALL TO authenticated
  USING (EXISTS (
    SELECT 1
    FROM identity.organization_memberships membership
    WHERE membership.organization_id = cms_collections.org_id
      AND membership.user_id = (SELECT auth.uid())
      AND membership.membership_status = 'ACTIVE'
  ))
  WITH CHECK (EXISTS (
    SELECT 1
    FROM identity.organization_memberships membership
    WHERE membership.organization_id = cms_collections.org_id
      AND membership.user_id = (SELECT auth.uid())
      AND membership.membership_status = 'ACTIVE'
  ));

CREATE POLICY cms_items_manage_active_org_members ON content.cms_items
  FOR ALL TO authenticated
  USING (EXISTS (
    SELECT 1
    FROM identity.organization_memberships membership
    WHERE membership.organization_id = cms_items.org_id
      AND membership.user_id = (SELECT auth.uid())
      AND membership.membership_status = 'ACTIVE'
  ))
  WITH CHECK (EXISTS (
    SELECT 1
    FROM identity.organization_memberships membership
    WHERE membership.organization_id = cms_items.org_id
      AND membership.user_id = (SELECT auth.uid())
      AND membership.membership_status = 'ACTIVE'
  ));

GRANT SELECT, INSERT, UPDATE, DELETE
  ON content.cms_collections, content.cms_items TO authenticated;
GRANT ALL ON content.cms_collections, content.cms_items TO service_role;

COMMENT ON TABLE identity.profiles IS
  'User profile metadata adopted from Coach OS; identity remains anchored to auth.users.';
COMMENT ON TABLE content.cms_collections IS
  'Tenant-scoped collection definitions; org_id references identity.organizations.';
COMMENT ON TABLE content.cms_items IS
  'Tenant-scoped CMS records; collection ownership is enforced by a composite foreign key.';

COMMIT;
