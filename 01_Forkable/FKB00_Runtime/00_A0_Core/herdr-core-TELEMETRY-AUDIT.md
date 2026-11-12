# Audit télémétrie zéro — herdr-core (D-N053 pas F1)

**Module :** `Amdkn/herdr-core`, gel `cd12ddd` (v0.1.18), adapter
`aspace-herdr-core-adapter` (voir `herdr-core-ADAPTATION.md`).
**Date :** 2026-11-12. **Verdict : 0 appel sortant par défaut.**

## Méthode

Scan statique du code Rust au gel + lecture du `Cargo.lock` + capture
réseau bornée (strace des chemins du smoke : `hc --version`, `hc --help`,
`hc doctor`, `hc server status` sans serveur — aucune connexion autre
qu'un socket Unix local ; voir le log du smoke). Chaque déclencheur du
Discover §6 est tranché ci-dessous.

## Scan statique

- `grep -r "telemetry|analytics|posthog|sentry|segment" crates/ --include=*.rs` :
  **0 occurrence**.
- `Cargo.lock` : aucune crate `reqwest`, `ureq`, `hyper`, `curl`.
  Le seul réseau sortant du code passe par `curl` en sous-processus
  (`crates/herdr-core/src/releases.rs:38`, `Command::new("curl") -fsL
  --retry 2`) ou par SSH (`remote.rs`, `machines.rs`).

## Déclencheurs (Discover §6) — tous tranchés

| # | Émetteur | Déclencheur | Cible | Statut amont | Décision adapter |
|---|---|---|---|---|---|
| T6 | `hc update` | Commande manuelle explicite seulement — « Only when asked: hc never checks for updates on its own » (`cli.rs:591`) | `releases.herdr.dev` (`core/latest.json`, `core/<version>/manifest.json`) | Manuel, jamais automatique | **Hors contrat** : la commande n'existe pas dans le binaire adapter `hc` (clap la rejette). Les tests amont utilisent le faux serveur local `releases_server.py`, jamais `releases.herdr.dev`. |
| T7 | `notes` agent-à-agent | **Défaut ON** (`config.rs` : « Notes to parent agents […] on or off (default on) » ; `notes_on()` : `c.notes.unwrap_or(true)`) | Pas réseau — comportement (hc tape des notes seul) | ON par défaut | **Forcé OFF** par l'adapter (D-F1-5) : `config.toml` embarquée (`notes = false`), vérifiée au fichier ET par la preuve de protocole (la lib lit la config, `notes == Some(false)`). |
| T8 | Machines distantes | Opt-in explicite (`hc machine add/connect`, `machine.exec`) | SSH vers la machine distante | Manuel | **Hors contrat télémétrie** : pont SSH, pas de télémétrie. Le binaire adapter expose `machine add|ls|login|update|rename|rm` comme client vers des machines côté opérateur uniquement. |

## Capture réseau (bornée)

Chemins du smoke sous `strace -e trace=network` : `hc --version`,
`hc --help`, `hc doctor`, `hc server status` (sans serveur) — 0
`connect()` vers une adresse IP ; seule une tentative de connexion au
socket Unix scratch (`$XDG_RUNTIME_DIR/herdr-core/default.sock`) qui
échoue proprement (`unavailable`, sans auto-démarrage). Aucun DNS, aucun
HTTP. (Log : `logs-smoke-adapte.log`.)

## Conclusion

**0 appel sortant par défaut.** Les deux seuls émetteurs possibles sont
`hc update` (manuel, exclu du binaire adapter) et `notes` (défaut ON,
forcé OFF par l'adapter). Ré-audit à chaque changement de commit gelé ou
d'adapter, et au minimum à chaque transition d'état (D3).
