# Fiche d'adaptation — MiroFish (D-N053, pas A)

**Statut :** état 0 Basique → 1 Adapté (fiche + adapter + manifeste, tests
verts — voir § Tests). **Niveaux :** le manifeste porte `levels.current: 0` ;
le coordinateur le monte à 1 à l'intégration.
**Fork :** https://github.com/Amdkn/MiroFish (gel `7657031ac01184afe2cb220f5ee3545573b5e843`,
branche `main`, parent `666ghj/MiroFish`).
**Dossier :** `aspace-mirofish-adapter/` (service.py + client.py +
contract.json + SERVICE-CONTRACT.md + README.md + config.example +
smoke_test.py + test_adapter.py), commit adapter `dff2f017d97015319f080738aa4944c74c565206`
sur le fork. **Bind re-appliqué verbatim** sur `main` au-dessus de
l'adapter : commit `65d327eba68c0729edbfbb29d2ff2105ce2a5525`
(`aspace-plugin.json`, sha256 `6db9d8bf…` identique au bind `9b49ac4`).
**Pin proposé pour V5 : `65d327e`** (adapter + bind, per F8 D4) ;
le commit adapter seul est `dff2f01`. **Seul code A'Space du fork** —
le code amont est byte-identique au gel (diff bind → HEAD = les 8
fichiers adapter seuls ; 0 fichier amont modifié, H-M2).
**Version amont :** 0.1.0 (`backend/pyproject.toml`).

## Licence — AGPL-3.0 (le seul copyleft du Runtime)

Fichier `LICENSE` vérifié au fichier : GNU AFFERO GENERAL PUBLIC
LICENSE v3. Le fork ET l'amont disent AGPL-3.0 (API GitHub, vérifié des
deux côtés). L'AGPL couvre l'usage en réseau : adapter MiroFish en
bibliothèque liée au Runtime soumettrait la distribution (et l'usage en
réseau) du Runtime à l'obligation de source correspondante AGPL —
contamination copyleft du Runtime, inacceptable pour le profil B2B.

## Décision §D2 — isolé en service (tranchée, ne pas rouvrir)

**MiroFish est isolé en service, ni adapté en bibliothèque, ni
remplacé.** Remplacer est rejeté : MiroFish est le moteur
d'intelligence de swarm (OASIS + MindGraph) — aucun équivalent dans le
Runtime. Isoler en service : MiroFish tourne comme un service séparé
(son propre processus, derrière une interface HTTP locale) ; le Runtime
l'appelle par l'interface (jamais lié — aucun import, aucun processus
partagé). L'obligation AGPL est alors confinée au service MiroFish
lui-même (sa source est offerte sous AGPL — le fork, déjà AGPL,
inchangé). **L'adapter est la frontière de service** (le service
MiroFish + l'interface cliente dans le Runtime).

## Surface de l'adapter (la frontière de service, §D2)

