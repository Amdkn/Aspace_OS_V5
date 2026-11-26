# A'Space Marketplace — Supabase Cloud Foundation

**Status: DEPLOYED AND VERIFIED**  
**Project:** `swegnrvaxxgfrnshdpxx` (single cloud environment for the current build)  
**Migration:** `20261124000100_identity_tenant_foundation`

## Applied foundation

The first cloud migration creates the private domain schemas `identity`, `areas`, `enterprise`, `catalog`, `commerce`, `operations`, `trust`, `integration`, `finance`, and `api`.

It creates four identity tables:
- `identity.organizations`
- `identity.organization_memberships`
- `identity.delegations`
- `identity.role_bindings`

RLS is enabled on all four tables. Authenticated access is SELECT-only and constrained by row policies. Writes remain server-mediated; `service_role` is server-side only.

The migration also removes broad default grants for future postgres-owned objects in `public` and establishes least-privilege defaults for the private domain schemas.

## Cloud verification — 2026-11-24

- Migration history contains `20261124000100_identity_tenant_foundation`.
- Supabase reports exactly four tables in `identity`.
- All four tables report `relrowsecurity = true`.
- Four SELECT policies are present, one per table.
- The other nine domain schemas exist and are empty, ready for subsequent Day 1/Day 2 implementation.
- No local database or container is required.
- No second Supabase project was created.

## Execution boundary

This is the canonical applied migration. Future schema changes must be added as versioned migrations under `supabase/migrations/`, applied to this cloud project, and verified against the resulting cloud state. Do not keep a parallel proposal copy.


## Marketplace taxonomy blueprints — 2026-11-26

**Migration:** `20261126024200_marketplace_taxonomy_blueprints`  
**Status:** applied to `swegnrvaxxgfrnshdpxx` and verified.

Two independent global reference tables now exist:

- `areas.domain_blueprints`: eight Areas OS mission portfolios, LD01–LD08.
- `enterprise.department_blueprints`: eight Business Marketplace departments, B2.1–B2.8.

Both tables are in private schemas, have RLS enabled, and grant no table access to `PUBLIC`, `anon`, or `authenticated`. The server-side `marketplace-api` Edge Function reads them using its service-role database connection and exposes only the two static reference lists through a public, read-only action. This action is intentionally available to the app's publishable/anon client because the blueprints contain no tenant data or secrets. All table access remains private; the client never queries these schemas directly.

The migration inserted exactly eight rows in each table. These are global blueprints, not organization installations. It did not create tenants, mutate memberships, add role bindings, or link any customer capability to a domain.

The Edge Function now exposes the authenticated read action `list_taxonomy_blueprints` and reports version `0.4.0`. Deployment metadata reports version 4 / ACTIVE; its unauthenticated health endpoint returned HTTP 200 and version 0.4.0.

**Not yet verified:** the authenticated `list_taxonomy_blueprints` call from a real signed-in browser session. The app integration will show a Supabase-source label only after the function returns the expected 8+8 payload; otherwise it retains the clearly labeled local reference fallback.
