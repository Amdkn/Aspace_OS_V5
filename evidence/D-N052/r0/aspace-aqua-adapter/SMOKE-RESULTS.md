# SMOKE-RESULTS — aspace-aqua-adapter (D-N052 R0)

**Bilan : 6/6 PASS, 0,195 s. Base non modifiée (sha256 avant == après).**

## Commande

```bash
cd ~/workspace/v4-factory/evidence/D-N052/r0/aspace-aqua-adapter
python3 smoke_test.py
```

## Sortie (intégrale)

```
test_cli_writes_jsonl_and_does_not_touch_the_db (__main__.TestAquaFactoryReader.test_cli_writes_jsonl_and_does_not_touch_the_db) ... ok
test_database_is_not_modified (__main__.TestAquaFactoryReader.test_database_is_not_modified) ... ok
test_empty_workflow_is_emitted_not_dropped (__main__.TestAquaFactoryReader.test_empty_workflow_is_emitted_not_dropped) ... ok
test_failure_workflow_carries_tool_error (__main__.TestAquaFactoryReader.test_failure_workflow_carries_tool_error) ... ok
test_success_workflow_mapping (__main__.TestAquaFactoryReader.test_success_workflow_mapping) ... ok
test_three_traces_in_created_order (__main__.TestAquaFactoryReader.test_three_traces_in_created_order) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.195s

OK
```

## Ce que le smoke vérifie

Base temporaire construite avec le schéma copié verbatim de
`02_Factory/factory.ps1` (lignes 42–95) et 3 workflows connus :

| Workflow | Contenu | Attendu vérifié |
|---|---|---|
| `req-smoke-ok` | 2 steps en succès (ryan, clara), 1 event `COMPLETED`, 1 ticket | 2 turns, `turn_id` `wf-ok:step-1/2`, événements user (task) + modèle (output, author = agent), configs ryan + clara, provenance `verdict: success`, `model_pool` verbatim, event en jalons, ticket joint |
| `req-smoke-fail` | step 1 succès, step 2 `failed` sans output, 3 attempts, 1 event `FAILED` | provenance `verdict: failure`, turn 2 = user event (« Run suite ») + événement modèle avec **une seule partie `function_response` nommée `tool_error`** (`error: failed`, `step_key: step-2`, `agent: bill`, `attempts: 3`), ticket `null` |
| `req-smoke-empty` | aucun step, aucun event, statut `running` | émis, pas abandonné : `turns: []`, `agents: {}`, `verdict: in_progress` |

Lecture seule prouvée : `sha256` du fichier base identique avant/après
`read_traces` (appelé 2×) et après le CLI `--db --out` (3 lignes JSONL,
`eval_case_id` dans l'ordre `created_at`).

## Exemple de trace émise (workflow en échec, extrait)

```json
{"eval_case_id": "req-smoke-fail",
 "agent_data": {
  "agents": {
   "ryan": {"agent_id": "ryan",
            "instruction": "Worker V5 — Compagnon ryan (harness python).",
            "description": "Agent observé V5 — trace factory.sqlite, workflow wf-fail, worktree /work/pi."},
   "bill": {"agent_id": "bill",
            "instruction": "Worker V5 — Compagnon bill (harness python).",
            "description": "Agent observé V5 — trace factory.sqlite, workflow wf-fail, worktree /work/pi."}},
  "turns": [
   {"turn_index": 0, "turn_id": "wf-fail:step-1",
    "events": [
     {"author": "user", "content": {"role": "user", "parts": [{"text": "Prepare"}]},
      "event_time": "2026-11-10T15:01:00-05:00"},
     {"author": "ryan", "content": {"role": "model", "parts": [{"text": "Prepared"}]},
      "event_time": "2026-11-10T15:01:00-05:00"}]},
   {"turn_index": 1, "turn_id": "wf-fail:step-2",
    "events": [
     {"author": "user", "content": {"role": "user", "parts": [{"text": "Run suite"}]},
      "event_time": "2026-11-10T15:02:00-05:00"},
     {"author": "bill", "content": {"role": "model",
      "parts": [{"function_response": {"name": "tool_error",
       "response": {"error": "failed", "step_key": "step-2", "agent": "bill", "attempts": 3}}}]},
      "event_time": "2026-11-10T15:02:00-05:00"}]}]},
 "aspace_provenance": {"wid": "wf-fail", "mode": "chain", "status": "failed",
  "verdict": "failure", "model_pool": "freellmapi/auto",
  "active_model": "freellmapi/auto", "labels": "smoke",
  "owner_kind": "companion", "owner_id": "bill",
  "ingestion_source": "factory_sqlite", "source": "factory.sqlite",
  "ticket": null, "events": [{"phase": "durable_subagent", "actor": "python:bill",
  "verdict": "FAILED", "detail": "Run suite", "ts": "2026-11-10T15:02:00-05:00"}], "...": "steps résumés"}}
```

## Correction en cours de smoke (nommée)

Premier run : 4/6 — les 2 échecs portaient sur l'ordre des traces, pas sur
l'adapter. Cause : les 3 workflows du seed partageaient le même
`created_at` (T0), donc `ORDER BY created_at, wid` triait par `wid`
(`wf-empty` d'abord). L'adapter se comportait comme documenté ; c'est le
seed du test qui était faux. Corrigé : `created_at` distincts par workflow
(`wf-ok` T0, `wf-fail` T1, `wf-empty` T2) — re-run 6/6.
