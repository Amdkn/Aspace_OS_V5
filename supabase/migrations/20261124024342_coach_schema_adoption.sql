-- A'Space Marketplace — Coach OS schema adoption
-- Source: Coach OS Supabase project qjrwcdzaebyqponqkiqs (PostgreSQL 17).
-- Captured 2026-11-24 after source project resumed.
--
-- Source inventory:
--   * public.organizations, public.memberships, public.profiles
--   * public.cms_collections, public.cms_items
--   * 3 applied Coach OS migrations; all five application tables had 0 rows.
--   * No Storage buckets, custom triggers, or custom business SQL functions.
--   * One deployed Edge Function (sign-up-organization v2); its organization
--     creation responsibility is already represented by marketplace-api.
--
-- Adoption mapping:
--   * public.organizations      -> identity.organizations (already exists)
--   * public.memberships        -> identity.organization_memberships +
--                                  identity.role_bindings (already exist)
--   * public.profiles           -> identity.profiles (created here)
--   * public.cms_collections    -> content.cms_collections
--   * public.cms_items          -> content.cms_items
--
-- No source data or migration-history rows are copied. Coach OS tenancy tables
-- are not recreated in public: Marketplace's identity domain is authoritative.
-- Auth provider/settings are not changed here; source and target settings were
-- inspected separately and match. Their localhost site_url is intentionally
-- not treated as production configuration.

BEGIN;

DO $guard$
BEGIN
  IF current_user <> 'postgres' THEN
    RAISE EXCEPTION 'Migration requires postgres; current_user=%', current_user;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
     OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated')
     OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
    RAISE EXCEPTION 'Expected Supabase roles anon, authenticated and service_role';
  END IF;
END
$guard$;

CREATE SCHEMA IF NOT EXISTS content AUTHORIZATION postgres;
REVOKE ALL ON SCHEMA content FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA content TO authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  GRANT ALL ON TABLES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  GRANT ALL ON SEQUENCES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA content
  GRANT EXECUTE ON FUNCTIONS TO service_role;

-- Coach OS profile metadata, relocated out of the PostgREST public schema.
CREATE TABLE identity.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name text,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE identity.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY profiles_read_self ON identity.profiles
  FOR SELECT TO authenticated
  USING ((SELECT auth.uid()) = id);

CREATE POLICY profiles_insert_self ON identity.profiles
  FOR INSERT TO authenticated
  WITH CHECK ((SELECT auth.uid()) = id);

CREATE POLICY profiles_update_self ON identity.profiles
  FOR UPDATE TO authenticated
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

REVOKE ALL ON TABLE identity.profiles FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON TABLE identity.profiles TO authenticated;
GRANT ALL ON TABLE identity.profiles TO service_role;

-- Generic tenant-scoped CMS collections. org_id now points to the canonical
-- Marketplace tenant root instead of the legacy public.organizations table.
CREATE TABLE content.cms_collections (
  id text NOT NULL,
  org_id uuid NOT NULL
    REFERENCES identity.organizations(id) ON DELETE RESTRICT,
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
  org_id uuid NOT NULL
    REFERENCES identity.organizations(id) ON DELETE RESTRICT,
  data jsonb NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (org_id, collection_id, id),
  CONSTRAINT cms_items_collection_org_fk
    FOREIGN KEY (org_id, collection_id)
    REFERENCES content.cms_collections(org_id, id) ON DELETE CASCADE
);

-- The composite primary key on cms_items already supports the source query
-- pattern (org_id, collection_id); no redundant duplicate index is added.

ALTER TABLE content.cms_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE content.cms_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY cms_collections_manage_active_org_members
  ON content.cms_collections
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM identity.organization_memberships AS membership
      WHERE membership.organization_id = cms_collections.org_id
        AND membership.user_id = (SELECT auth.uid())
        AND membership.membership_status = 'ACTIVE'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1
      FROM identity.organization_memberships AS membership
      WHERE membership.organization_id = cms_collections.org_id
        AND membership.user_id = (SELECT auth.uid())
        AND membership.membership_status = 'ACTIVE'
    )
  );

CREATE POLICY cms_items_manage_active_org_members
  ON content.cms_items
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM identity.organization_memberships AS membership
      WHERE membership.organization_id = cms_items.org_id
        AND membership.user_id = (SELECT auth.uid())
        AND membership.membership_status = 'ACTIVE'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1
      FROM identity.organization_memberships AS membership
      WHERE membership.organization_id = cms_items.org_id
        AND membership.user_id = (SELECT auth.uid())
        AND membership.membership_status = 'ACTIVE'
    )
  );

REVOKE ALL ON TABLE content.cms_collections, content.cms_items
  FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE
  ON TABLE content.cms_collections, content.cms_items TO authenticated;
GRANT ALL ON TABLE content.cms_collections, content.cms_items TO service_role;

COMMENT ON SCHEMA content IS
  'Private A''Space content domain; tenant-scoped CMS resources adopted from Coach OS.';
COMMENT ON TABLE identity.profiles IS
  'User profile metadata adopted from Coach OS; identity remains anchored to auth.users.';
COMMENT ON TABLE content.cms_collections IS
  'Tenant-scoped collection definitions; org_id references identity.organizations.';
COMMENT ON TABLE content.cms_items IS
  'Tenant-scoped CMS records; collection ownership is enforced by a composite foreign key.';

COMMIT;
