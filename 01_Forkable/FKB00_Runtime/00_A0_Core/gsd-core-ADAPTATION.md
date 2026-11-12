# Fiche d'adaptation — gsd-core (D-N053 pas C)

**Module :** `gsd-core` — `open-gsd/gsd-core`, fork `Amdkn/gsd-core`, branche `next`.
**Gel :** `cb15dcf1` (« docs(#5307): list beads in the Community Capability Registry (#5384) »).
**Bind 4L :** `d8c51c5` (créé pendant le pas, parent = gel, patron D8 / pas A autogluon) sur la branche `aspace-v5-native` ; re-appliqué verbatim sur `next` : `1214039` (blob byte-identique, vérifié).
**Adapter :** `adc42da` (parent = gel, 3 fichiers, +356/−0, `aspace-gsd-core-adapter/` : `__init__.py`, `README.md`, `tests/test_smoke.py`, stdlib seule).
**Licence :** MIT (vérifiée au fichier). **Niveau cible :** 1 (Adapté).
**Coordination :** référence du canonique superpowers (§D5). Ancien fork `Amdkn/get-shit-done` non touché (H-A7) — le gitlink V5 est re-pointé par renommage `get-shit-done` → `gsd-core` (D-C1 option (a)).

## Inventaire (au gel, vérifié au fichier)

- `gsd-core/bin/lib/` : **9 sources `.cjs` suivies** (+ `vendor/`) — la mesure brute sur disque (265 .cjs) est polluée par `npm run build:lib` (ADR-457 : artefacts `.cjs` gitignored compilés dans ce dossier ; 256 fichiers après build, 270 entrées sur disque). La mesure porte sur les 9 sources suivies (`bin_lib_expected_present`).
- `gsd-core/bin/` : `check-latest-version.cjs`, `ensure-runtime-build.cjs`, `gsd-tools.cjs`, `gsd_run`, `lib/`, `shared/`, `verify-reapply-patches.cjs`.
- **Workflows : 91 fichiers à la racine + 18 sous-dossiers (187 fichiers)** — la mesure « 109 » du Discover comptait les entrées sans distinguer fichiers et dossiers.
- `skills/` : 72 entrées, **72 SKILL.md**. `agents/` : 64 fichiers `.md`. `commands/gsd`.
- Registre de capacités : `capability-registry.cjs` 8 518 lignes (généré), `docs/registries/capability-registry.md` 136 lignes, 7 sections.
- `.claude-plugin/plugin.json`, `.opencode/`, `scripts/run-tests.cjs`.
- Pas de `AGENTS.md` dans le repo (vérifié : absent).

## Suite bornée D-C2 — TERMINÉE (voir NOTE-CORRECTION-BASELINE.md)

Commande : `node scripts/run-tests.cjs --suite unit` après `npm run build:lib` (`npm ci` : 398 packages, exit 0 ; `build:lib` : exit 0). 1 169 fichiers, 27 chunks en run séquentiel.
Environnement final : umask ambiant 0007, `RUN_TESTS_CHUNK_TIMEOUT_MS=1800000` (override opérateur supporté par le runner, défaut 600 000 — voir note § causes point 5), `TMPDIR=/var/tmp/.tmp-pas-c` (hors $HOME → #3712 passe) + `GIT_TEMPLATE_DIR=/var/tmp/git-templates` (templates git sur le même tmpfs → `git init` OK — voir note § causes point 8 ; `/var/tmp` effacé à chaque reboot, recréé à chaque lancement).
Exécution : 3 shards séquentiels `--shard i/3` (389+390+390 fichiers, partition déterministe sig `cfacde7f`) — la VM reboote périodiquement, un run séquentiel complet ne survit pas.

| Run | Gel (`cb15dcf1`) | Adapté (`1214039`) |
|---|---|---|
| Shard 1/3 | **16 379 pass / 1 fail** (exit 1) — #1634 (umask 0007, mode 640 vs 644) | **16 379 pass / 1 fail** (exit 1) — #1634, IDENTIQUE |
| Shard 2/3 | **17 913 pass / 2 fail** (exit 1) — npm-audit 403 (proxy VM) + pi-package timeout flaky (30 s) | **17 914 pass / 1 fail** (exit 1) — npm-audit 403 seul ; pi-package PASSE ici |
| Shard 3/3 | **15 794 pass / 0 fail** (exit 0) | **15 794 pass / 0 fail** (exit 0) — IDENTIQUE |
| **Total** | **50 086 pass / 3 fail** | **50 087 pass / 2 fail** |

**Delta gel → adapté : +1 pass / −1 fail = le test flaky pi-package (`pi-package.test.cjs:152`, timeout 30 s sous contention), passé au run adapté. Zéro échec imputable à l'adapter.** Les 2 échecs restants sont environnementaux et identiques dans les deux runs (#1634 umask ; npm-audit 403, proxy de sortie de la VM — vérifié manuellement). H-C3 gsd-core : NON VERT strict (2 fails environnementaux) — à juger par le coordinateur/13e, même posture que H-C3 gstack ; **aucune réduction appliquée** (D-C2).

Historique : runs 1–3 sur l'arbre adapté par erreur de checkout (conservés comme évidence, pas comme bilan) ; run 5 = chunk 10 tué par le timeout 600 s (umask 0022) ; run 6 = chunk 1 tué par le timeout 600 s ; run 7 tué par reboot de la VM (chunks 1–7 : 2 981/0) ; shard 1 adapté tentative 1 : 16 285/79 (orage EPERM sandbox ~15:38–15:43 UTC, chunks 4–5 — même fichier 74/0 puis 39 fails hors runner sur le même arbre, preuve environnementale ; log `logs-suite-adapte-shard1-eperm-orage.log`) ; shard 3 adapté tentative 1 tué par reboot VM à 6/9 (9 395/0, log `logs-suite-adapte-shard3-tue-reboot-6sur9.log`). Détail complet : `NOTE-CORRECTION-BASELINE.md`.

## Smoke (adapter, `pytest` 9.2.0)

`validate()` + `doctor()` : **6/6**. Namespace sans interface (`unshare -n`) : **9/9** (dont `validate()` + `doctor()` en netns, 0 appel sortant possible).

## Télémétrie

**ZÉRO.** Audit : `gsd-core-TELEMETRY-AUDIT.md`. 0 SDK ; seuls hôtes = loopback locaux configurés par l'utilisateur (Ollama 11434, LM Studio 1234, MemPalace 8080) + `npm view` explicite via `/gsd-update` ; `repoUrl` = constante, pas un appel. Prouvé en netns (0 appel sortant possible).

## Corrections de mesure (ce pas)

1. Workflows 109 → **91 fichiers racine + 18 dossiers (187 fichiers)**.
2. `bin/lib/` : mesure sur les **9 sources suivies**, pas le disque brut (build ADR-457).
3. SKILL.md : n/a (pas de correction ; 72/72 cohérents).

## Réserves

1. Suite bornée terminée : **50 087/2 adapté vs 50 086/3 gel** — delta = flaky pi-package ; 2 échecs environnementaux identiques (#1634 umask, npm-audit 403) ; H-C3 NON VERT strict, à juger.
2. Build `build:lib` génère 256 `.cjs` gitignored dans `bin/lib/` (ADR-457) — artefacts de build, pas du code suivi.
3. Ancien fork `Amdkn/get-shit-done` non touché (H-A7) ; le gitlink V5 est renommé, pas le fork.
4. Aucun secret, aucune dépense, aucune activation client, aucun test sur numéro réel.
