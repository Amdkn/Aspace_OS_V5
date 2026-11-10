# Audit télémétrie — MiroFish (D-N053, pas A)

**Verdict : télémétrie zéro par contrat.** Aucun mécanisme de
télémétrie, d'analytique, de rapport de crash ou de vérification de
version dans le service. Les seuls appels sortants sont fonctionnels,
déclenchés par l'opérateur, et n'ont lieu que pendant une simulation
ou une construction de graphe — jamais par défaut.

## Méthode

- Scan statique (grep) de `backend/` (Python), `frontend/src/`
  (JS/TS), `scripts/`, `backend/requirements.txt`,
  `backend/pyproject.toml`, `.env.example`, `docker-compose.yml` :
  recherche de `sentry|posthog|amplitude|mixpanel|segment|hotjar|
  clarity|google-analytics|googletagmanager` → **0 occurrence**.
- Scan des URL sortantes codées en dur dans `backend/app/` et
  `backend/scripts/` → 2 hôtes seulement (voir § Appels sortants).
- Lecture de `backend/app/config.py` (`Config.validate`) et de
  `backend/run.py` (porte d'entrée) : sans clés, le service refuse de
  démarrer — aucun appel sortant n'est possible par défaut.

## Appels sortants — chaque déclencheur tranché

| # | Destination | Déclencheur | Statut |
|---|---|---|---|
| 1 | LLM configuré — `LLM_BASE_URL` (défaut `https://api.openai.com/v1`, opérateur) | Une simulation, une génération de rapport ou une construction de graphe, avec `LLM_API_KEY` opérateur | **Fonctionnel, opérateur seul.** Jamais par défaut (sans clé, pas de démarrage). Consomme du quota LLM (l'amont recommande < 40 tours pour commencer). |
| 2 | Zep Cloud — `https://api.getzep.com/api/v2` (SDK `zep-cloud==3.25.0`) | Lecture / écriture de la mémoire graphe pendant une simulation ou une construction de graphe, avec `ZEP_API_KEY` opérateur | **Fonctionnel, opérateur seul.** Jamais par défaut. `ZEP_API_URL` est refusé par l'amont (Zep Cloud seul). |
| — | (aucun autre) | — | Aucun ping de version, aucun heartbeat, aucun rapport de crash, aucun SDK d'analytique. |

## Hors périmètre du service (noté, non compté)

- **Frontend** (`frontend/`, non servi par la frontière) : sa seule
  sortie est `VITE_API_BASE_URL` (défaut `http://localhost:5001`,
  l'API locale) plus un lien `https://github.com/666ghj/MiroFish`.
  Aucun SDK d'analytique.
- **Scripts de développement** (`scripts/fetch_star_count.py`,
  `scripts/star_history.py`, `tests/test_local_star_*.py`) : appels à
  l'API GitHub (compteurs d'étoiles). Hors du runtime du service —
  ils ne tournent jamais quand le service tourne.
- **README** : badges externes (trendshift, shields, deepwiki) — des
  images dans de la documentation, pas du code exécuté.

## Ce que le service n'émet jamais

- Aucun appel sortant au démarrage : `/health` n'appelle ni LLM ni
  Zep (vérifié par le smoke : `/health` 200 avec des clés factices).
- Aucun envoi en arrière-plan : pas de thread, pas de tâche planifiée
  qui appellerait un tiers hors d'une requête opérateur.
- Aucune donnée d'usage collectée : pas d'identifiant machine, pas de
  journal d'événements sortant.

## Dépendances (surface d'appel)

`backend/requirements.txt` (gel) : flask, flask-cors, openai,
zep-cloud 3.25.0, httpx, camel-oasis 0.2.5, camel-ai 0.2.78, PyMuPDF,
charset-normalizer, chardet, python-dotenv, pydantic. Aucune
dépendance de télémétrie. `camel-oasis` / `camel-ai` sont chargés
paresseusement (seulement pendant une simulation) et appellent le LLM
configuré — même déclencheur que la ligne 1 ci-dessus.

## Conclusion

**Télémétrie zéro.** Le service MiroFish, tel qu'adapté (frontière de
service, clés opérateur uniquement), n'émet aucun appel sortant par
défaut. Tout appel sortant est un appel fonctionnel explicite de
l'opérateur (LLM, Zep Cloud), avec ses propres clés, pendant une
opération qu'il a demandée.
