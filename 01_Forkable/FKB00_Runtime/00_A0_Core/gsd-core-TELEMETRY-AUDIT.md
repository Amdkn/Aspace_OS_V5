# Audit télémétrie — gsd-core (D-N053 pas C, H-M4)

**Module :** `gsd-core` — fork `Amdkn/gsd-core`, gel `cb15dcf1`, adapter `adc42da`.
**Verdict : TÉLÉMÉTRIE ZÉRO par contrat.** Aucun SDK de télémétrie, aucun appel réseau en arrière-plan, aucun appel à l'import. Les seuls appels réseau du repo sont des endpoints locaux configurés par l'utilisateur (modèles locaux, mémoire locale) et une vérification de version explicite, jamais déclenchés par l'adapter.

## 1. Scan statique du code amont (au gel)

Motifs cherchés dans `gsd-core/bin/` et `scripts/` : `posthog|sentry|amplitude|mixpanel` → **0 hit**.
Motif `telemetry` (mot seul) : **0 hit** dans `gsd-core/bin/lib/` et `scripts/run-tests.cjs`.
L'adapter est **stdlib seule** (0 import réseau dans `aspace_gsd_core_adapter/__init__.py`, vérifié : 0 hit).

### Sites réseau explicites (tous déclenchés par l'utilisateur, jamais en arrière-plan)

- `gsd-core/bin/lib/capability-registry.cjs` — hôtes par défaut **loopback locaux** : `http://localhost:11434` (Ollama), `http://localhost:1234` (LM Studio), `http://localhost:8080` (MemPalace). Ce sont des endpoints de modèles / mémoire **locaux**, configurés par l'utilisateur ; aucune donnée ne sort de la machine par défaut.
- `gsd-core/bin/check-latest-version.cjs` — vérification de version déterministe via `npm view gsd-core version` (nom de paquet constant en code, #2992) ; **explicite**, déclenchée par le workflow `/gsd-update` uniquement, jamais à l'import.
- `gsd-core/bin/lib/package-identity.cjs:9` — constante `repoUrl = "https://github.com/open-gsd/gsd-core"` (chaîne, pas un appel).
- `gsd-core/bin/lib/capability-registry.cjs` — références `https://mempalaceofficial.com/reference/cli.html` (documentation dans des fragments de prompts, pas des appels).
- Les tests d'intégration (`--suite integration`) et de sécurité (`--suite security`) sont **hors borne** D-C2 ; jamais exécutés ici.

## 2. Dépendances

`package.json` : aucune dépendance de télémétrie déclarée (vérifié : 0 hit `posthog|sentry|amplitude|mixpanel|telemetry` dans les dépendances). L'adapter est stdlib seule.

## 3. Preuve d'exécution — namespace sans interface

`unshare -n` (aucune interface réseau, DNS en échec) : `validate()` + `doctor()` réussissent (inventaire cohérent, 9/9 contrôles ok). Log : `logs-netns-validate.log`. **0 appel sortant possible dans ce namespace — la preuve est structurelle, pas déclarative.**

## 4. Poids dans le fork

Aucun poids : le repo est du code Node/TypeScript + skills Markdown + workflows. Aucun fichier `.safetensors` / `.bin` / `.pt` / `.pth` dans le repo (vérifié au fichier).

## 5. Déclencheurs tranchés

| Déclencheur | Décision |
|---|---|
| Endpoints loopback locaux (Ollama 11434, LM Studio 1234, MemPalace 8080) | Locaux, configurés par l'utilisateur, 0 donnée sortante par défaut — **conservés tels quels** |
| Vérification de version `npm view` (/gsd-update) | Explicite, workflow uniquement — **conservée telle quelle** |
| Constante repoUrl / liens de documentation | Chaînes, pas des appels — **conservées telles quelles** |
| SDK de télémétrie | Aucun — **rien à retirer** |
| Appel réseau à l'import | Aucun (prouvé en netns) — **rien à retirer** |
| Poids montés dans le fork | Aucun — **conforme** |

## 6. Ré-audit

À chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état.
