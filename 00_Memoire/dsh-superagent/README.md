# Bundle Superagent — `00_Memoire/dsh-superagent/`

Configuration Superagent d'A'Space, **écrite depuis la spécification du contrat** (`AGENTS.md` §§2–4) et du design signé Clara (D-N049) — **sans copie de code amont**.

## Contenu

| Fichier | Rôle |
|---|---|
| `config.json` | Bundle : port, `stateDir`, presets, `github-watch`, Shared Brain, `factory.sqlite`, `modelPool`, plafonds, pulsation, déclencheurs D9 par Worker, protocole gelé D12 |
| `profiles/worker.json` | Preset `worker` (les 6 Compagnons non-routers) |
| `profiles/router.json` | Preset `router` (Nardole, Clara, Ryan) — étend `worker.json` |
| `scripts/derive-memory-snapshot.py` | Régénération déterministe de `memory.json` depuis `memory.jsonl` (D4) |

## Installation (D2)

Le profil machine-local `~/.dsh/profiles/superagent` est un **lien symbolique** vers `profiles/` :

```sh
ln -s <repo>/00_Memoire/dsh-superagent/profiles ~/.dsh/profiles/superagent
```

Si aucun lien n'est possible : copie + vérification de hash à chaque démarrage du Worker (écart = le Worker refuse de démarrer et pulse une anomalie).

## DSH épinglé

**0.2.1-rc.5** (design D-N049). Une version installée différente est une **déviation nommée**, consignée dans le reçu du Worker — pas un échec. **Oh My Pi n'est pas une dépendance.**

## Protocole (D12)

Fork souverain `Amdkn/dsh-superagent-prototype`, gelé sur `8c32a9d` (HEAD de `main` amont, 2026-10-31). **Référence seule** — pas un sous-module, pas dans `.gitmodules`, pas dans le compteur C. Revisite par signal de dérive (règle D-N048 D5), jamais de fast-forward silencieux.

## Shared Brain (D3, D4)

Nom d'usage : **« Shared Brain »** (Gateway MCP Mémoire Partagée, `00_Memoire/shared_brain/`).

- `memory.jsonl` = seule source de vérité.
- `memory.json` = instantané dérivé, régénéré par `scripts/derive-memory-snapshot.py`.
- Déduplication à l'écriture : `search_nodes` avant toute création d'entité ; un nom déjà présent est refusé en création — on ajoute des observations à l'entité existante.
- Le doublon `Muse_Browser_Agent` a été purgé une fois (vague T1, D-N049) : fusion en un seul enregistrement, relations dédupliquées, purge consignée dans `log.md`.

## Déclencheurs (D9)

Table exacte par Worker dans `config.json` (`triggers`). Latence < 5 min.

## Plafonds (D10)

1 % du pool restant par Worker, 5 % pour la mission. Alerte à 80 %, arrêt à 100 %. Mesure à la comptabilité du fournisseur, consignée dans le reçu de chaque Worker. **La dépense n'est pas mesurable depuis la factory — le reçu le dit honnêtement, sans chiffres inventés.**

## Pulsation (D11)

Pulsation à chaque étape + battement toutes les 30 min, même à vide. Plus de 2 h sans pulsation (4 battements manqués) = anomalie, routée à Yaz (watchlist) et à Rick.
