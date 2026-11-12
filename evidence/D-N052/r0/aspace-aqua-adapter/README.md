# aspace-aqua-adapter — AQuA reads `factory.sqlite`

**Mission : D-N052 R0 — acte §D1 + §D15 du design signé Clara**
(`~/workspace/v4-factory/plans/DEVELOPPEMENT-MODULES-RECURSIVITE-plan-borne.md`).

AQuA (`core/python/ambient-quality-agent` du fork `Amdkn/adk-recipes`, gel
`a93b9cc`) ne sait lire que BigQuery / Cloud Telemetry / agents-cli. V5 n'a
ni l'un ni l'autre. Cet adapter est le pont : il lit la trace locale
`02_Factory/factory.sqlite` — écrite par la factory elle-même — et la mappe
vers le format d'entrée qu'AQuA attend, sans toucher à la base, sans
dépendance Google, sans réseau.

## 1. L'agent observé (§D15)

**L'agent observé, c'est le Worker V5** — le Compagnon Worker, l'agent de la
Factory. Sa trace EST la trace `factory.sqlite` :

- le `request_id` est **l'identité de la trace** (il devient
  `eval_case_id` — l'identifiant du cas d'évaluation AQuA) ;
- le `wid` est **son identifiant de workflow** (porté dans la provenance et
  dans les `turn_id` sous la forme `<wid>:<step_key>`) ;
- l'`agent` de chaque step est **son acteur** (il devient l'`author` de
  l'événement modèle et la clé de l'`AgentConfig` correspondante).

L'adapter ne fait **pas** des agents V5 des agents ADK : il rend leurs
traces lisibles par AQuA. Aucune conversion de sémantique d'agent, aucune
ré-écriture d'instruction — la trace V5 est présentée telle quelle, dans la
forme qu'AQuA sait consommer.

## 2. Le format d'entrée qu'AQuA attend (établi depuis le code)

