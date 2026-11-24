# D1-09 Supabase tenant foundation — proposal only

**Status: NOT APPROVED / NOT DEPLOYABLE.**  
**Source design:** [D1-09 — Canonical PostgreSQL Schema & Security Migration Design](https://docs.google.com/document/d/1i9TOd4HsRUUR7c7uWktIhJXYXfOXNVclgjzjOWEPJfk/edit)  
**Baseline:** [D1-08 — Supabase Baseline & Security Audit](https://docs.google.com/document/d/14irNCJhhQ-udW-VL3fnqSbs_ng6KKQZFoenOLUVVGdw/edit)

## Why this folder is named proposals

These SQL files are deliberately outside `supabase/migrations/`. Supabase CLI migration commands do not discover them as deployable migrations. They are versioned design artifacts for review only.

Do not copy them into an active migration directory, run `supabase db push`, link this branch to the production project, or apply them to the selected hosted Supabase project until:
- D1-09 ARB-09 (BD01–BD08 vs DEPT-01–DEPT-08 crosswalk) is resolved.
- ARB-10 (private schemas + API facade vs Edge Functions-only) is approved.
- ARB-11 (agent/service identity and delegated execution) is approved.
- Backup/restore and SSL gates in D1-08 are resolved.
- Default ACL ownership and migration execution role are confirmed.
- A separate local/staging test run and independent SQL/security review pass.

## Proposed contents

- `migrations/20261124000100_identity_tenant_foundation.sql`: private domain schema scaffolding and first identity tables (organizations, memberships, delegations, role bindings), explicit RLS, authenticated read-only policies, server-mediated writes.
- `tests/tenant_rls_assertions.sql`: disposable local-only SQL assertions for two-tenant visibility, role/delegation visibility, RLS enablement and privilege denial. It inserts synthetic Auth users inside a transaction and rolls everything back.

## Design choices / deliberate restrictions

- Auth users authenticate humans; `identity.organization_memberships` and `identity.role_bindings` are the authorization source.
- The A0/A1/A2/A3/B1/B2/B3 role hierarchy is stored as scoped role codes; it is not flattened to a generic admin/member model.
- Delegation is an explicit record with grantor, grantee, organization, scope, permissions and validity.
- A delegation does not silently grant organization membership.
- The first foundation grants authenticated users SELECT only. No client INSERT/UPDATE/DELETE policies are created. Writes must go through reviewed trusted server-side operations.
- `service_role` remains server-side only. It must never be placed in a browser, agent prompt, customer install or log.
- The Data API exposed-schema configuration is not changed; D1-08 observed `public,graphql_public`.
- The existing `public.ensure_rls` event trigger is not treated as coverage for custom schemas; each identity table explicitly enables RLS.

## Validation status

- Static review: prepared against D1-08/D1-09 design constraints.
- Database execution: NOT RUN.
- Supabase advisor: NOT RUN on this branch.
- Local tenant/RLS assertions: NOT RUN.
- Hosted Supabase project: UNCHANGED.

The test script is intentionally not in the normal `supabase/tests` path yet. First verify the migration and fixture SQL on a disposable local Supabase stack, then move it into the standard test layout as part of the approved implementation.
