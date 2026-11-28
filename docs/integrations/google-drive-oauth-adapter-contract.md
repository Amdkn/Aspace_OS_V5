# Google Drive OAuth 2.0 adapter — implementation contract

**Status:** DESIGN LOCKED / IMPLEMENTATION NOT DEPLOYED  
**Target provider key:** `files-knowledge-google-drive`  
**Blueprint version:** `0.1.0`  
**Target project:** `swegnrvaxxgfrnshdpxx`  
**Repository branch:** `feat/marketplace-taxonomy-blueprints`

This contract is grounded in the live provider blueprint registry and the deployed adapter runtime. It does not claim that Google Drive is connected or executable yet.

## 1. Live baseline

The provider registry contains Google Drive as `files-knowledge-google-drive`, family `files-knowledge`, version `0.1.0`, currently `PLANNED` with `UNSPECIFIED` auth contract.

The deployed `adapter-api` v4 authenticates Supabase users and enforces active workspace membership plus OWNER/ADMIN checks for connection mutations. It currently rejects OAuth credential provisioning. Its action router has no OAuth start/callback action.

The deployed `adapter-worker` v4 validates HTTPS hosts and manifest paths, limits response size and timeouts, sanitizes response data, and authenticates its public platform route by constant-time comparison with the service-role bearer secret. It currently rejects OAuth in `buildHeaders` with `OAUTH_FLOW_NOT_IMPLEMENTED`. The worker's platform JWT verification is disabled intentionally for service-to-service dispatch; the handler itself requires the exact service-role bearer secret.

The existing database already has `integration.adapter_oauth_transactions`, including a unique SHA-256 state digest, Vault reference for the PKCE verifier, redirect URI, expiry and one-use lifecycle. It does not yet have a provider OAuth client registry.

## 2. OAuth security model

- Authorization Code flow with PKCE S256; no implicit flow.
- `state` is 256 bits of cryptographically random entropy. Store only SHA-256(state) in Postgres.
- PKCE verifier is stored only in Supabase Vault; `pkce_secret_id` is the only database reference.
- OAuth client secret is stored only in Vault. The client ID, authorization endpoint, token endpoint, redirect URI, auth method and allowed scopes are non-secret configuration.
- OAuth endpoints must be HTTPS, exact-host allowlisted, and immutable while a transaction is pending.
- Callback has `verify_jwt=false` because Google redirects a browser without a Supabase JWT. The handler must validate state digest, pending status, expiry, provider, manifest version, redirect URI and one-use atomic claim before exchanging the code.
- Callback must reject missing/duplicate query parameters, provider errors, replayed state, expired state, mismatched redirect URI, unexpected token content types and oversized responses.
- Never log authorization codes, state, verifier, access token, refresh token, client secret or raw provider response.
- Persist token material only in Vault. Persist only granted scopes, provider account identifier and non-sensitive metadata in `tenant_connections`.
- Use exact redirect URI equality. Never derive redirect targets from an untrusted query parameter.
- Revocation detaches Vault references, cancels queued jobs and records append-only events. Delete a Vault secret only after confirming that no active connection or OAuth transaction references it.

## 3. Provider client configuration registry (required schema addition)

Add a private, RLS-enabled, service-role-only table `integration.provider_oauth_clients` keyed by (`provider_key`, `manifest_version`) with:

- `client_id` (text, non-secret)
- `client_secret_id` (UUID reference to Vault; nullable only for providers that do not issue a secret)
- `authorization_endpoint` and `token_endpoint` (HTTPS URLs)
- `redirect_uri` (exact registered HTTPS callback URI)
- `client_auth_method` (`client_secret_post` or `client_secret_basic`)
- `enabled` boolean, `created_at`, `updated_at`
- foreign key to the exact provider manifest version
- endpoint-host validation and no secret material in ordinary columns

Only a platform-level provisioning path may create/update this row. Workspace OWNER/ADMIN may initiate a connection but must never be able to replace platform OAuth client credentials.

## 4. Required lifecycle

