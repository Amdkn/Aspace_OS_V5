---
okf_version: "0.2"
type: Decision
title: "ADR-01 — Réveil Événementiel & Hibernation Pure-Data vs Sondage Cron Périodique"
enonce_ref: "00_Memoire/bundle/fusion/FUSION-ENONCE.md"
enonce_sha256: "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"
---

# ADR-01 — Réveil Événementiel & Hibernation Pure-Data vs Sondage Cron Périodique
- **Statut** : `ACCEPTÉE`
- **Conflit** : `automaton`, `openclaw`, `daily_stock_analysis`, `uptime-kuma`, `changedetection.io` utilisent historiquement des boucles `cron` / sondages périodiques (ex. toutes les 30 min), tandis qu'`infinity` et `pi` imposent l'état **Pure Data Between Turns** et les **checkpoints événementiels**.
- **Décision** : Tout cœur agentique (`K1`, `K2`) hiberne à coût CPU/RAM nul entre deux tours (état sérialisé en SQLite WAL dans `session_store.rs` / `factory.sqlite`) et se réveille uniquement sur événement typé (`RAP`, message, webhook, échéance de bail). Les outils de sondage externe `RETENU` (`uptime-kuma`, `changedetection.io`) sont cantonnés à la périphérie `K5` et émettent des webhooks d'événement vers `K2`, jamais de threads agents permanents.
- **Invariant** : Zéro `cron 30min` sur les 578 Holons ; temps de veille inactif = 0 thread actif.
- **Modules résolus** : `infinity`, `pi`, `automaton`, `openclaw`, `daily_stock_analysis`, `uptime-kuma`, `changedetection.io`.
