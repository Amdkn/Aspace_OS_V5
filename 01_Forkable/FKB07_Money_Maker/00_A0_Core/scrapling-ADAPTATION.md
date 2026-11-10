# Fiche d'adaptation — Scrapling (D-N048 V4, FKB07)

**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste, smoke 6/6, suite 2 418 passés / 7 échecs qualifiés environnementaux / 0 ignorés — voir § Tests)

## Commit gelé

- **Amont :** `D4Vinci/Scrapling`, branche `main`, gel **`c5121c7`** (complet `c5121c7c06a8595ed3a0a9b7b7dcd6802b5ebfc5`).
- **Fork :** https://github.com/Amdkn/Scrapling (HEAD `c5121c7` = gel dès la création, H-M1 tient ; aucune dérive amont constatée entre le gel du design et la création du fork).
- **Version :** 0.5.1. Taille ~16 Mo. Clone complet.

## Licence : BSD-3-Clause

`LICENSE` amont préservé byte-identique dans le fork.

**Clause 3 — non-approbation (§D4 du design) :** le nom du titulaire du
copyright (Karim Shoair, 2024) et des contributeurs ne peut pas servir à
endosser ou promouvoir un produit dérivé sans autorisation écrite préalable.
**Ce fork n'est ni endossé par D4Vinci, ni présenté comme tel** — l'adapter
le dit explicitement (`contract.json`, `README.md`), et aucune mention
d'aval de l'amont n'apparaît nulle part dans le fork.

## Dossier : `aspace-scrapling-adapter/` (contract.json + smoke_test.py + README.md), commit `2240bb5` sur le fork

**Seul code A'Space du fork** — le code amont est byte-identique au gel
(diff gel→adapter = 3 fichiers, vérifié à l'API, H-M2 tient).
Surface : parse HTML hors-ligne (`Selector`), fetchers explicites
(`Fetcher.get`, `AsyncFetcher.get`, `StealthyFetcher.fetch`) — **jamais
invoqués par l'adapter**. Aucun appel réseau de l'adapter, aucun secret.

## Tests

- **Au gel `c5121c7` : suite amont complète, 3 volets tox** (log `logs-scrapling-suite.log`).
  Commande CI (`tox.ini`) reproduite sans `--cov` (comptages identiques) :
  `pytest -m "browser"`, puis `pytest -m "asyncio and not browser"`,
  puis `pytest -m "not asyncio and not browser" -n auto`, depuis `tests/`
  (venv dédié, `pip install -e ".[ai,shell]"` + `tests/requirements.txt`).
- **Bilan : 2 418 passés, 7 échecs, 0 ignorés (2 425 tests courus, doctests inclus).**
  - Volet 1 (`browser`) : 171 passés, **7 échecs**, 2 247 désélectionnés, 17 min 24 s, rc=1.
  - Volet 2 (`asyncio and not browser`) : 1 131 passés, 0 échec, 2 min 30 s, rc=0.
  - Volet 3 (`not asyncio and not browser`, `-n auto`) : 1 116 passés, 0 échec, 24,58 s, rc=0.
- **Les 7 échecs, tous qualifiés à la racine, aucun imputable à l'adapter
  (l'adapter ne touche pas `scrapling/`) ni à un défaut du code amont :**
  1. `ai/test_browser_extract_content.py::test_browser_extract_content_live_target_errors_allow_next_call` —
     `Page.aria_snapshot: Timeout 100ms exceeded` : budget de 100 ms dépassé
     sous charge (VM partagée, 1,5 CPU, 4 agents V4 simultanés). Timing.
  2. `fetchers/async/test_stealth.py::test_properties[kwargs0]` et
  3. `fetchers/async/test_stealth.py::test_properties[kwargs6]` —
     `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome` :
     les cas paramétrés portent `real_chrome: True` ; Google Chrome n'est pas
     installé sur cette VM (vérifié : `/opt/google/chrome/chrome` absent ;
     seul le Chromium Playwright `chromium-1248` est présent).
  4. `fetchers/async/test_stealth_session.py::test_stealthy_session_with_options[options1]` —
     `TargetClosedError` : le cas porte `headless: False` (navigateur avec
     affichage) sur une VM sans serveur X (`DISPLAY` vide, vérifié).
  5. `fetchers/sync/test_stealth.py::test_properties[kwargs0]` et
  6. `fetchers/sync/test_stealth.py::test_properties[kwargs3]` —
     même cause que 2–3 (`real_chrome: True`, Chrome absent).
  7. `fetchers/test_cloudflare_readiness.py::test_async_widget_readiness[delayed_script]` —
     `assert elapsed < 8, elapsed` avec `elapsed = 8.354 s` : assertion
     d'horloge dépassée de 0,35 s sous charge. Timing.
- **Smoke test de l'adapter : 6/6 VERT** (`logs-scrapling-smoke.log`),
  en normal **et** sous `unshare -n` (sans interface réseau) :
  version épinglée, API publique, parse CSS/XPath hors-ligne,
  stockage adaptatif inactif par défaut.
- **Comportement amont noté (pas un défaut) :** le stockage adaptatif de
  `Selector` écrit par défaut dans `scrapling/elements_storage.db`
  (chemin du paquet) quand `adaptive=True` ; la suite a créé ce fichier
  (artefact de test, supprimé après le run, jamais committé — l'arbre du
  fork est propre, HEAD `2240bb5`).

## Télémétrie

**Zéro par construction** (audit `scrapling-TELEMETRY-AUDIT.md`) : aucun SDK,
aucun envoi en arrière-plan, aucune vérification de version. Le réseau n'est
utilisé que pour les requêtes explicites de l'utilisateur (la fonction même
de la bibliothèque) ; DoH Cloudflare opt-in uniquement ; en-tête `Referer`
Google = valeur de façade envoyée à la cible, pas un appel vers Google.
`ad_domains.py` est une liste de blocage statique (données, pas un envoi).
Aucun interrupteur à forcer : il n'y a rien à couper.

## Divergence

- **Dette de divergence :** propriétaire nommé = cœur Buzz (lane Clara / 12e).
  Le module est au gel `c5121c7` ; toute revisite passe par un signal de
  dérive (inventaire Auto Research) et un candidat de fusion, jamais par
  fast-forward silencieux (§D5 du design).
- **Dérive constatée :** aucune entre le gel du design et la création du fork
  (amont toujours à `c5121c7` le 2026-11-10).
- **Contrainte nommée (§D4) :** clause de non-approbation BSD — respectée
  (voir § Licence).

## Réserves nommées

1. Suite courue sans `--cov` (écart à la commande tox exacte, comptages
   identiques ; la couverture n'affecte pas les résultats).
2. Les 7 échecs sont environnementaux (Chrome réel absent, affichage absent,
   timings sous charge) — à re-vérifier en CI hors sandbox si le 13e l'exige ;
   aucun n'est imputable à l'adapter.
3. La preuve réseau de l'audit est statique + smoke sans réseau, pas une
   capture exhaustive de la suite complète (qui comporte des tests navigateur
   réels) ; un appel non sollicité exigerait un code absent de l'arbre.
4. `elements_storage.db` (chemin par défaut du stockage adaptatif, dans le
   paquet) : artefact de test supprimé ; à surveiller si l'adapter active
   un jour `adaptive=True` (il ne le fait pas).
