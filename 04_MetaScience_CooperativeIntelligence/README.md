# 04_MetaScience_CooperativeIntelligence — Pôle Méta-Science & Intelligence Coopérative

Bienvenue dans le pôle **04_MetaScience_CooperativeIntelligence** d'Aspace OS V5. Ce pôle rassemble, structure et formalise les fondations théoriques, empiriques et algorithmiques de l'intelligence collective, de la dynamique des foules, de l'auto-organisation sans chef, et de la méta-science des réseaux de recherche.

---

## 1. Architecture du Pôle

```
04_MetaScience_CooperativeIntelligence/
├── 01_Videos/
│   ├── registres/
│   │   ├── chaines_youtube.csv      # Registre structuré des chaînes auditées
│   │   ├── playlists.csv            # Registre des playlists thématiques
│   │   └── videos_index.csv         # Index détaillé des vidéos analysées
│   ├── chaines/
│   │   ├── fouloscopie/             # Analyses Fouloscopie (Mehdi Moussaïd)
│   │   │   ├── 150_ans_recherche_scientifique.md
│   │   │   ├── jeux_video_font_avancer_science.md
│   │   │   ├── banc_de_poissons_5_niveaux.md
│   │   │   └── synthese_intelligence_collective.md
│   │   └── brad_bonanno/            # Video-to-Skill & Compilateurs
│   ├── playlists/
│   └── videos/
├── 02_Livres/
│   └── registres/
│       └── livres_index.csv         # Registre des ouvrages fondateurs convertis en SOPs
├── 03_Articles/
│   └── registres/
│       └── articles_index.csv       # Index des papiers fondamentaux (Vicsek, Boids, Small-World)
└── README.md
```

---

## 2. Ontologie des Sources

1. **`01_Videos/`** : Ingestion et décomposition de vidéos scientifiques et techniques. Chaque vidéo est décomposée en ses principes mathématiques/organisationnels et traduite en règles exécutables pour Aspace OS V5.
2. **`02_Livres/`** : Ingestion d'ouvrages majeurs de stratégie, psychologie financière, marketing fondamental et ethologie, compilés en arbres de décision selon le pipeline Omni-Compiler.
3. **`03_Articles/`** : Études académiques pionnières en physique statistique des systèmes complexes, intelligence en essaim, théorie des graphes et science citoyenne.

---

## 3. Registres CSV Normalisés

Tous les registres tabulaires respectent la norme RFC 4180 avec encodage UTF-8 et identifiants uniques pérennes (`id_chaine`, `id_playlist`, `id_video`, `id_livre`, `id_article`).
Ces registres sont directement interrogeables par les scripts de l'Aspace Factory (`factory.ps1`), les agents de recherche (`bill-research`), et les outils d'ingestion multimodale (`omni-compiler`, `watch`).
