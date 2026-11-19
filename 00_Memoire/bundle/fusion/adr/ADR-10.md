---
okf_version: "0.2"
type: Decision
title: "ADR-10 — Contrat de Fibre Spatio-Temporel Unique vs Silos d'Outils & Skills"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-10 — Contrat de Fibre Spatio-Temporel Unique vs Silos d'Outils & Skills
- **Statut** : `ACCEPTÉE`
- **Conflit** : Les catalogues d'outils et compétences sont fragmentés entre `a0-plugins`, `anthropic-skills`, `mattpocock-skills`, `openai-plugins`, `impeccable`, `API-Anything`, `CLI-Anything`, `Scrapling`, `agent-browser`, `agent-desktop`, `rea`, `superpowers`, `dox`, `deepseek-harness`.
- **Décision** : Toute capacité opérationnelle est enregistrée dans l'hôte de fibres (`aspace-fiber-host` / `RigInfinity` avec ID `fiber:a0:*` unique et `capabilities_owned` disjoints dans `MODULES-LOCK.json`) ; toute compétence procédurale suit le format unifié `SKILL.md` à divulgation progressive ; tout pilotage logiciel privilégie la hiérarchie **API (`api-anything`) -> CLI (`CLI-Anything`) -> Arbre d'accessibilité sans vol de focus (`agent-browser` CDP `@ref` / `agent-desktop`)**.
- **Invariant** : 1 capacité = 1 seul propriétaire dans `MODULES-LOCK.json` ; vérification automatisée par `check-modules-lock.py` check #4.
- **Modules résolus** : `cordis`, `aspace-fiber-host`, `a0-plugins`, `deepseek-harness`, `openrig`, `CLI-Anything`, `api-anything`, `agent-browser`, `agent-desktop`, `rea`, `Scrapling`, `impeccable`, `anthropic-skills`, `mattpocock-skills`, `claude-video`, `dox`, `superpowers`.
