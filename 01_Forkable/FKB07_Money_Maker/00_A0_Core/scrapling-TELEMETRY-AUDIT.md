# Audit télémétrie — Scrapling (D-N048 V4, FKB07)

Module : `Scrapling` (D4Vinci/Scrapling → fork `Amdkn/Scrapling`).
Gel : `c5121c7c06a8595ed3a0a9b7b7dcd6802b5ebfc5` (version 0.5.1, licence BSD-3-Clause).
Date : 2026-11-10. Auditeur : Ryan (Factory), D-N048 V4.

## §1 — Verdict

**Télémétrie zéro.** Aucun SDK de télémétrie, aucun envoi en arrière-plan,
aucune vérification de version, aucun rapport d'usage, aucun identifiant collecté.
Le réseau n'est utilisé que pour les requêtes **explicites de l'utilisateur**
(la fonction même de la bibliothèque : scraper) et pour deux comportements
opt-in ou de façade documentés ci-dessous (§2).

## §2 — Faits (scan statique, `grep -rniE` sur `scrapling/` + `pyproject.toml`)

### 2.1 Aucun SDK tiers de télémétrie

- `telemetry | posthog | sentry | segment | mixpanel | amplitude | usage-stat | crash-report | update-check | check-update | DO_NOT_TRACK` :
  **0 occurrence** dans `scrapling/` hors `ad_domains.py` (liste de données, voir §2.2).
  Seule occurrence voisine : `scrapling/engines/constants.py:64` —
  `"--disable-crash-reporter"` (drapeau Chromium qui **désactive** le rapport
  de crash du navigateur, pas un envoi).
- Dépendances (`pyproject.toml`) : `lxml`, `cssselect`, `orjson`, `tld`, `w3lib`,
  `typing_extensions` ; extras `fetchers` : `click`, `curl_cffi`, `playwright`,
  `patchright`, `browserforge`, `apify-fingerprint-datapoints`, `msgspec` ;
  extras `ai`/`shell` : pas de paquet de télémétrie. **Aucun SDK de télémétrie
  dans aucune dépendance, directe ou optionnelle.**
- `browserforge` (génération d'empreintes) travaille sur des données
  **embarquées** localement ; `apify-fingerprint-datapoints` est un jeu de
  données local. Aucun téléchargement au runtime (vérifié : `fingerprints.py`
  ne contient ni `download`, ni URL, ni appel HTTP).

### 2.2 `ad_domains.py` — liste de données, pas un envoi

`scrapling/engines/toolbelt/ad_domains.py` contient ~1 000 noms de domaines
de publicité et de suivi (source : liste de Peter Lowe, `pgl.yoyo.org`).
C'est une **liste de blocage statique** (données) : la bibliothèque l'utilise
pour filtrer, pas pour contacter ces domaines. Aucun appel réseau dans ce fichier.

### 2.3 URL codées en dur — toutes expliquées

| URL | Contexte | Déclenchement |
|---|---|---|
| `https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/logo.png` | `core/ai/server.py:1056` — métadonnée `icons` du serveur MCP | Jamais récupérée par la bibliothèque ; c'est le **client MCP** qui peut la charger. Aucun fetch au démarrage du serveur. |
| `https://cloudflare-dns.com/dns-query` | `engines/_browsers/_base.py:544` — gabarit DNS-over-HTTPS | **Opt-in uniquement** : seulement si `config.dns_over_https` est activé par l'utilisateur. |
| `https://www.google.com/` | `engines/_browsers/_stealth.py:257,575` et `engines/static.py:196` — valeur par défaut de l'en-tête `Referer` en mode furtif | **Façade** : valeur d'en-tête envoyée à la cible que l'utilisateur scrappe, pas un appel vers Google. Aucune requête vers google.com n'est émise pour elle-même. |
| `http://username`, `http://proxy1`, … | `cli.py`, `static.py`, `toolbelt/proxy_rotation.py` | Exemples dans les docstrings / valeurs factices. |
| `https://searchfox.org/…`, `https://developer.mozilla.org/…`, `https://playwright.dev/…`, `https://www.rfc-editor.org/…`, `https://www.w3schools.com/…`, `https://bugs.launchpad.net/…`, `https://lxml.de/…` | Commentaires et docstrings | Documentation, jamais appelées. |

### 2.4 Stockage local, pas de réseau

- `core/storage.py` / `spiders/cache.py` : SQLite local et fichiers locaux,
  clés par URL (séparation par site). Aucun appel réseau.
- `Selector` : stockage adaptatif **désactivé par défaut** (`adaptive=False`) ;
  quand il est activé, il écrit dans un SQLite local (`elements_storage.db`),
  jamais sur le réseau.

## §3 — Preuve réseau

- **Smoke test de l'adapter sous `unshare -n`** (sans interface réseau) :
  `aspace-scrapling-adapter/smoke_test.py` — 6 checks `ok`
  (version épinglée, API publique, parse CSS/XPath hors-ligne,
  stockage adaptatif inactif). Voir `logs-scrapling-smoke.log`.
  La surface de l'adapter fonctionne sans aucune interface réseau.
- **Scan statique** (§2) : aucune primitive d'envoi en arrière-plan
  (`requests.`, `urlopen`, `httpx`, `aiohttp`, `socket.` hors des fetchers
  explicites de l'utilisateur). Les seuls appels HTTP du code sont ceux des
  fetchers (`curl_cffi`), déclenchés uniquement par une requête explicite
  (`Fetcher.get`, `AsyncFetcher.get`, `StealthyFetcher`, sessions, spiders).
- **Limite honnête** : aucune capture réseau exhaustive de la suite complète
  n'a été faite (la suite comporte des tests navigateur réels) ; la preuve
  repose sur le scan statique exhaustif + le smoke sans réseau + la lecture
  des chemins de code. Un appel réseau non sollicité exigerait un code qui
  n'existe pas dans l'arbre (vérifié par grep sur tout `scrapling/`).

## §4 — Conclusion

**Télémétrie zéro par construction.** L'adapter n'ajoute aucun appel réseau :
il expose le parse hors-ligne (`Selector`) et n'invoque jamais les fetchers.
Aucun interrupteur à forcer : il n'y a rien à couper.
