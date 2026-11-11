# 02_Inference_Cooperative — Pile d'IA Souveraine Distribuée (Cluster & P2P Mesh)

> **Vision** : Fusionner le **Moteur (Compute)**, le **Réseau (Topologie)** et la **Surface (Client)** en une pile d'inférence coopérative où un cluster hétérogène (PC local, tablette, serveur distant/VPS) exécute des modèles lourds de manière distribuée et optimisée, via une interface unifiée accessible sur n'importe quel écran.

---

## 1. Les Trois Piliers Coopératifs

| Composant | Sous-Module Fork | Rôle dans l'Architecture | Valeur Ajoutée Aspace OS V5 |
|---|---|---|---|
| **Noyau d'Exécution (Engine)** | [`DeepInfer`](https://github.com/Amdkn/DeepInfer) | Inférence matérielle bas niveau, micro-kernels CUDA/C++, quantification dynamique (FP8, INT4), KV-cache (PagedAttention, MLA) et décodage spéculatif. | Maximise le débit (tokens/s) et minimise l'empreinte VRAM par nœud. |
| **Orchestration Distribuée (Mesh)** | [`mesh-llm`](https://github.com/Amdkn/mesh-llm) | Découpage des couches (*Pipeline Parallelism*), protocole P2P/mDNS, routage dynamique de charge et tolérance aux pannes. | Permet d'exécuter des modèles géants en agrégeant la mémoire de plusieurs machines sans NVLink. |
| **Surface Utilisateur (Client)** | [`cross-platform-llm-client`](https://github.com/Amdkn/cross-platform-llm-client) | Interface multi-plateforme (Desktop, Mobile, Web), sessions locales, streaming SSE, prompt templating et abstraction multi-endpoints. | Offre un accès omnicanal fluide sans dépendance vis-à-vis d'un cloud propriétaire. |

---

## 2. Topologie de l'Architecture Unifiée

```
┌────────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 · CLIENT OMNICANAL (Cross-Platform Interface)                 │
│ Framework : Tauri / Rust + React ou Flutter                            │
│  ├─ UI Desktop (Windows 11 / Linux), Mobile (Android / Tablette), Web │
│  ├─ Streaming de tokens temps réel (SSE / WebSockets)                  │
│  └─ Gestion de session locale & prompt engineering déterministe        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Requête d'inférence (JSON RPC / gRPC)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ COUCHE 2 · ORCHESTRATEUR EN MAILLAGE (Mesh-LLM Layer)                  │
│ Protocole : Libp2p / WebRTC / mDNS                                     │
│  ├─ Découverte automatique des nœuds locaux (PC hôte, VPS, tablette)   │
│  ├─ Partitionnement du modèle (Pipeline Parallelism : Nœud A = L0..L15, │
│  │  Nœud B = L16..L31)                                                 │
│  └─ Allocation de mémoire dynamique selon la RAM/VRAM disponible       │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌─────────────────────────────────────┐  ┌───────────────────────────────┐
│ COUCHE 3 · NŒUD COMPUTE A (DeepInfer)│  │ COUCHE 3 · NŒUD COMPUTE B (Worker)
│  ├─ Machine principale (ex. PC 30 Go)│  │  ├─ Machine secondaire (VPS/Edge) 
│  ├─ Kernels C++/CUDA optimisés FP8   │  │  ├─ Kernels CPU/Metal/ROCm         
│  ├─ Traitement des couches L0..L15   │  │  ├─ Traitement des couches L16..L31
│  └─ Envoi des activations intermédiaires vers le Nœud B via IPC/TCP    │
└─────────────────────────────────────┘  └───────────────────────────────┘
```

---

## 3. Spécification Technique de la Fusion

### A. Le Moteur (`DeepInfer-Core`)
- **Stratégie mémoire** : Allocateurs de mémoire unifiés et quantification dynamique (FP8 / Q4_K_M) pour contenir les couches dans la RAM/VRAM assignée.
- **Décodage spéculatif local** : Le nœud le plus léger génère des propositions de tokens (*draft model* 1B/2B), validées en une seule passe parallèle par le grand modèle distribué sur le maillage.

### B. La Découverte et le Partitionnement (`Mesh-Router`)
- **Pipeline Parallelism (PP) plutôt que Tensor Parallelism (TP)** :
  - Le *Tensor Parallelism* requiert une bande passante inter-GPU massive (NVLink à plusieurs centaines de Go/s), incompatible avec un réseau local classique.
  - Le *Pipeline Parallelism* découpe le modèle par blocs de couches entières. Entre deux nœuds, seules les activations séquentielles d'une couche charnière transitent par le réseau local (quelques Mo par batch), rendant l'inférence collaborative fluide même sur Ethernet 1 Gbps ou Wi-Fi 6.
- **Auto-équilibrage** : Détection des nœuds via mDNS ; si un nœud quitte le maillage, le coordinateur recompose le graphe d'inférence sur les machines restantes.

### C. L'Interface Client (`Omni-Client`)
- Le client s'adresse à l'adresse de passerelle virtuelle exposée par le coordinateur Mesh (`http://localhost:8080/v1/chat/completions`, standard OpenAI).
- Stockage local chiffré des historiques et configuration dynamique sans altérer le backend.

---

## 4. Stack d'Implémentation Industrielle

1. **Noyau & Mesh (Backend)** : **Rust**
   - *Réseau* : `libp2p` pour la couche décentralisée / découverte des pairs (`mesh-llm`).
   - *Bindings Inférence* : Moteurs C++ / CUDA intégrés via FFI (`DeepInfer` / `llama.cpp` / `vLLM`).
   - *Transport inter-couches* : gRPC avec buffers partagés pour minimiser la latence de sérialisation.
2. **Client Multi-plateforme (Frontend)** : **Tauri 2.0 (Rust + Web)**
   - Coordinateur local embarqué directement dans le binaire sur Windows, Linux, macOS et Android.
3. **Conteneurisation Headless** : Manifest Docker Compose / Coolify pour déployer un nœud compute sur VPS prêt à rejoindre le maillage.
