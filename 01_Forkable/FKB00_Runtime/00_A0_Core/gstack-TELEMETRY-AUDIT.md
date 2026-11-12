# Audit télémétrie — gstack (D-N053 pas C, H-M4)

**Module :** `gstack` — fork `Amdkn/gstack`, gel `3742ee95`, adapter `6cb6da7`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Les seuls appels réseau du repo sont des appels explicites de l'utilisateur / des workflows (navigateur, modèles, CI), jamais déclenchés par l'adapter.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `lib/`, `scripts/`, `bin/` : `posthog|sentry|amplitude|mixpanel` → **0 hit**.
Motifs cherchés dans `package.json` et `bun.lock` : `posthog|sentry|amplitude|mixpanel|telemetry` → **0 hit** (aucune dépendance de télémétrie déclarée).
L'adapter est **stdlib seule** (0 import réseau dans `aspace_gstack_adapter/__init__.py`, vérifié : 0 hit).

### Sites réseau explicites (tous déclenchés par l'utilisateur / les skills, jamais en arrière-plan)

- `browse/` — navigateur intégré (Chromium via Playwright/CDP, navigation explicite de l'utilisateur) ; pas de télémétrie.
- Skills `/codex`, `/claude-code` et voisins — appels aux CLI de modèles **par l'utilisateur**, avec ses propres clés ; pas d'appel automatique.
- `scripts/` CI — appels API GitHub explicites, déclenchés par les workflows.
- Le repo ne contient aucun exporteur ni endpoint de télémétrie (contrairement à openrig, dont la surface `/api/telemetry` locale avait été constatée au pas F8-4 — ici : rien de tel).

## 2. Dépendances

`package.json` / `bun.lock` : aucune dépendance de télémétrie. L'adapter est stdlib seule.

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (inventaire cohérent, 64 skills, 9/9 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids : le repo est des skills Markdown + code TypeScript + tests. Aucun fichier `.safetensors` / `.bin` / `.pt` / `.pth` dans le repo (vérifié au fichier).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Navigateur intégré (browse/, Chromium) | Explicite, navigation de l'utilisateur — **conservé tel quel** (comportement amont, pas une télémétrie) |
| Appels CLI de modèles (codex, claude-code) | Explicites, clés de l'utilisateur — **conservés tels quels** |
| Appels API GitHub (CI) | Explicites, workflows — **conservés tels quels** |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
