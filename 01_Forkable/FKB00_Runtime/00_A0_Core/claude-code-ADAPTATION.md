# Fiche d'adaptation — claude-code (D-N048 V3b, variante D12)

**Adresse :** — (D12 : pas d'adresse `fiber:a0:*` tant qu'aucune adaptation clean-room n'est validée par le 13e)
**Manifeste :** `claude-code.manifest.json` (même domicile, `id: null`)
**Audit télémétrie :** `claude-code-TELEMETRY-AUDIT.md` (même domicile)
**Statut :** état 0 Basique → 1 Adapté en cours (fiche + adapter clean-room + manifeste, smoke vert)
**Licence :** **sans licence** (voir ci-dessous)

## Commit gelé

- **Fork :** `Amdkn/claude-code` (parent `anthropics/claude-code`, branche `main`).
- **Gel : `0ed9469`** — `0ed94698aa0aeee471465fc9c867c2e8434c4d68`.
- **Correction de création nommée :** le fork a d'abord été créé sur le HEAD courant de l'amont (`fd1f3c4`) ; la référence `main` a été ramenée au gel par mise à jour forcée de la ref (SHA complet, corps JSON).
- **Tout commit amont ultérieur exige un amendement de design**, jamais un fast-forward silencieux (D5).

## Licence — sans licence (D12)

- L'API GitHub rapporte `license: null` pour l'amont.
- Le fichier `LICENSE.md` du dépôt dit : « © Anthropic PBC. All rights reserved. Use is subject to Anthropic's Commercial Terms of Service » — un **avis propriétaire, pas une licence libre**.
- **Variante D12 (design D-N048, D4, §6) :** fork = **référence seule** ; adaptation = **clean-room** (écrite depuis la spécification publique, aucune copie de fichier amont) ; **repli suppression nommé** : si Anthropic s'oppose à la référence ou si une licence apparaît qui l'exige, le fork est supprimé ; amendement si une licence apparaît.

## Adapter — clean-room, zéro copie

- **Dossier :** `aspace-claude-code-adapter/` (contrat JSON + faux local + smoke test + README), commit `f2965df` sur le fork. **Seul code A'Space du fork** — écrit de zéro.
- **Surface (contrat seul, §1.5) :** description de l'interface documentée — commande `claude`, modes de permission (`auto`, `acceptEdits`, `default`), commande `/bug`, mentions `@claude`, clés de settings nommées dans les exemples, événements de télémétrie documentés et leurs interrupteurs. Le faux local (`mock_claude.py`, stdlib seule) implémente `--help`, `--version`, `status` — jamais le CLI amont, jamais un appel réseau.
- **Preuve zéro copie :** diff gel→HEAD = 4 fichiers adapter seuls (nouveaux chemins) ; **aucun des 4 contenus n'existe parmi les 1 479 blobs de l'arbre du gel** (comparaison de hashes, consignée dans `logs-claude-code-suite.log`).
- **Smoke test :** `python3 aspace-claude-code-adapter/smoke_test.py` — **6/6 checks pass** (contrat valide, `--help`, `--version`, `status`, zéro code réseau dans l'adapter, stdlib seule).

## Tests au gel

- **Suite amont : NON courue (variante D12)** — une suite amont validerait du code amont, pas l'adaptation. Preuve à la place : diff gel→HEAD + comparaison de blobs + smoke du contrat clean-room (voir ci-dessus).
- **Ce qui a tourné :** smoke test de l'adapter (6/6), vérifications API (fork au gel, licence nulle), comparaison de blobs. **Ce qui n'a pas tourné :** la suite amont (hors variante D12, par décision du design).

## Télémétrie

**Réelle dans l'amont, zéro dans l'adaptation.** Voir `claude-code-TELEMETRY-AUDIT.md` : collecte d'usage et de conversations déclarée par l'amont (README), ingest documenté `https://api.anthropic.com/api/event_logging/v2/batch` (mod `mods/telemetry/`), interrupteurs `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` / `DO_NOT_TRACK` lus avant chaque lot. **L'adapter n'émet rien, par construction** (aucun code réseau ; vérifié par le smoke test).

## Divergence (dette portée par le cœur Buzz, lane Clara / 12e)

- **Ré-audit télémétrie :** à chaque changement de commit gelé ou d'adapter, et au minimum à chaque transition d'état (D3).
- **Repli suppression :** si Anthropic s'oppose, le fork est supprimé ; l'adapter clean-room survit (il ne dépend d'aucun fichier amont).
- **Amendement :** si une licence apparaît pour l'amont, la variante D12 est réexaminée (le fork pourrait passer en adaptation normale ou être supprimé).

## Références

- Design D-N048 (Clara, 2026-11-09) : `~/workspace/v4-factory/plans/FORKS-AMONT-21-plan-borne-vagues.md` (D4, §2 ligne 5, variante D12 §6).
- Évidences : `~/workspace/v4-factory/evidence/D-N048/PROGRESS-D-N048.md`, `logs-claude-code-suite.log`.
- Fork : https://github.com/Amdkn/claude-code (gel `0ed9469`, adapter `f2965df`).
