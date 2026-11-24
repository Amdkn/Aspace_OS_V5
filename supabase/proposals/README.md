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
