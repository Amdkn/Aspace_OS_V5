# Fiche d'adaptation — herdr-app (D-N048 V3a)

**Adresse :** `fiber:a0:herdr-app`
**Manifeste :** `herdr-app.manifest.json` (même domicile)
**Audit télémétrie :** `herdr-app-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 2 Vérifié (hold-outs verts + validation 13e, PR #9 mergée `d0631f1`)
**Licence :** Apache-2.0

## Commit gelé

- **Fork :** `Amdkn/herdr-app` (parent `herdrdev/herdr-app`, Apache-2.0, branche `master`).
- **Gel : `b1a2a67`** — version 0.1.14.
- **Correction de création nommée :** le fork a d'abord été créé sur le HEAD courant de l'amont (`8138954`, 4 commits après le gel) ; la référence `master` a été ramenée au gel par mise à jour forcée de la ref (SHA complet, corps JSON — `gh api -f force=true` rejeté). `b1a2a67` est l'ancêtre strict de `8138954` (merge-base vérifié).
- **Gitlink V5 :** `7fe7ac3` → `b1a2a67` dans cette PR (avance fast-forward, ancêtre strict, 28 commits).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Adapter

- **Dossier :** `aspace-herdr-app-adapter/` (contrat JSON + smoke test shell + README), commit `2baee17` sur le fork. **Seul code A'Space du fork** — le code amont est byte-identique au gel.
- **Surface (contrat seul, §1.5) :** sous-commandes qui parlent seulement (AGENTS.md amont) — `herdr-app --help`, `--skill` (imprime `src/SKILL.md`), `--version`, `check <mod>`, `types <mod>`.
- **Jamais :** lancer la fenêtre sans `HERDR_APP_HOME` scratch (AGENTS.md amont), tout envoi télémétrie (`DO_NOT_TRACK=1` + `HERDR_TELEMETRY=0` forcés), tout appel réseau.
- **Couture Rust↔TS (§2) :** contrat seul — aucune couture spécifique construite.
- **Smoke test :** `bash aspace-herdr-app-adapter/smoke_test.sh` (binaire debug, maison scratch, interrupteurs forcés ; vérifie `--version` 0.1.14, `--help`, `--skill`).

## Tests au gel et sur le fork adapté

- **Au gel `b1a2a67` : bun 67 passés, 0 échec (7 fichiers) ; cargo 386 passés, 0 échec, 1 ignoré** (387 tests, `cargo test --locked`, 12,49 s). Premier run : 383/3/1 — les 3 échecs étaient des tests de rendu GPU (`No usable headless GPU adapter found`, VM sans pilote Vulkan) ; après `apt-get install mesa-vulkan-drivers` (lavapipe), les 3 passent. **Smoke test adapter vert** (`smoke herdr-app OK — version 0.1.14, --help, --skill`).
- **CI amont :** `just test` = `bun test scripts/*.test.ts` + `cargo test --locked` (Rust 1.95.0, Zig 0.16.0, `CARGO_PROFILE_DEV_DEBUG=1`, `CARGO_INCREMENTAL=0`).
- **Limite franche :** Zig absent de cette VM — installé manuellement (0.16.0, `~/workspace/.tmp/zig-x86_64-linux-0.16.0`) pour `ghostty-sys`. Le client HTTP de zig ne passe pas le proxy de la VM : les 36 paquets de la fermeture (`uucode`, `translate-c`, `arocc`, `wuffs`, `pixels`, + 31 autres) ont été téléchargés avec curl puis mis en cache par `zig fetch` local ; `zigimg` cloné avec git au commit épinglé. Dépendances système installées pour la suite : `libclang-dev`, `clang` (18.1.3, binaire `clang` exigé par build.rs), `libxkbcommon-x11-dev`, `mesa-vulkan-drivers` (lavapipe, sans quoi 3 tests GPU échouent). Les fetches git de Cargo (`quickjs-jit`, `llrt`) sont lents via le proxy de la VM.

## Télémétrie

**Coupée par contrat (module réel dans l'amont).** Voir `herdr-app-TELEMETRY-AUDIT.md` : `src/telemetry.rs` — rapport anonyme 1/jour, ON par défaut, coupé par `DO_NOT_TRACK` / `HERDR_TELEMETRY=0` / CI ; seuls les builds release (`HERDR_APP_RELEASE`) envoient. L'adapter force les deux interrupteurs et ne construit que du debug.

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Règles maison amont respectées (AGENTS.md) :** la racine `AGENTS.md` amont n'a PAS été éditée (H-M2) ; l'adapter ne touche pas au cœur de l'app (le cœur reste petit, tout le reste est en mods — règle du mainteneur) ; aucune modification du comportement agent (`defaults/AGENTS.md`, `src/SKILL.md`).
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md`.
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`.
- Fork : https://github.com/Amdkn/herdr-app (gel `b1a2a67`, adapter `2baee17`).
