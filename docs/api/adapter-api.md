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
  "display_name": "Primary provider connection",
  "credentials": { "api_key": "provided-only-over-TLS" }
}
```

For `BEARER`, `API_KEY_HEADER` and `BASIC` manifests, the request may include the matching `credentials` object. The function stores only the selected credential fields in Supabase Vault and stores the Vault UUID reference in the connection row. Raw credentials are never returned or logged. For OAUTH2_AUTH_CODE, omit credentials; credentials are provisioned only by the server-side OAuth callback. The connection remains `PENDING_AUTH` until a health check succeeds.


### start_oauth_authorization
Requires workspace role OWNER or ADMIN and an existing tenant connection whose active manifest uses OAUTH2_AUTH_CODE. Generates 256-bit random state and a PKCE S256 verifier/challenge. Only the SHA-256 state digest is stored in the OAuth transaction; the verifier is stored in Vault. The authorization endpoint must be HTTPS and its hostname must be present in the manifest oauth_allowed_hosts. The server requires provider-specific client ID and client secret environment variables before returning an authorization URL.

```json
{
  "action": "start_oauth_authorization",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "connection_id": "00000000-0000-4000-8000-000000000003"
}
```

The response contains an authorization_url and a 600-second expiry. Treat the URL as a short-lived capability: do not log it or persist it in analytics.

### OAuth callback
The public GET /functions/v1/adapter-oauth-callback function has gateway JWT verification disabled because the provider redirects the browser without a Supabase user JWT. The callback validates the 43-character state, hashes it, and atomically changes a matching unexpired transaction from PENDING to PROCESSING before exchanging the code. A consumed state cannot be replayed. It uses the exact stored redirect URI and PKCE verifier, validates the token endpoint against the manifest host allowlist, checks the returned scopes and stores tokens only in Vault. The callback does not return tokens or provider error details.

### `revoke_connection`
Requires workspace role OWNER or ADMIN. Revokes the connection and cancels queued/retry-wait jobs with append-only cancellation events. For OAuth connections, it attempts the manifest-declared HTTPS provider revocation endpoint before local credential detachment. Local revocation remains authoritative even if remote revocation is unavailable; the response reports provider_revocation as REVOKED, FAILED, NOT_CONFIGURED or NOT_APPLICABLE. Running jobs are not silently rewritten; the worker re-checks connection status before execution.

```json
{
  "action": "revoke_connection",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "connection_id": "00000000-0000-4000-8000-000000000003"
}
```

### `rotate_connection_credentials`
Requires workspace role OWNER or ADMIN. Updates the existing Vault secret (or creates its reference if missing), resets the connection to `PENDING_AUTH`, and requires another health check before execution resumes.

```json
{
  "action": "rotate_connection_credentials",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "connection_id": "00000000-0000-4000-8000-000000000003",
  "credentials": { "api_key": "new-value-provided-only-over-TLS" }
}
```

### `test_connection`
Requires workspace role OWNER or ADMIN. Queues the manifest-declared `health_check` operation with an idempotency key and dispatches the private worker. A successful 2xx response marks the connection `CONNECTED`; a terminal failure marks it `ERROR`.

```json
{
  "action": "test_connection",
  "organization_id": "00000000-0000-4000-8000-000000000001",
  "workspace_id": "00000000-0000-4000-8000-000000000002",
  "connection_id": "00000000-0000-4000-8000-000000000003",
  "idempotency_key": "health-check-2026-11-26-0001"
}
```

### `enqueue_execution`
Requires workspace role OWNER, ADMIN or MEMBER. Requires a CONNECTED connection, ACTIVE manifest, and an operation key declared by that manifest. The idempotency key is unique per connection. Request payload is limited to 64 KB and rejects credential-like field names (token, secret, password, API key, authorization, cookie, private key).

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

The adapter runtime is deployed, but no provider has passed an authorized provider E2E:

- No provider manifest is ACTIVE; Google Drive v1.0.0 exists as DRAFT.
- No tenant connection or OAuth transaction currently exists.
- OAuth Authorization Code + PKCE initiation, callback completion, Vault token storage, token refresh/rotation and local/provider revocation paths are implemented and deployed.
- OAuth2 client-credentials remains unsupported.
- Google Drive v1.0.0 currently declares six metadata operations: health check, list files, get file, create folder, update metadata and delete file. Binary content upload/download and resumable transfer are not in this contract.
- Google Drive uses drive.readonly + drive.file; it does not request the unrestricted drive scope.
- A real Google OAuth Web Client, exact callback configuration, authenticated OWNER/ADMIN tenant and full consent/API/refresh/revoke round-trip are still required before the manifest can become ACTIVE.
- The private adapter-worker Edge Function has gateway JWT verification disabled but enforces an exact service-role bearer in its handler. Only the authenticated adapter API dispatches it internally.
- Webhook receipt storage exists, but provider-specific webhook signature verification and replay-protected webhook ingress remain open.

Do not present Google Drive or any other provider as executable until the worker and provider-specific manifest have been tested against a real authorized provider account.