1. **Provision provider client:** platform operator stores Google OAuth client secret in Vault and registers non-secret client metadata.
2. **Create tenant connection:** authenticated OWNER/ADMIN creates a `PENDING_AUTH` connection for `files-knowledge-google-drive`.
3. **Start OAuth:** authenticated API checks active workspace membership, active manifest and enabled provider client; creates state + PKCE verifier; inserts a 10-minute pending transaction; returns only the authorization URL.
4. **Google consent:** browser redirects to Google's authorization endpoint with `response_type=code`, client ID, exact redirect URI, configured scopes, state, S256 challenge, `access_type=offline`, and `include_granted_scopes=true`. Request refresh token on initial authorization and handle absent refresh tokens on later consent.
5. **Callback:** public callback atomically claims the pending transaction by state digest, reads the PKCE verifier and client secret from Vault, exchanges the code with a fixed token endpoint, validates the response, stores token material in Vault and marks the connection `CONNECTED`.
6. **Refresh:** worker refreshes access tokens before expiry using the refresh token; token rotation replaces the Vault secret atomically. A missing refresh token or revoked consent transitions the connection to `DEGRADED` or `ERROR` and emits a safe event.
7. **Execute:** worker uses the access token as a bearer token and executes only manifest-declared operations on the exact allowlisted Google API host.
8. **Disconnect:** revoke local access immediately, cancel queued jobs, detach Vault reference and attempt provider token revocation as a best-effort follow-up. Local revocation must not depend on Google's availability.

## 5. Google Drive manifest contract

Provider identity:
- `provider_key`: `files-knowledge-google-drive`
- `family_key`: `files-knowledge`
- `manifest_version`: `1.0.0`
- `base_url`: `https://www.googleapis.com/drive/v3`
- `allowed_hosts`: `["www.googleapis.com"]`
- `auth_method`: `OAUTH2_AUTH_CODE`

Initial operation set:
- `health_check`: `GET /about?fields=user(displayName,emailAddress,permissionId)`
- `list_files`: `GET /files`, with explicit fields/pageSize/pageToken/q handling
- `get_file`: `GET /files/{fileId}` (path parameter must be encoded and validated by a manifest-safe path builder)
- `create_folder`: `POST /files`, MIME type `application/vnd.google-apps.folder`
- `update_file_metadata`: `PATCH /files/{fileId}`
- `download_file`: separate media-download operation; response streaming and binary handling must be designed before activation
- `upload_file`: separate resumable upload protocol; do not route large binary bodies through the generic JSON worker

Do not activate the manifest until path parameterization, query allowlists, pagination, file metadata redaction, media streaming, resumable uploads and OAuth refresh are implemented and tested. The current generic worker path builder rejects dynamic path interpolation; it must be extended safely rather than concatenating untrusted file IDs.

## 6. Scope profiles

- **Restricted starter profile:** `https://www.googleapis.com/auth/drive.file` — app-created/opened files only. Good for validating OAuth and basic CRUD without blanket Drive access.
- **Read-only workspace profile:** `https://www.googleapis.com/auth/drive.readonly` — broad read access to the user's Drive. Requires explicit user consent and a clear data-handling explanation.
- **Full workspace profile:** `https://www.googleapis.com/auth/drive` — broad read/write access. Do not request by default; requires explicit product decision, security review and Google's applicable OAuth verification/restricted-scope assessment.

The product must display requested scopes and the consequences before redirecting to Google. Never silently escalate an existing connection's scopes.

## 7. Acceptance gates

- Unit tests: state entropy/digest, PKCE S256, constant-time secret comparison, callback parameter validation, redirect URI exact match, endpoint allowlist, expiry, replay, concurrent callback race, Vault cleanup, token redaction.
- Database tests: private schema grants, RLS, manifest/client FK integrity, one-use transaction state transition, append-only events, no secret values in manifest/config columns.
- API tests: unauthenticated start denied; non-member denied; MEMBER/VIEWER denied; OWNER/ADMIN allowed; client config inaccessible to workspace members.
- Callback tests: valid code exchange; invalid state; expired state; replay; provider denial; token endpoint error; missing refresh token; scope mismatch.
- Worker tests: OAuth bearer header; refresh success and token rotation; refresh failure; no token leakage; only Google API host; dynamic file IDs cannot escape base path.
- Live E2E: authenticated user + organization + workspace + OWNER membership, configured Google OAuth web client, exact callback URI registered in Google Cloud, and a real consent/Drive API round trip.

## 8. External configuration still required

A real Google OAuth Web application client ID and client secret must be created in the owner's Google Cloud project. Register the deployed callback URL exactly, configure the consent screen and authorized scopes, and store the client secret in Supabase Vault. Do not paste secrets into GitHub, migration files, chat, or ordinary database columns.

Until all gates pass, lifecycle status remains `BLUEPRINT ONLY`; the provider blueprint remains `PLANNED`, and no Google Drive connection is claimed.
