---
title: "Orchestration Cloud Gratuite : Workspace Studio Triggers, Google Apps Script (GAS), Retool, Zenphi & Quota Accounting"
type: concept
status: active
updated: 2026-11-08
tags:
  - freecomputeapi
  - workspace-studio
  - apps-script
  - retool
  - zenphi
  - gkit
  - zapier
  - cloud-quotas
---

# Orchestration Cloud Gratuite : Workspace Studio, GAS, Retool & Comptabilité Prévisible

Avant l'avènement de l'orchestration par IA d'**A'Space OS V5**, coordonner des outils disparates représentait une charge d'ingénierie et de maintenance prohibitive.
L'intégration des déclencheurs événementiels de **Google Workspace Studio**, du compute serverless de **Google Apps Script (GAS)**, des workflows de **Retool**, de **Zenphi**, de **GKit** et des plateformes de connecteurs (**Make**, **Activepieces**, **Zapier**) permet de bâtir une infrastructure d'automatisation à **coût nul ($0.00)** avec une comptabilité prévisible des quotas.

---

## 1. Les Déclencheurs Natifs de Google Workspace Studio

L'interface de **Google Workspace Studio** (`studio.workspace.google.com`) met à disposition **13 déclencheurs événementiels natifs** qui absorbent les événements sans aucun coût d'infrastructure :

| Famille d'Événements | Déclencheur Workspace Studio | Rôle dans A'Space OS V5 |
|---|---|---|
| **E-mail & Communication** | *Lorsque je reçois un e-mail* (Gmail) | Ingestion des demandes entrantes B2B The OMK Office |
| **Google Chat** | *Lorsque je reçois un message de chat* | Commandes conversationnelles S0 $\rightarrow$ A0 Amadeus |
| **Mentions & Réactions** | *Lorsqu'une personne me mentionne* / *Réaction emoji ajoutée* | Approbation humaine rapide (Human-in-the-Loop) |
| **Google Sheets** | *Lorsqu'une feuille est modifiée* | Événements de mutation de données dans `Areas OS` (`LD01..LD08`) |
| **Google Drive** | *Lorsqu'un élément est ajouté / modifié dans un dossier* | Ingestion automatique vers le **Bucket Drive 5 To** (`.cas.json`) |
| **Calendrier & Réunions** | *D'après une réunion* / *Lorsque les notes de réunion sont prêtes* | Extraction des compte-rendus vers `Vision_Pike` & `Planning_Una` |
| **Google Forms** | *À réception d'une réponse à un formulaire* | Capture des leads et qualification automatique GTME |

---

## 2. Google Apps Script (GAS) : Le Compute Serverless Gratuit

Le script [`02_Factory/gas/Aspace_Gateway_GAS.js`](file:///c:/Users/amado/Aspace%20OS%20V5/02_Factory/gas/Aspace_Gateway_GAS.js) transforme **Google Apps Script** (`script.google.com`) en worker serverless connecté à GitHub Actions :
- **Quota CPU** : **90 minutes par jour** (soit **2 700 minutes/mois** de pur calcul CPU gratuit).
- **Temps d'exécution maximal** : **6 minutes par invocation** (suffisant pour agréger des données, formater des JSON ou router des webhooks).
- **Appels réseau (`UrlFetchApp`)** : **20 000 requêtes sortantes par jour**.
- **Webhooks Bidirectionnels** : `doPost()` reçoit les événements externes et déclenche l'API `repository_dispatch` de GitHub Actions (`gws_webhook_trigger`).

---

## 3. Retool Workflows, Zenphi & GKit : La Couche d'Automatisation d'Entreprise

1. **Retool Workflows (`retool.com`)** :
   - Offre gratuite : **5 000 exécutions de workflows par mois** + requêtes REST/GraphQL illimitées + 5 utilisateurs.
   - Utilisé pour les dashboards administratifs et les webhooks asynchrones.
2. **Zenphi (`zenphi.com`)** :
   - Alternative no-code native pour Google Workspace supprimant la limite de 6 minutes de GAS, avec traçabilité d'audit étape par étape.
3. **GKit (`gkit.mreshank.com`)** :
   - Beta **$0/mois** : API REST CRUD complète sur Google Sheets, conversions de formats (JSON, CSV, TSV) et scanner GDriveKit.

---

## 4. Matrice Consolidée de Comptabilité Prévisible des Quotas

| Fournisseur | Catégorie | Capacité Mensuelle Gratuite | Coût | Rôle dans l'Écosystème |
|---|---|---|---|---|
| **Google Apps Script (GAS)** | Serverless Compute | **2 700 min CPU/mois** (90 min/j) | **$0.00** | Passerelle webhooks & workers légers GWS |
| **Google Workspace Studio** | Événements Natifs | **13 Déclencheurs Illimités** | **$0.00** | Détection d'événements Gmail/Sheets/Drive/Chat |
| **Retool Workflows** | Enterprise Workflows | **5 000 runs/mois** | **$0.00** | Connecteur B2B & dashboards opérationnels |
| **Cloudflare Workers** | Edge Compute | **3 000 000 requêtes/mois** (100k/j) | **$0.00** | Routage DNS/Edge (`aspaceos.tech`) |
| **Trio Workflow Ops** | Connecteurs Cloud | **2 100 opérations/mois** (Activepieces + Make + Zapier) | **$0.00** | Intégrations CRM & outils tiers |
| **GitHub Actions** | Runners CI/CD | **Illimité Public + 2 000 min Privé** | **$0.00** | Moteur n8n primitif & exécution RigInfinity |
| **Google Cloud Shell** | Linux VM Persistante | **200 heures/mois** (50h/semaine) | **$0.00** | Environnement d'exécution `antigravity-a0` |
| **GitHub Codespaces** | Cloud Dev Containers | **120 core-hours/mois** | **$0.00** | Tâches de build lourdes avec auto-kill |
| **Google Drive 5 To** | Bucket Multimédia CAS | **4 987,99 Go disponibles** | Inclus | Stockage perpétuel des binaires lourds |
