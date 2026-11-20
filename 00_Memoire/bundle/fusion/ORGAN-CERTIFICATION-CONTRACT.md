---
okf_version: "0.2"
type: Specification
title: "Organ Certification Contract — Promotion PARTIEL vers FUSIONNÉ"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ORGAN-CERTIFICATION-CONTRACT — Contrat Normatif de Certification

## 1. Gate d'Entrée Pré-Portage (Decision Gate — 5 Conditions Bloquantes)

Aucune ligne de code d'un nouvel organe ne peut être écrite ni fusionnée tant que les 5 conditions suivantes ne sont pas documentées et validées :
1. **Clôture amont vérifiée** : le cycle/vague précédent dispose de tous ses commits publiés, d'une CI Porte B verte sans erreur silencieuse, de ses reçus R10 et d'un bilan honnête de ses limites offline.
2. **Contrat de fusion du candidat figé** : module ID exact (`Mxxx`), noyau `ADR-15` (`ÂME` / `SYSTÈME NERVEUX` / `CORPS`), organe cible (`K1..K5`), chemin de destination, périmètre inclus et sous-systèmes explicitement exclus ou différés.
3. **Stratégie d'oracle définie** : mécanisme exact permettant d'exécuter le code amont réel en Phase A sans dépendance réseau non déterministe, et inventaire complet des seuils/arrondis/retries/fichiers à tester selon `THRESHOLD-AND-PARITY-SPEC.md`.
4. **Critères de suppression physique établis** : liste des répertoires amont détruits en Phase B (`_force_rmtree`), localisation des copies d'entrées brutes en lecture seule, et preuve que l'organe cible n'importe rien du sous-module.
5. **Critères d'acceptation de promotion `FUSIONNÉ` approuvés** : seuils exacts de cas comparés, nombre minimum de sabotages exigés, et vérification des dépendances CI requises dans `.github/workflows/foundation-proof.yml`.

---

## 2. Contrat d'Interface Organe Natif & Bus L0

1. **Zéro auto-certification** : la fonction `run_<organ>_self_test(...)` peut vérifier la plomberie interne sur données synthétiques et consigner un reçu `*-SMOKE`, mais doit impérativement retourner `"source_parity_verified": []` et ne jamais revendiquer de statut `FUSIONNÉ`.
2. **Consignation R10 mesurée** : seule la fonction `consign_<organ>_parity_receipt(module_results, head_sha40, repo_root=...)` (appelée par la suite de vérification après Phase C) inscrit sur le bus L0 (`EventJournal` + `R10Ledger` dans `aspace_foundation_kernel.py`) les modules pour lesquels `compared_against_source == True`, `cases_compared > 0` et `cases_matched == cases_compared`.
3. **Rattachement ADR-15** : tout organe est rattaché à l'un des 3 Noyaux (`ÂME`, `SYSTÈME NERVEUX`, `CORPS`). Les organes financiers/trading incluent en outre le verrou `READ_ONLY_VETO_S0 = True` (`ADR-07`).

---

## 3. Contrat d'Oracle Différentiel, Suppression Physique et Sabotage

1. **Phase A (Oracle amont réel)** : exécute les scripts/modules réels du sous-module avant toute modification. Aucun mock ne peut être utilisé pour prétendre qu'une interaction live externe (UI Windows Win32, navigateur CDP live, appel HTTP réseau authentifié) a été prouvée.
2. **Phase B (Amputation physique effective)** : supprime physiquement les répertoires amont dans `iso_root` par `_force_rmtree` et bloque sur `assert not target.exists()`.
3. **Phase C (Parité `==` stricte & Sabotage total)** :
   - Compare les sorties par égalité stricte `py_out == oracle[module_id]`.
   - Chaque fonction déclarée, chaque seuil `N-1 / N / N+1`, chaque règle d'arrondi, chaque politique de retry/erreur et le refus des clés parasites doivent disposer d'un test de sabotage vérifiant l'échec effectif de `verify_<module>()`.
   - Une clause `assert parsed["sabotages_detected"] >= <nouveau_plancher>` interdit toute régression silencieuse de couverture.

---

## 4. Critères de Promotion `PARTIEL -> FUSIONNÉ` & Statut `PARTIEL` Honnête

- Un module ne passe de `PARTIEL` à `FUSIONNÉ` dans `REGISTRE-DE-FUSION.md` que lorsque :
  1. Le code est porté nativement sans dépendance runtime vers le sous-module ;
  2. La bijection `CARTE-DES-PRINCIPES.md <-> REGISTRE-DE-FUSION.md` et l'égalité dynamique `registry_fusionne == proven_fusionne` passent ;
  3. Les 3 suites (`test_foundation_deletion_suite.py`, `01_Forkable/check-modules-lock.py`, `02_Factory/checks.ps1`) retournent `0` localement et sur GitHub Actions CI (`foundation-proof.yml`, sans `continue-on-error` ni `|| true`).
- Tout module dont le cœur comporte des dépendances live non exercées (`M058` UIA Win32 live, `M066` CDP live), des runtimes inaccessibles en CI (`M095` `bpy`), ou aucun exécutable prouvé par oracle (`M120` documentation seule) reste **strictement `PARTIEL`**.
- Les gitlinks des modules prouvés par oracle sont conservés dans `.gitmodules` pour le rejeu continu Phase A, tandis que la preuve d'autonomie sans dépendance amont est apportée à chaque exécution dans `iso_root` amputé.
