# A'Space Marketplace — Adapter API contract

**Function:** `adapter-api`  
**Endpoint:** `POST /functions/v1/adapter-api`  
**Deployment:** Supabase Edge Function, JWT verification enabled  
**Repository source:** `supabase/functions/adapter-api/index.ts`

Every request requires a valid Supabase Auth access token:

```http
Authorization: Bearer <user-access-token>
Content-Type: application/json
```

The function authenticates the token with Supabase Auth, then uses a server-side service-role transaction. Tenant and workspace authorization is re-evaluated inside the function; client-supplied role claims are never trusted.

## Actions

### `list_manifests`
Lists only ACTIVE provider manifests and their declared operation keys. Requires an authenticated user. Does not return credentials or secret references.

### `list_connections`
Requires `organization_id` and `workspace_id`. Any active workspace role may list connections. Secret IDs and secret values are not projected.

```json
{
  "action": "list_connections",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002"
}
```

### `create_connection`
Requires workspace role OWNER or ADMIN. The selected provider/version must have an ACTIVE manifest. Creates a tenant/workspace-scoped connection in `PENDING_AUTH`.

```json
{
  "action": "create_connection",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "provider_key": "provider-key",
  "manifest_version": "1.0.0",
  "connection_key": "primary",
  "display_name": "Primary provider connection"
}
```

No raw credentials are accepted by this action. No connection is marked CONNECTED merely because it was created.

### `revoke_connection`
Requires workspace role OWNER or ADMIN. Revokes the connection and cancels queued/retry-wait jobs with append-only cancellation events. Running jobs are not silently rewritten; the future worker must re-check connection status before dispatch.

```json
{
  "action": "revoke_connection",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "connection_id": "00000000-0000-4000-8000-000000000003"
}
```

### `enqueue_execution`
Requires workspace role OWNER, ADMIN or MEMBER. Requires a CONNECTED connection, ACTIVE manifest, and an operation key declared by that manifest. The idempotency key is unique per connection. Request payload is limited to 64 KB.

```json
{
  "action": "enqueue_execution",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "connection_id": "00000000-0000-4000-8000-000000000003",
  "operation_key": "list_records",
  "idempotency_key": "request-2026-11-26-0001",
  "request_payload": { "limit": 25 }
}
```

### `list_executions`
Requires an active workspace role. Returns the latest 100 job summaries without request payloads or secret references.

## Error semantics

- `401`: missing, invalid or expired Auth session.
- `403`: workspace membership/role does not authorize the action.
- `400`: invalid input, inactive manifest/connection, or invalid lifecycle state.
- `404`: unknown action.

## Current implementation boundary

The API and schema foundation are deployed, but the adapter runtime is not complete:

- No provider manifest is currently ACTIVE.
- No tenant connection currently exists.
- `create_connection` deliberately stops at `PENDING_AUTH`; OAuth/credential provisioning and connection health verification are not yet exposed.
- `enqueue_execution` is ready for a CONNECTED connection but no private worker currently claims and executes jobs.
- Provider-specific HTTP dispatch, Vault secret retrieval, response redaction, retries, health checks, webhook signature verification and replay protection remain open implementation work.

Do not present any provider as executable until the worker and provider-specific manifest have been tested against a real authorized provider account.