- `service.py` — lanceur (stdlib seule) : exécute le vrai backend
  amont `backend/run.py` comme processus séparé (`subprocess.Popen`,
  `start_new_session=True`), hôte forcé 127.0.0.1, port 5150 par
  défaut (`MIROFISH_SERVICE_PORT`), attend `/health` (180 s), arrêt
  propre SIGTERM (15 s de grâce, puis SIGKILL). Refuse de démarrer
  sans `LLM_API_KEY` / `ZEP_API_KEY` (miroir de `Config.validate()`
  amont) et refuse `ZEP_API_URL` (non supporté par l'amont). Aucune
  valeur de clé n'est jamais journalisée.
- `client.py` — interface cliente HTTP locale (stdlib seule, `urllib`) :
  santé, graphe (`/api/graph/*`), simulation (`/api/simulation/*`),
  rapport (`/api/report/*`). Refuse tout hôte non local. Aucun import
  d'un module MiroFish — le Runtime ne connaît MiroFish que par HTTP.
- `contract.json` + `SERVICE-CONTRACT.md` — contrat de service
  (endpoints, formes de requête/réponse relevées sur le backend au
  gel, erreurs, délais). Le service offre la simulation de swarm ; il
  ne fait pas : import par le Runtime, exposition réseau, simulation
  sans clés opérateur, télémétrie, frontend, usage B2B.
- `config.example` — configuration opérateur, sans secret (clés en
  variables d'environnement uniquement).

## § Tests

**Suite adapter (stdlib, sans clés, sans réseau) : 12 passés, 0 échec,
0 ignoré** (`python3 aspace-mirofish-adapter/test_adapter.py`, 0,05 s,
rc=0). Log `logs-mirofish-suite-adapter.log`. Couvre : contrat valide
et fidèle aux routes amont, client refuse les hôtes non locaux et
mappe les erreurs HTTP, lanceur refuse sans clés / hôte non local /
`ZEP_API_URL`, aucun import MiroFish dans l'adapter.

**Suite amont (`backend/tests/`, 18 fichiers) : 129 passés, 0 échec,
0 ignoré** (`pytest tests/ -q`, 5,74 s, rc=0, venv dédiée avec les
dépendances légères du backend : flask, flask-cors, python-dotenv,
openai, zep-cloud 3.25.0, httpx, pydantic, PyMuPDF, charset-normalizer,
chardet, pytest). Log `logs-mirofish-suite-upstream.log`. Les imports
`camel`/`oasis` sont paresseux (chargés seulement pendant une
simulation) — la suite amont tourne sans eux.

**Smoke (vrai backend, processus séparé, HTTP local) : 6/6, rc=0.**
Log `logs-mirofish-smoke.log` (+ journal du service
`logs-mirofish-service.log`). Lanceur PID 44605, service PID 44606
(processus séparé prouvé) ; démarrage 2,1 s ; `GET /health` →
`{"status": "ok", "service": "MiroFish Backend"}` via `client.py` ;
`GET /api/simulation/list` → 200 `{"success": true, "data": [],
"count": 0}` via `client.py` ; arrêt propre SIGTERM en 0,2 s
(`killed: false`), processus mort vérifié. Clés factices
(`dummy-smoke-key`) : `/health` et `/list` n'appellent ni LLM ni Zep ;
aucune simulation lancée (elle consommerait du quota).
Premier run : arrêt en 30,5 s avec SIGKILL — cause trouvée et corrigée
dans le lanceur (le fils mort restait zombie non moissonné, `kill(pid,
0)` réussissait à tort) ; second run : arrêt propre 0,2 s.

## Preuves d'isolation (H-A5)

1. **Aucun import MiroFish dans le code du Runtime** — scan
   `grep -rniE "import.*mirofish|from.*mirofish"` sur
   `01_Forkable/FKB00_Runtime/` : 0 import de code MiroFish. Les seuls
   noms correspondants sont de la documentation (`.md`) et
   `load_mirofish_nodes` (dans `aspace_precheck_weights.py`, natif
   A'Space, stdlib seule) — un chargeur de *données* de nœuds
   (SQLite / export JSONL), jamais un import de code MiroFish.
   Côté adapter : scan par test unitaire (lignes d'import) — stdlib
   seule, 0 import amont.
2. **Processus séparé** — prouvé par le smoke : le service tourne
   comme son propre processus (PID 44606 ≠ lanceur 44605), démarré par
   `subprocess.Popen` avec `start_new_session=True`.
3. **Interface HTTP-locale** — tous les appels passent par HTTP sur
   127.0.0.1 (le client refuse tout autre hôte ; le lanceur force
   `FLASK_HOST=127.0.0.1`, l'amont seul mettrait `0.0.0.0`).

## Télémétrie (audit complet : `MiroFish-TELEMETRY-AUDIT.md`)

- **Télémétrie zéro par contrat** — aucun SDK d'analytique
  (sentry/posthog/amplitude/mixpanel/segment/hotjar/clarity) dans le
  backend, le frontend ou les scripts ; aucun ping de version, aucun
  rapport de crash.
- Seuls appels sortants fonctionnels, tous déclenchés par l'opérateur :
  le LLM configuré (`LLM_BASE_URL`, défaut `https://api.openai.com/v1`)
  et Zep Cloud (`https://api.getzep.com/api/v2`), uniquement pendant
  une simulation ou une construction de graphe, jamais par défaut
  (sans clés, le service refuse de démarrer).

## Réserves nommées

1. **Aucune simulation réelle exécutée ici** — elle exige des clés
   LLM + Zep valides (secrets opérateur, jamais provisionnés ici) et
   consomme du quota ; le smoke prouve la frontière (démarrage,
   `/health`, appel d'API, arrêt), pas une simulation. La première
   simulation réelle est un acte de déploiement, pas de sandbox.
2. **Dépendances lourdes non installées** — `camel-oasis` /
   `camel-ai` (simulation OASIS) ne sont pas dans la venv de test ;
   elles ne sont chargées que pendant une simulation. À installer au
   déploiement (`pip install -r backend/requirements.txt`).
3. **Serveur de développement** — l'amont sert Flask en dev
   (`WARNING: This is a development server`) ; un déploiement exposé
   exigerait un serveur WSGI de production. La frontière est locale
   (127.0.0.1), donc ce n'est pas une exposition.
4. **Champ `branch` du bind** — `aspace-plugin.json` dit
   `"branch": "aspace-v5-native"` (sa branche d'origine) ; il est
   ré-appliqué **verbatim** per F8 D2 (sha256 identique au bind
   `9b49ac4`), le champ n'a pas été retouché. À noter à l'intégration,
   pas à corriger ici.
5. **Dérive amont : 0** au gel (tête amont toujours `7657031` après
   les pushs). Le fork ajoute exactement 2 commits A'Space (adapter +
   bind).

## Dette de divergence

Propriétaire : cœur Buzz (lane Clara / 12e). La divergence est portée
par le fork `Amdkn/MiroFish` : l'adapter seul est du code A'Space ;
tout le reste est l'amont au gel `7657031`. Dérive amont suivie par
l'inventaire hebdomadaire (HEAD amont vs commit gelé) ; revisite par
signal, jamais de fast-forward silencieux. Aucun usage en B2B sans
arbitrage vision (AGPL).
