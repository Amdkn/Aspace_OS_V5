---
type: concept
id: ceo-automaton-cubefarm
title: "Jumeau Numérique CEO 24/7 (Automaton) & Cube Farm 3 Étages OS (01_Forkable)"
created: "2026-11-03"
updated: "2026-11-03"
sources:
  - "../../../01_Forkable/AGENTS.md"
  - "../../../01_Forkable/automaton/constitution.md"
  - "../../../01_Forkable/automaton/src/aspace/holon-topology.ts"
  - "../../../01_Forkable/cubefarm/shared/aspaceHolons.ts"
tags:
  - automaton
  - cubefarm
  - ceo-digital-twin
  - a0-amadeus
  - 01-forkable
---

# Jumeau Numérique CEO 24/7 (`01_Forkable/automaton`) & Cube Farm 3 Étages OS (`01_Forkable/cubefarm`)

## 1. Transformation de `Conway-Research/automaton` en `A0 Amadeus` (`01_Forkable/automaton`)
Le dépôt `Conway-Research/automaton` a été forké et refondu pour remplacer sa logique de survie Web4/USDC (mort à 0 crédit) par l'architecture souveraine 24/7 d'**A0 Amadeus (`aspace:a0:amadeus`)** :
- **Constitution Souveraine (`constitution.md`)** : intègre la Loi 0 (distinction `Amadou Kone` `human:amdkn` vs `A0 Amadeus`), le Triangle E-Myth (`Beth/Morty/Rick/Jerry/Summer`), les 193 Holons répartis sur les 3 OS, et le protocole d'Ambition **« Modo de Volar »** de Felix Rieseberg.
- **Topologie & Moteur d'Ambition (`src/aspace/holon-topology.ts`)** :
  - `A0_CEO_HOLON` & `ASPACE_3OS_FLOORS` (Floor 1 `tech-os` 13 Holons, Floor 2 `life-os` 43 Holons, Floor 3 `business-os` 137 Holons).
  - `upgradeTaskWithAmbition()` : élève toute tâche sur les 4 vecteurs (*Speed, Altitude, Depth, Range*).
  - `evaluateWithOutsideJudge()` : valide le livrable par le Juge Externe Indépendant (`S1-RICK`, `S3-YAZ`, `A1-BETH`, `A1-MORTY`, `B1-JERRY`).
  - Ponts directs `runAspaceFactoryCommand()` (`02_Factory/factory.ps1`) et `readAspaceWikiPage()` (`00_Memoire/`).
- **5 Outils Natifs ajoutés à Automaton (`src/agent/aspace-holon-tools.ts` & `src/agent/tools.ts`)** :
  - `aspace_3os_holon_map`, `aspace_ambition_upgrade`, `aspace_outside_judge`, `aspace_factory_spine`, `aspace_wiki_memory`.
- **Continuité 24/7 sans mort à 0 USDC (`src/heartbeat/tasks.ts`)** :
  - Ajout des heartbeats `aspace_ceo_3os_sync` et `aspace_beth_homeostasis` et maintien en vie via `aspace_sovereign_mode = enabled` (failover local `freellmapi/auto` sur `127.0.0.1:31415`).

## 2. Transformation de `leonvanzyl/cubefarm` en Immeuble Holonique à 3 Étages OS (`01_Forkable/cubefarm`)
Au lieu d'associer chaque étage à un dépôt GitHub ordinaire, **Cube Farm** représente désormais les **3 Étages OS d'Aspace OS** (`shared/aspaceHolons.ts`) :
- **Lobby (Rez-de-chaussée `G`)** : Bureau du CEO 24/7 **`A0 Amadeus`** (`server/swarm.ts`, `server/ceo.ts`) supervisant la compagnie **`A'Space OS V5 · 3-OS Holon Cube Farm`** pour **`Amadou Kone`**.
- **Étage 1 (`aspace-os/tech-os`)** : `Tech OS · L0 BedRock & Software Factory` (13 Holons `S1/S2/S3` : `S1-Rick`, `D13-Kernel`, `Ryan-Build`, `Yaz-Observe`, `Graham-State`, `D11-Life`, `Amy-Interface`, `Rory-Persistence`, `River-Flow`, `D12-Buzz`, `Bill-Research`, `Clara-Forge`, `Nardole-Dispatch`).
- **Étage 2 (`aspace-os/life-os`)** : `Life OS 2026 · L1 Cockpit 6 Frameworks × 8 LD` (43 Holons `A1/A2/A3` : `A1-Beth`, `A1-Morty`, `Orville-Ikigai`, `Zora-LifeWheel`, `Curie-12WY`, `Enterprise-PARA`, `Cerritos-GTD`, `Protostar-DEAL`, etc.).
- **Étage 3 (`aspace-os/business-os`)** : `Business OS · L2 Jerry Verse & Family Office` (137 Holons `B1..I1 + J1 + 64 DC + 64 Marvel` : `B1-Jerry`, `B1-Summer`, `B1-Book-LD01`, `C1-Saru-LD02`, `D1-Culber-LD03`, `E1-Tilly-LD04`, `F1-Stamets-LD05`, `G1-Burnham-LD06`, `H1-Reno-LD07`, `I1-Georgiou-LD08`, `J1-Meta-Jerry`).
- **Interface 3D & Ascenseur (`ElevatorPanel.tsx`, `OfficeFloor.tsx`)** : Affiche les badges OS (`L0 Tech OS · 13 Holons`, `L1 Life OS 2026 · 43 Holons`, `L2 Business OS · 137 Holons`) et les panneaux muraux 3D de chaque étage.