AQuA ingère des **cas d'évaluation** (`EvalCase`,
`agentplatform._genai.types`). Le chemin d'ingestion complet, vérifié dans le
clone local `~/workspace/adk-recipes-repo` (code AQuA au gel, l'adapter du
fork n'a ajouté que des fichiers `aspace-adk-recipes-adapter`) :

| Étape | Fichier : lignes | Fait établi |
|---|---|---|
| Fetchers BigQuery | `tools/trajectories/bigquery_reader.py:51-54` | Tables lues : `trajectories`, `trajectory_payloads`, `trajectory_payload_turns` |
| Choix de la copie | `tools/trajectories/bigquery_reader.py:72` | `PAYLOAD_PREFERENCE = "(status = 'ingested') DESC, created_at ASC"` — préférer une copie entière, puis la plus ancienne |
| Colonnes trace | `tools/trajectories/bigquery_reader.py:212-213, 237-238` | `run_id, agent_name, trajectory_id, created_at, source, source_session_id, source_trace_ids, ingest_status` |
| Conversion OTEL → AgentData | `tools/ingestion/trace_converter.py:180-233` | `convert()` : **une trace devient un `ConversationTurn`** ; un span sans événement est compté comme abandonné (`dropped_traces`) ; retour `AgentData(agents=..., turns=...)` |
| Échec runtime → tool_error | `tools/ingestion/trace_converter.py:746` | `_resolve_error_tool_name` retourne `"tool_error"` par défaut |
| Noms d'échec | `tools/ingestion/message_parts.py:87` | `RUNTIME_ERROR_RESPONSES = {llm_error, agent_error, invocation_error}` — noms que les règles de revue référencent |
| Parts | `tools/ingestion/message_parts.py:100-109, 189, 203` | `parse_part` accepte `text`, `function_call`, `function_response`, `file_data`, … (snake_case ou camelCase) ; construction via `Part.from_function_call` / `Part.from_function_response` |
| Assemblage du bundle | `tools/trajectories/bundles.py:71, 99-118` | `build_bundle(case, ...)` : `agent_data` tient les configs d'agents et les turns ; **un turn devient un `TrajectoryStep` indexé par sa POSITION dans `agent_data.turns`**, pas par le `turn_index` du SDK |
| Cap d'écriture | `tools/trajectories/bundles.py:46` | `MAX_JSON_BYTES = 10 * 1024 * 1024` par colonne |
| Modèles stockés | `tools/trajectories/models.py:58, 182, 224` | `InvestigationTrajectory` (identifiants, statuts `ingested/partial/not_ingested`) ; `TrajectoryManifest` (agents, `step_count`, statut `ingested/partial/truncated`) ; `TrajectoryStep` (le turn sérialisé en dict JSON) |
| Consommation aval | `core/investigation/preview.py:_extract_first_user_message` | La revue extrait **le premier message utilisateur** (événements `role == "user"`, parties texte) — d'où le mapping tâche → événement utilisateur |

Formes constructeur confirmées par les fixtures de tests
(`tests/test_trajectory_bundles.py`, `tests/conftest.py:1236`) :

```python
EvalCase(eval_case_id=<id>, agent_data=AgentData(
    agents={agent_id: AgentConfig(agent_id=..., instruction=...)},
    turns=[ConversationTurn(turn_index=0, turn_id="t0", events=[
        AgentEvent(author="agent",
                   content=Content(role="model", parts=[Part(text=...)]))
    ])]))
```

Forme JSON sérialisée (ce que l'adapter émet — équivalent de
`EvalCase.model_dump(mode="json", exclude_none=True)`) :

```json
{"eval_case_id": "<request_id>",
 "agent_data": {"agents": {"<agent>": {"agent_id": "<agent>",
                                       "instruction": "...",
                                       "description": "..."}},
                "turns": [{"turn_index": 0, "turn_id": "<wid>:<step_key>",
                           "events": [{"author": "user",
                                       "content": {"role": "user",
                                                   "parts": [{"text": "..."}]},
                                       "event_time": "<ISO-8601>"}]}]}}
```

Ni `agentplatform` ni `google.genai` ne sont installés sur cette VM : la
forme ci-dessus est établie depuis le code AQuA et ses tests, pas depuis le
SDK — c'est l'incertitude nommée du §5, et c'est pourquoi l'adapter émet des
dicts JSON bruts (stdlib seule) plutôt que des objets SDK.

## 3. Mapping champ par champ (`factory.sqlite` → AQuA)

Schéma source : `~/workspace/v5-repo/02_Factory/factory.ps1`, lignes 42–115
(`CREATE TABLE`). Timestamps : format ISO-8601 « o » (`Get-Date -Format "o"`,
lignes 175/191), passés **verbatim** — pydantic les parse en `datetime` à la
construction de l'`EvalCase`.

| Source (`factory.sqlite`) | Cible AQuA | Note |
|---|---|---|
| `durable_workflows.request_id` | `eval_case_id` | Identité de la trace (§D15) ; repli `wid` si vide |
| `durable_workflows.wid` | `aspace_provenance.wid` + préfixe des `turn_id` | Identifiant de workflow (§D15) |
| `durable_steps` (un row) | un `ConversationTurn` | `turn_index` = position (0-based), `turn_id` = `<wid>:<step_key>`, ordre `seq` |
| `durable_steps.task` | événement `user` (`role: "user"`, parties `[{"text": task}]`) | L'instruction reçue par le worker — c'est le « premier message utilisateur » que la revue extrait |
| `durable_steps.output` | événement modèle (`author` = step `agent`, `role: "model"`, parties `[{"text": output}]`) | La réponse du worker |
| `durable_steps.agent` | `author` de l'événement modèle + clé de `AgentConfig` | L'acteur du step (§D15) |
| `durable_steps.harness` | `AgentConfig.instruction` / `description` | « Worker V5 — Compagnon `<agent>` (harness `<harness>`) » |
| `durable_steps.worktree` | `AgentConfig.description` | Contexte du worker |
| `durable_steps.status` (échec) | partie `function_response` nommée `"tool_error"` | `{"error": status, "step_key", "agent", "attempts"}` — le nom qu'AQuA assigne elle-même aux échecs runtime (`trace_converter.py:746`) ; ajoutée à l'événement modèle, ou événement modèle propre s'il n'y a pas d'`output` |
| `durable_steps.updated_at` | `event_time` des deux événements du turn | Verbatim ISO-8601 |
| `durable_steps` (ni `task` ni `output`, sans échec) | **aucun turn** | Enregistré en provenance (`emitted_as_turn: false`) — rien n'est inventé |
| `durable_workflows.status` + statuts des steps | `aspace_provenance.verdict` | Classification V5 (voir §4) — pas un champ AQuA |
| `durable_workflows.model_pool` / `active_model` / `labels` / `mode` / `owner_kind` / `owner_id` | `aspace_provenance.*` | Verbatim tels que stockés (chaînes) |
| `events` (`ticket_id = wid`) | `aspace_provenance.events` | **Jalons, pas des turns** : phase, actor, verdict, detail, ts — le journal du workflow, conservé comme métadonnée pour le diagnostic, sans prétendre que ce sont des paroles d'agent |
| `tickets` (`id = wid`) | `aspace_provenance.ticket` ou `null` | Contexte opportuniste : l'intake ne crée pas de ligne ticket pour le workflow, donc l'absence est normale |
| `writer_locks`, `durable_docs`, `handoffs` | **non lus** | État de coordination, pas du contenu de trace |

## 4. Verdict (classification V5, pas AQuA)

`aspace_provenance.verdict` ∈ `success | failure | in_progress | unknown` :

- `failure` — le workflow ou **un** step a échoué (statut contenant
  `fail`, `error`, `timeout`, `abort` ou `crash`, insensible à la casse).
- `in_progress` — le workflow ou un step est encore ouvert (`running`,
  `paused`, `interrupted`, `asking`, ou `waiting for writer lock: …`), ou un
  step n'est pas en succès terminal.
- `success` — le workflow **et** tous les steps sont en succès terminal
  (`completed`, `success`, `done`, `ok`…).
- `unknown` — aucun des cas ci-dessus (orthographe terminale inconnue — elle
  est classée `unknown`, jamais `success` par défaut).

Vocabulaire : l'intake écrit `running` / `paused` / `interrupted` /
`asking` (factory.ps1 lignes 291–294) ; les valeurs terminales
(`completed` / `failed`) sont écrites par la boucle d'exécution, pas par
l'intake — d'où le classement par jetons plutôt que par énumération fermée.

Note : le `TrajectoryStatus` d'AQuA (`ingested` / `partial` / `truncated`)
décrit la **complétude de l'ingestion**, pas le succès ou l'échec du
workflow — le verdict vit en provenance et dans le contenu des turns, pas
dans un `TrajectoryStatus`.

## 5. Limites nommées

1. **SDK non installé ici** — ni `agentplatform` ni `google.genai` ne sont
   présents sur cette VM ; la forme JSON émise est établie depuis le code
   AQuA et ses fixtures de tests (§2), pas depuis une construction SDK. R3
   devra valider la construction `EvalCase(**ligne)` dans l'environnement où
   le SDK existe. L'incertitude porte sur les champs optionnels du SDK
   (`turn_id`, `event_time`, `description`) — tous documentés comme
   optionnels dans les fixtures.
2. **Pas de définitions d'outils** — `AgentConfig.tools` est omis : aucun
   step ne porte de liste d'outils (seul le nom du harness existe). R3 peut
   l'enrichir depuis le harness.
3. **Pas d'identité de modèle par turn** — AQuA n'a pas de champ modèle par
   turn ; `active_model` est en provenance seulement.
4. **Pas de compteurs de tokens ni de latences** — `factory.sqlite` n'a pas
   ces colonnes ; rien n'est inventé.
5. **Pas d'instructions système** — aucun step ne porte de texte
   d'instruction d'agent ; `AgentConfig.instruction` est la ligne générée
   « Worker V5 — Compagnon … ».
6. **`steers_json` non mappé** — les directives de pilotage n'ont pas
   d'équivalent AQuA ; elles ne sont pas copiées (même pas en provenance).
7. **Workflows sans step** — émis avec `turns: []` et `agents: {}` (jamais
   silencieusement abandonnés) ; `build_bundle` accepte un cas sans turn
   (`bundles.py:96` — « A case with no turns produces a … »).
8. **Événements sans `step_key`** — les lignes `events` ne portent pas de
   `step_key` ; elles ne sont donc pas rattachées à un turn, mais conservées
   comme jalons en provenance.

## 6. Usage

```bash
python3 src/aqua_factory_reader.py --db /chemin/vers/factory.sqlite \
                                    --out traces.jsonl
```

Lecture seule : ouverture `mode=ro` (URI) + `PRAGMA query_only = ON`. Le
fichier de sortie est du JSONL — une ligne par workflow, un workflow = une
trace. Le bloc `aspace_provenance` est une extension V5 : R3 le retire
avant de construire l'`EvalCase` SDK (pydantic ignore les champs inconnus
par défaut, mais le retrait est explicite).

```bash
python3 smoke_test.py   # test de fumée, stdlib seule — voir SMOKE-RESULTS.md
```

## Fichiers

| Fichier | Contenu |
|---|---|
| `src/aqua_factory_reader.py` | Le lecteur (`read_traces(db_path)` + CLI `--db --out`) |
| `contract.json` | Le contrat d'entrée/sortie (machine-readable) |
| `smoke_test.py` | Test de fumée : base temporaire, 3 workflows connus, hash avant/après |
| `SMOKE-RESULTS.md` | Bilan du smoke, commandes et sorties |
| `README.md` | Ce fichier |
