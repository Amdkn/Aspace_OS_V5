"""Dream variants — the "dream" (explore) step of the D-N052 R4 loop.

DREAM-RSI (``dream_rsi/orchestrate.py``) repeats explore -> learning ->
promote: the online rollout produces a discovery tree, offline learning
rewrites the policy, the best version explores the next round. The fork's
proposer is a model agent (Gemini CLI / Claude Agent SDK / Codex CLI —
``dream_rsi/agents/``); it rewrites ``policy/method.py`` and each version is
replayed on all replay worlds, once per budget preference
``rho in {0, 0.25, 0.5, 0.75, 1}`` (README, env ``DRSI_REPLAY_BETA_GRID``).

V5 mirror (design §D16 — the adapter defines the backend, the harness V5
executes it): the "policy version" here is a diagnostic rule variant — the
same object the R3 gate promotes (a compiled rule: clauses + SKILL.md +
purpose). The proposer is a DETERMINISTIC variant generator, not a model
agent: it varies, from the compiled R3 rule, the staleness TTL and the
clause subset, plus the R3 negative control. That is a deliberate, named
narrowing of the fork (the fork rewrites arbitrary policy code with a model;
the V5 mirror explores a bounded, auditable neighbourhood of the one real
rule). No model call, no network call — the whole loop is offline and
replayable.

Variants (all derived from the compile trace ``h-p2-3-20261111-1245``):

* ``incumbent`` — the R3 rule ``stale_writer_lock`` itself (TTL 86 400 s,
  2 clauses), compiled by ``aqua_gate.compile_rule_from_trace``. The
  incumbent policy of the loop; Dream keeps it when no rewrite beats it
  (``orchestrate.py``: ``evaluate_incumbent=True``, "may keep the
  incumbent").
* ``v-tight-1h`` — same clauses, TTL 3 600 s (1 h).
* ``v-loose-7d`` — same clauses, TTL 604 800 s (7 d).
* ``v-single-clause`` — only the ``lock_holder_stale`` clause, TTL 86 400 s.
* ``v-regress`` — the R3 negative control ``running_means_defect``
  (``aqua_gate.regressing_rule_variant``): any running workflow is DEFECT.

Every variant is a full rule dict (``aqua_gate`` shape) so the gate runner
consumes it unchanged (``gate_runner.proposal_of``). The ``dream`` block
records the variant's provenance (generator, parent rule, TTL, clauses)
and its RRSI edit tag (component ``skill`` — every variant is a skill
edit; see ``dream_loop.py`` for why novelty is therefore 0).
"""

from __future__ import annotations

import copy

import aqua_gate as ag

# TTL variants of the incumbent rule (seconds). 1 h and 7 d are exactly the
# bounds of the TTL-robustness interval measured in R3 (classification
# invariant for any TTL in [1 h, 7 d] on the R3 snapshot) — the dream
# probes the edges of the interval the data cannot distinguish.
TTL_VARIANTS_S = (3_600, 604_800)

VARIANT_NAMES = (
    "incumbent",
    "v-tight-1h",
    "v-loose-7d",
    "v-single-clause",
    "v-regress",
)


def _retitle(rule: dict, name: str, ttl_s: int, clauses: list[dict]) -> dict:
    """A copy of ``rule`` with a new name, TTL and clause set.

    The SKILL.md / purpose keep the incumbent's text (they describe the
    same invariant); the name and the machine clauses are what changes.
    The ``dream`` block names the generator so the variant is never
    mistaken for a model-written policy.
    """
    variant = copy.deepcopy(rule)
    variant["name"] = name
    variant["clauses"] = clauses
    variant["dream"] = {
        "proposer": "deterministic-variant-generator (V5 mirror — no model call)",
        "parent_rule": rule["name"],
        "parent_source_trace": rule["source_trace"],
        "ttl_s": ttl_s,
        "n_clauses": len(clauses),
        "clause_kinds": [c["kind"] for c in clauses],
    }
    variant["skill_md"] = variant["skill_md"].replace(
        "name: stale_writer_lock", f"name: {name}", 1
    )
    variant["purpose_md"] = (
        f"Origin: Dream variant {name} of {rule['name']} "
        f"(TTL {ttl_s} s, {len(clauses)} clause(s)).\n"
        + variant["purpose_md"]
    )
    return variant


def generate_variants(compile_trace: dict, trace_by_wid: dict, ref) -> dict:
    """Dream (explore): produce the candidate policy versions.

    Returns ``{name: rule}`` in deterministic order (incumbent first).
    The incumbent is compiled from the real trace by the R3 compiler;
    the challengers are its deterministic TTL / clause-subset variants.
    """
    incumbent = ag.compile_rule_from_trace(compile_trace, trace_by_wid, ref)
    variants: dict[str, dict] = {"incumbent": incumbent}
    for name, ttl_s in (("v-tight-1h", 3_600), ("v-loose-7d", 604_800)):
        clauses = [
            {"kind": "lock_holder_stale", "ttl_s": ttl_s},
            {"kind": "running_stale", "ttl_s": ttl_s},
        ]
        variants[name] = _retitle(incumbent, name, ttl_s, clauses)
    single = _retitle(
        incumbent,
        "v-single-clause",
        ag.TTL_STALE_S,
        [{"kind": "lock_holder_stale", "ttl_s": ag.TTL_STALE_S}],
    )
    variants["v-single-clause"] = single
    regress = ag.regressing_rule_variant()
    # The gate maps active skills to machine clauses BY RULE NAME
    # (gate_runner.active_rules): the variant's name must be its key.
    # Keep the R3 control's identity in the dream block / note.
    regress["name"] = "v-regress"
    regress["skill_md"] = regress["skill_md"].replace(
        "name: running_means_defect", "name: v-regress", 1)
    regress["dream"] = {
        "proposer": "deterministic-variant-generator (V5 mirror — no model call)",
        "parent_rule": "stale_writer_lock (misread)",
        "parent_source_trace": "h-p2-3-20261111-1245 (misread)",
        "ttl_s": 0,
        "n_clauses": 1,
        "clause_kinds": ["running_any"],
    }
    variants["v-regress"] = regress
    return variants


def variant_cost(rule: dict, n_traces: int) -> int:
    """RRSI cost proxy C for a variant: clause-evaluations on the split.

    The fork's C is inference tokens (``rrsi/evaluate.py``: ``C_hat``).
    The V5 mirror has no model call, so the measured cost is the work the
    harness backend does to grade the variant: one clause evaluation per
    trace per clause. Deterministic, comparable across variants, and the
    relative change ``(C' - C_t) / C_t`` is what Algorithm 2 consumes.
    """
    return len(rule["clauses"]) * n_traces


def critic_screen(rule: dict) -> tuple[bool, str]:
    """RRSI critic screen (``rrsi/critic.py`` pattern): no suite-specific logic.

    The critic screens every candidate for suite-specific logic BEFORE it
    is evaluated. The V5 screen checks the machine-readable part of the
    variant (its clauses): no trace id, no workflow id, no literal that
    names one trace of the pool. The SKILL.md / purpose may carry provenance
    text (which trace the rule was compiled from — as the fork's prompts
    carry task text); the LOGIC (clauses) must be generic. A variant that
    hard-codes a trace id in a clause is critic-rejected, never evaluated.
    """
    import re

    blob = __import__("json").dumps(rule["clauses"], ensure_ascii=False)
    hit = re.search(r"(h-p2-|smoke-|wid-2026|2026110|2026111)", blob)
    if hit:
        return False, f"critic_reject: clause mentions trace literal {hit.group(0)!r}"
    return True, "critic pass: clauses contain no trace literal"
