# Fiche d'adaptation — Automaton (D-N051 F8, pas 1)

**Adresse :** `fiber:a0:automaton` (l'Âme — D2 : émetteur exécution ;
validateur 13e)
**Manifeste :** `automaton.manifest.json` (même domicile)
**Audit télémétrie :** `automaton-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter + manifeste ;
**H-M3 ROUGE, jugement 13e requis** — voir § Tests)

## Commit gelé

- **Fork :** `Amdkn/automaton` (parent `Conway-Research/automaton`, MIT,
  branche `main`).
- **Gel : `e025526`** (`e0255269f2fd6b3940a8398424fdff3aec940ba0`) —
  « feat(aspace): integrer doctrine souveraine A0 Amadeus CEO Holon et
  outils holoniques », 2026-11-06 03:32:10 -05:00. Le gel EST le commit de
  doctrine A'Space : il contient déjà `constitution.md`,
  `src/aspace/holon-topology.ts`, `src/agent/aspace-holon-tools.ts` et les
  ajouts `src/heartbeat/tasks.ts` (40 lignes) — code A'Space sur `main`,
  non touché par l'adapter, qui part en natif via Ryan à ce pas.
- **Vérifié au fichier :** clone local `~/workspace/automaton-repo`,
  216 fichiers, HEAD = gel, arbre propre avant adaptation.
- **Tout commit amont ultérieur exige un amendement de design**, jamais un
  fast-forward silencieux (D1).

## Adapter

- **Paquet :** `aspace-automaton-adapter/` (`@aspace/automaton-adapter`
  0.1.0), commits `2d25016` + `7cdaa00`
  (`7cdaa00fb7464046dcb2016896f48f60b5426a8b`, HEAD) sur le fork.
  **Seul code A'Space du fork** (D6) — l'amont est byte-identique
  au gel (H-M2 vérifié à l'API : compare gel...HEAD = ahead 2, behind 0,
  exactement les 6 fichiers adapter, 2 commits). Le 2e commit corrige le
  smoke : `verifyFrozenCommit()` (HEAD == gel) échoue par construction
  une fois l'adapter commité — remplacé par `verifyFrozenLineage()`
  (gel ancêtre de HEAD + `gel..HEAD` limité au dossier adapter).
- **Surface :** `isOutboundAllowed(url, extraHosts?)` (politique pure) ;
  `installOutboundGuard({ allowHosts })` → `restore()` (enveloppe le
  `fetch` global, refuse avant tout accès réseau) ; `getFrozenRepoInfo()`
  / `verifyFrozenCommit()` / `verifyFrozenLineage()` (lectures git locales
  via le helper amont `getRepoInfo()` ; la lignée prouve D1 + H-M2 en
  local) ; `ASPACE_HEARTBEAT_OVERRIDES`
  (`check_for_updates: { enabled: false }`) ; `TELEMETRY_BLOCKLIST`
  (16 motifs, refusés même allow-listés).
- **Smoke tests :** 21/21 verts (`npx tsx
  aspace-automaton-adapter/smoke_test.ts`), re-courus 19/19 sous
  `unshare -n` (zéro interface réseau — zéro egress physiquement
  possible). `tsc --noEmit` propre sur l'adapter.

## Tests au gel et sur le fork adapté

- **Commande CI :** `vitest run` (`test:ci` = `vitest run
  --reporter=verbose`). 65 fichiers, 1 647 tests au total.
- **Sur le fork adapté (après rebuild du binding natif — voir §
  Contraintes) : 1 646 passés, 0 échoué, 0 ignoré ; 1 test bloqué
  (jamais terminé — voir ci-dessous).** 64/65 fichiers verts ; le
  65e (`src/__tests__/context-hardening.test.ts`, 29 tests) : 28 verts,
  1 bloqué.
- **Les 3 tests lents** (`buildContextMessages token budget`) :
  « summarizes old turns when budget is exceeded » (5 tours × 50 000
  car.), « preserves most recent turns when summarizing » (5 × 50 000
  car.), « does not summarize when only one turn exists » (1 × 500 000
  car.).
- **Cause racine prouvée, code amont, pré-existante au gel :**
  `estimateTokens` (`src/agent/context.ts:36`) appelle
  `countTokens` (`src/memory/context-manager.ts:141`), qui appelle
  `encoder.encode()` de `js-tiktoken` (cl100k_base) **sans garde de
  longueur**. Mesuré en direct : `encode("x".repeat(n))` est
  quadratique — 1 000 car. → 259 ms, 5 000 → 2,7 s, 10 000 → 10,9 s,
  20 000 → 42,8 s (×4 par ×2 de longueur) — alors qu'un texte réaliste
  de 54 000 car. s'encode en 12 ms. Extrapolation : 50 000 car. ≈ 270 s
  par appel ; 500 000 car. ≈ 7 h. Les tests utilisent `"x".repeat()`
  (course dégénérée d'un seul caractère) : la boucle BPE de js-tiktoken
  explose sur ce contenu. Le spin est synchrone : le timeout vitest de
  30 s ne peut pas interrompre une boucle synchrone — le worker reste à
  ~92 % CPU (observé 6 min, tué par l'auditeur).
- **Confirmation empirique (2026-11-10) :** « summarizes old turns when
  budget is exceeded » (5 × 50 000 car.) **passe en 273,7 s**
  (`logs-automaton-context-hardening-50k-confirm.log`) — la prédiction
  quadratique (≈ 268 s) est vérifiée. Les deux tests à 50 000 car.
  passent donc, au prix de ~4,5 min de CPU chacun. Le test à 500 000
  car. n'a pas été exécuté : ~7 h prédites, il bloque l'achèvement de
  la suite en pratique — c'est le seul test non vert. Bilan final :
  **1 646 passés / 0 échoué / 1 bloqué (~7 h) sur 1 647.**
- **Ce n'est PAS un échec de l'adapter :** l'adapter ne touche aucun
  fichier amont ; le défaut est dans `src/agent/context.ts` +
  `src/memory/context-manager.ts` + `js-tiktoken`, tous amont. Le
  correctif appartient à l'amont (garde de longueur / repli sur
  l'heuristique caractères au-delà d'un seuil dans `estimateTokens`, ou
  découpage avant `encode`) — hors périmètre de cette mission, qui
  interdit de modifier un fichier amont. **H-M3 est donc ROUGE et le
  passage en état 1 attend le jugement du 13e.**
- **Limites franches de l'environnement :**
  - `better-sqlite3` n'a pas de binaire précompilé pour Node 24.22.1
    sur cette VM ; son build natif échoue d'abord sur `fchown` EPERM
    (extraction des headers Node dans un namespace sans CAP_CHOWN) —
    contourné par extraction manuelle des headers
    (`~/.cache/node-headers-24.22.1`) + `node-gyp rebuild --nodedir`.
    Le binding a été reconstruit **deux fois** : le `pnpm install
    --ignore-scripts` relinké après le premier build a effacé `build/`,
    invalidant la première passe de suite (tous les tests SQLite en
    échec « Could not locate the bindings file » — log de la passe
    invalide écrasé avant la re-passe, non compté ici). La passe comptée
    (1 618 verts) a tourné **après** le rebuild final, avec 0 erreur
    de binding.
  - `npm ci` refuse (le `package-lock.json` amont est incomplet) ;
    installation via `pnpm@10.28.1 install --frozen-lockfile
    --ignore-scripts` (208 paquets, lock pnpm faisant foi).
  - `pnpm` natif absent de la VM (utilisé via `npx -y pnpm@10.28.1`) ;
    `corepack` indisponible.

## Télémétrie

**Zéro par contrat.** Voir `automaton-TELEMETRY-AUDIT.md` : scan statique
(zéro SDK télémétrie dans `package.json` / `pnpm-lock.yaml` /
`package-lock.json` ; `src/observability/*` local-only, 0 `fetch`) +
audit des dépendances + audit d'exécution (smoke 19/19 sous `unshare -n`).
Réserves : R-1 fallback Conway silencieux (neutralisé par le garde-fou),
R-2 `check_for_updates` ON par défaut (désactivé par contrat de
déploiement), R-3 tâches crédits/USDC périodiques (clé-gatées), R-4
self-mod amont (`pull_upstream`).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Encodeur de tokens quadratique sur les courses dégénérées**
  (ci-dessus) : `estimateTokens` sans garde de longueur. Tout contenu
  de plus de ~20 000 car. d'un seul caractère répété rend le runtime
  inutilisable pendant des minutes ; 500 000 car. ≈ 7 h. Le correctif
  (garde de longueur dans `estimateTokens` ou découpage) est un événement
  de design, pas un patch silencieux.
- **Fallback Conway silencieux** (`src/agent/loop.ts:155-169`) : sans clé
  OpenAI mais avec clé Conway, l'inférence part vers Conway Compute.
  Neutralisé par défaut par le garde-fou de l'adapter ; opt-in explicite
  requis.
- **`check_for_updates` ON par défaut** (`0 */4 * * *`, `git fetch origin
  main`) : l'adapter ne peut pas intercepter `child_process` git — la
  désactivation est une règle de déploiement
  (`ASPACE_HEARTBEAT_OVERRIDES`).
- **Clés et RPCs** : `check_credits` (6 h) et `check_usdc_balance`
  (5 min) émettent vers l'API Conway / le RPC chaîne dès qu'une clé est
  provisionnée ; les opérations x402 peuvent dépenser (jamais sans
  provisionnement explicite).
- **Self-mod** : `pull_upstream` / `review_upstream_changes` peuvent
  fetcher et appliquer du code amont sur initiative de l'agent — jamais
  de fast-forward silencieux (D1).
- **Ré-audit télémétrie :** à chaque changement de commit gelé ou
  d'adapter, et au minimum à chaque transition d'état (D3).

## Contraintes nommées (§2 du design)

- Runtime amont lourd (TypeScript + SQLite natif + Solana/EVM + Ollama)
  : dépendances installées par `pnpm` (208 paquets), binaire natif
  `better-sqlite3` compilé sur place (voir § Tests).
- Aucune modification d'un paquet amont ; aucun fast-forward du gel ;
  aucune copie de fichier amont dans l'adapter ; aucun secret ; aucune
  dépense ; aucun merge, aucune PR, aucun dépôt R10 (intégration par
  Ryan).
- Le bind automaton (`aspace-plugin.json` +
  `src/aspace_reserve_governor.ts`, commit `e1f361d` sur
  `aspace-v5-native`) est re-appliqué sur `main` par Ryan à ce pas, pas
  par l'adaptation.

## Références

- Design D-N051 (Clara, 2026-11-10 14:15) :
  `~/workspace/v4-factory/plans/FUSION-F8-RUNTIME-TRIPTYQUE-NATIF-plan-borne.md`
  (§6 H-M1..H-M7, §2, §D2, §D11).
- Évidences : `~/workspace/v4-factory/evidence/D-N051/` —
  `logs-automaton-suite.log` (passe comptée, 64/65 fichiers, 1 618
  passés / 0 échoué), `logs-automaton-context-hardening.log` (fichier
  seul, timeout 180 s, 0 test démarré),
  `logs-automaton-context-hardening-50k-confirm.log` (test 50 000 car.,
  passe en 273,7 s), bisection en `/tmp/ch-*.log`
  (non conservée — résultats consignés ici).
- Fork : https://github.com/Amdkn/automaton (gel `e025526`, adapter
  `7cdaa00` — 2 commits, H-M2 re-vérifié à l'API après le 2e commit).
