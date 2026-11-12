# Audit télémétrie zéro — herdr (D-N053 pas F1)

**Module :** `Amdkn/herdr`, gel `ee5bfb5` (v0.9.5), adapter
`aspace-herdr-adapter` (voir `herdr-ADAPTATION.md`).
**Date :** 2026-11-12. **Verdict : 0 appel sortant par défaut.**

## Méthode

Scan statique du code Rust au gel + lecture du `Cargo.lock` + capture
réseau bornée (strace des chemins du smoke : `herdr --version`,
`herdr --help`, `herdr server --help`, `herdr config check` — aucune
connexion autre que locale ; voir le log du smoke). Chaque déclencheur
du Discover §6 est tranché ci-dessous.

## Scan statique

- `grep -r "telemetry|analytics|posthog|sentry|segment" src/ --include=*.rs` :
  seuls faux positifs `segment_index` (tab bar, `src/app/api.rs`,
  `src/app/tab_bar_status.rs`) — **0 SDK de télémétrie**.
- `Cargo.lock` : aucune crate `reqwest`, `ureq`, `hyper`, `curl`.
  Le réseau passe par `curl` en sous-processus ou par SSH, rien n'émet
  sans une commande explicite, sauf T1/T2 ci-dessous.
- `docs/next/product-announcement.json` = `null` au gel, aucun fetch
  trouvé dans `product_announcements.rs` — pas un émetteur au gel.
- `zbus` 5.19 (logind, D-Bus local) : pas réseau.

## Déclencheurs (Discover §6) — tous tranchés

| # | Émetteur | Déclencheur | Cible | Statut amont | Décision adapter |
|---|---|---|---|---|---|
| T1 | Vérification de version en arrière-plan | **Automatique au démarrage** (`AppPolicy::PRODUCTION`, `background_updates: true`), toutes les 30 min (`AUTO_UPDATE_CHECK_INTERVAL`, `src/app/mod.rs:42`) | `herdr.dev/latest.json`, `herdr.dev/preview.json`, `formulae.brew.sh/api/formula/herdr.json` (`src/update.rs:25-27`) | ON par défaut ; « only surface availability and release notes » (pas de téléchargement) | **Forcé OFF** par l'adapter (D-F1-5) : `[update] version_check = false` dans la config embarquée, vérifiée au fichier ET par `herdr config check` sur le binaire adapté. |
| T2 | Vérification du manifeste de détection d'agents | Même thread d'arrière-plan, même intervalle | `herdr.dev/agent-detection/index.toml` (`src/detect/manifest_update.rs:16`) | ON par défaut | **Forcé OFF** par l'adapter (D-F1-5) : `[update] manifest_check = false` dans la config embarquée, vérifiée au fichier ET par `herdr config check`. |
| T3 | `herdr update` | Commande manuelle explicite | `herdr.dev` (téléchargement + installation du binaire) | Manuel | **Hors contrat** : commande non exposée par l'adapter. |
| T4 | `herdr plugin update` | Commande manuelle explicite | GitHub (plugins) | Manuel | **Hors contrat** : commande non exposée par l'adapter. |
| T5 | Remote | Opt-in explicite (`--remote`) | SSH vers la machine distante | Manuel | **Hors contrat télémétrie** : pont SSH, pas de télémétrie. |

## Capture réseau (bornée)

Chemins du smoke sous `strace -e trace=network` : `herdr --version`,
`herdr --help`, `herdr server --help`, `herdr config check` (config
embarquée pointée par `HERDR_CONFIG_PATH`) — **0 `connect()`, 0 `socket()`**
(3 traces fusionnées : `logs-strace-adapte.log`).
Note : `herdr config check` ne contacte aucun serveur ; les commandes
`server stop|reload-config|reload-agent-manifests` parlent au socket
local `herdr.sock` (NDJSON) uniquement et ne sont pas jouées par le
smoke (aucun serveur lancé).

## Conclusion

**0 appel sortant par défaut.** Les deux seuls émetteurs automatiques
(T1/T2) sont coupés par l'adapter (`version_check = false`,
`manifest_check = false`, forcés et vérifiés). Le reste est manuel et
hors contrat. Ré-audit à chaque changement de commit gelé ou d'adapter,
et au minimum à chaque transition d'état (D3).
