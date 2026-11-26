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

**Initial migration:** `20261126024200_marketplace_taxonomy_blueprints`  
**Corrective migration:** `20261126024800_correct_marketplace_department_taxonomy`  
**Project:** `swegnrvaxxgfrnshdpxx`  
**Status:** both migrations applied and verified.

Two independent global reference tables exist:

- `areas.domain_blueprints`: eight Areas OS mission portfolios, LD01–LD08.
- `enterprise.department_blueprints`: eight Marketplace operating departments, keyed by stable slugs such as `product-ip` and `growth-distribution`.

The initial migration briefly seeded the department table with B2.1–B2.8. A source review of the canonical LD01 files showed those codes actually belong to LD01's internal delegation hierarchy, not to the Marketplace department list. The corrective migration renamed the key to `department_key`, removed the erroneous B2 rows, and seeded the eight actual operating departments. This correction was applied and verified; department taxonomy version is now `1.0.1`.

Both tables are in private schemas, have RLS enabled, and grant no table access to `PUBLIC`, `anon`, or `authenticated`. The server-side `marketplace-api` Edge Function reads them using its service-role database connection and exposes only the two static reference lists through public, read-only actions. This is intentionally available to the app's publishable/anon client because the blueprints contain no tenant data or secrets. All table access remains private; the client never queries these schemas directly.

The migration set inserted exactly eight rows in each table. These are global blueprints, not organization installations. It did not create tenants, mutate memberships, add role bindings, or link any customer capability to a domain.

The canonical V5 LD01 source separately defines B1 Book (OwnerBook), eight B2 tactical DC Managers (Operations, Tresorerie, Legal, R&D, Alliances, Infra, IT, Gouvernance), and eight B3 Marvel execution squads (each with seven specialists plus an operational runbook). The frontend shows this hierarchy inside LD01 details; it is not mislabeled as the Marketplace department taxonomy. The LD01 holarchy is not yet persisted as a separate blueprint table.

The Edge Function exposes `list_taxonomy_blueprints` and `browse_listings` as public, read-only actions, reports API version `0.4.0`, and is deployed as function version 7 / ACTIVE. Both actions were invoked with the publishable/anon key and returned HTTP 200; taxonomy returned exactly 8+8 records, while the published catalogue returned an empty array.


## Adapter family blueprints — 2026-11-26

**Migration:** `20261126025300_adapter_family_blueprints`  
**Table:** `integration.adapter_family_blueprints`  
**Status:** applied to `swegnrvaxxgfrnshdpxx`, 20 rows verified.

The table stores 20 global integration-family blueprints with stable keys, display names, provider examples, icon keys, ordering, taxonomy version and an explicit implementation lifecycle. All 20 are currently `PLANNED`.

The table is private, RLS-enabled and service-role-only. The public read-only `marketplace-api/list_adapter_families` action exposes only the reference family catalog. It does not expose credentials, tenant connections, OAuth state or runtime health.

The endpoint was invoked with the publishable/anon key and returned HTTP 200 with exactly 20 records. This is a family registry, not 20 shipped provider adapters. Provider-specific manifests, scopes, credentials, tenant connections, sync/webhook runtime and health checks remain unimplemented.

The Edge Function is deployed as version 8 / ACTIVE and reports API version `0.5.0`.


## Provider-level adapter blueprints — 2026-11-26

**Migration:** `20261126030000_provider_adapter_blueprints`  
**Table:** `integration.provider_adapter_blueprints`  
**API:** `marketplace-api` v0.6.0 / deployed function version 9  
**Status:** applied and verified.

The migration generated 73 provider-level blueprint records from the provider examples stored in the 20 adapter-family records. Each provider record has a stable family-scoped key, family reference, provider name and manifest version.

All 73 records deliberately remain:
- `implementation_status = PLANNED`
- `auth_contract_status = UNSPECIFIED`
- `supported_operations = {}`
- `documentation_uri = NULL`

No authentication method, OAuth scope, API endpoint, webhook or permission is inferred from a provider name. These are normalized design inventory records, not executable adapters or tenant connections.

The table is private, RLS-enabled and service-role-only. The public read-only `marketplace-api/list_provider_adapter_blueprints` action returns the 73 catalog records and supports an optional `family_key` filter. An anonymous invocation returned HTTP 200 with 73 records. A database integrity query confirmed 73 providers across all 20 families, all planned, all auth contracts unspecified and all supported-operation arrays empty.

Provider-specific auth/scope contracts, executable manifests, tenant connections, secret references, sync/webhook execution and health checks remain separate implementation work.
