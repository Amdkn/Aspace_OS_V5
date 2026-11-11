# 02_Video — Studio Vidéo Agentique & Productized Services (10 Moteurs)

Ce dossier regroupe l'ensemble des moteurs vidéo souverains d'**A'Space OS V5**, unifiant le studio de création agentique (**FKB06**) et les services productisés à haute marge (**FKB07**) :

## Les 10 Moteurs Vidéo Souverains (`Amdkn/*`)

### 1. Offres B2B Productized Services & SaaS
- [**OpenMontage**](https://github.com/Amdkn/OpenMontage) — Pack de 4 vidéos publicitaires courtes e-commerce / mois (Setup 500 $, Retainer 1 000 $/mois).
- [**flute**](https://github.com/Amdkn/flute) — Studio SaaS Vidéo & Canvas UI/UX interactif (`webprodigies-org/flute`, Setup 1 500 $, Retainer 750 $/mois).

### 2. Studio Agentique & Pipeline de Production
- [**take-one**](https://github.com/Amdkn/take-one) — Générateur autonome de scripts et de plans cinématographiques pour films de lancement.
- [**huashu-motion**](https://github.com/Amdkn/huashu-motion) — Animation procédurale et motion design pour vidéos produit.
- [**rossark-motion-skill**](https://github.com/Amdkn/rossark-motion-skill) — Animation de mascottes et graphismes interactifs 2D/3D.
- [**reanimate**](https://github.com/Amdkn/reanimate) — Moteur de réanimation vectorielle et synchronisation d'assets visuels.
- [**argo**](https://github.com/Amdkn/argo) — Capture de session interactive et rendu de vidéos démo SaaS.
- [**explainroo**](https://github.com/Amdkn/explainroo) — Générateur automatique de vidéos explicatives et d'onboarding produit.
- [**video-director**](https://github.com/Amdkn/video-director) — Metteur en scène IA orchestrant le découpage technique et les angles de caméra.
- [**earshot**](https://github.com/Amdkn/earshot) — Synchronisation vocale, habillage sonore, musique et effets sonores (SFX).

## Pipeline de Synthèse Unifié
```
Idée / Script (take-one)
       │
       ▼
Mise en Scène & Découpage (video-director)
       │
       ├────────────────────────┬────────────────────────┐
       ▼                        ▼                        ▼
Animation (rossark/huashu)   Canvas SaaS (flute)   Captures Démo (argo/explainroo)
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                ▼
                   Habillage Sonore (earshot)
                                ▼
             Rendu Publicitaire E-commerce (OpenMontage)
```
