# A'Space Marketplace — Day 1 Domain Core

**Status:** additive implementation candidate; not production-ready.

Implements versioned provider-owned capabilities, draft/published/suspended listings, Decimal-based prices, immutable order-term snapshots, guarded buyer/seller order transitions, and idempotent order creation. The append-only order history is in memory only.

**Not implemented:** database persistence, authentication, production authorization, durable audit, concurrency control, payments, escrow, payout, refund, tax/accounting, dispute adjudication, agent dispatch, external workflow, API, or legal guarantee. Caller-supplied organization IDs are not identity proof. Do not expose this core to a live marketplace until those controls and integrations are designed, built, and independently reviewed.

Run from repository root:

\`\`\`bash
PYTHONPATH=01_Forkable/FKB07_Money_Maker python -m unittest discover -s 01_Forkable/FKB07_Money_Maker/marketplace_core/tests -v
\`\`\`

This package is additive and does not replace the legacy \`aspace_marketplace_engine.py\`. The six market surfaces, eight Business Departments, eight Areas OS domains, and LD01 B2.1–B2.8 taxonomy remain distinct architectural axes.
