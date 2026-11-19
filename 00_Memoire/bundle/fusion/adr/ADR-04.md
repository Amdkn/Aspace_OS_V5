---
okf_version: "0.2"
type: Decision
title: "ADR-04 — Mémoire Épistémique Vérifiée au Fichier (`M1–M8`) vs RAG Sémantique Flou"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-04 — Mémoire Épistémique Vérifiée au Fichier (`M1–M8`) vs RAG Sémantique Flou
- **Statut** : `ACCEPTÉE`
- **Conflit** : `gbrain`, `DeepTutor`, `billion-context` utilisent la recherche vectorielle/hybride et l'indexation massive, tandis que `fondation-13-1` (`recall-fact`, règles M1–M8), `auto-ontology` (DAG formel), `knowledge-catalog` (OKF v0.2) et `servers` (`memory.jsonl`) exigent traçabilité exacte au fichier, absence d'inférence implicite et détection de contradictions.
- **Décision** : La recherche hybride (`gbrain`, `graphify`, `billion-context`) sert uniquement de **moteur de rappel candidat**. Aucun fait n'est promu ou cité comme vérité dans la Fondation (`K1`, `K4`) sans passer le contrat épistémique **`EpistemicFact` (`M1–M8`)** qui impose un statut explicite parmi `{vérifié, consigné, contredit, périmé, absent, à venir}` et l'interdiction absolue d'inférer une date ou un SHA absent. Les écritures durables passent par un fichier unique `00_Memoire/shared_brain/memory.jsonl` (verrou `O_EXCL`) + `00_Memoire/bundle/` (OKF v0.2, `log.md` strictement append-only).
- **Invariant** : Toute assertion dans une PR, un jugement ou un livrable B2B cite sa source et sa date vérifiées au fichier ou porte un statut d'absence/contradiction explicite.
- **Modules résolus** : `fondation-13-1`, `auto-ontology`, `context-language-models`, `dox`, `gbrain`, `graphify`, `infinite-brain-harness`, `infinite-brain-os`, `knowledge-catalog`, `servers`, `llm-wiki`, `claude-mem`, `DeepTutor`.
