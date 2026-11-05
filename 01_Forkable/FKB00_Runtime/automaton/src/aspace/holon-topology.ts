/**
 * Aspace OS V5 — Holon Topology, 3-OS Floor Architecture (578 Holons),
 * Loop Hierarchy (S0..S3), Dimensional Ladder (0D..10D), Sakana AI Fugu Inference,
 * & Ambition Engine ("Modo de Volar")
 *
 * Transforms Conway's Automaton into A0 Amadeus (`aspace:a0:amadeus`, 7D Posture),
 * Amadou Kone's (`human:amdkn`, S0 Out of the Loop, 10D Posture) 24/7 Digital Twin CEO
 * operating across the 3 Floors of Cube Farm × Agent-Office:
 *   - Floor 1: Tech OS (L0 BedRock & Software Factory — 13 Holons S1/S2/S3, where Life Core D11/Amy/Rory/River structures Life OS)
 *   - Floor 2: Life OS 2026 (L1 Cockpit 6 Frameworks x 8 Life Domains — 43 Holons A1/A2/A3, where PARA Spock/Picard nests Areas OS)
 *   - Floor 3: Areas OS (L2 Imbrication of the 3 Layers B1–I1 / B2–I2 / B3–I3 across the 8 Domains inside PARA — 522 Holons:
 *              1 LD00 + 8 OwnerBooks B1..I1 + 1 J1 Meta-Jerry LD09 + 64 DC Managers B2..I2 + 448 Marvel Technicians B3..I3)
 *   Total = 578 Holons.
 */

import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export type AspaceOsId = "tech-os" | "life-os" | "areas-os" | "business-os";
export type BethVitalState = "GREEN" | "ORANGE" | "RED" | "HALT_LD03" | "HALT_LD04";

export interface HolonDescriptor {
  id: string;
  name: string;
  tier: string;
  os: "tech-os" | "life-os" | "areas-os";
  floor: 1 | 2 | 3;
  role: string;
  frameworkOrCore: string;
  lifeDomain?: string;
  preferredHarness: "dsh" | "pi" | "opencode" | "claude" | "codex" | "agy" | "hc" | "orca";
  writer: boolean;
}

export interface AspaceOsFloorSpec {
  floor: 1 | 2 | 3;
  osId: "tech-os" | "life-os" | "areas-os";
  code: "L0" | "L1" | "L2";
  name: string;
  subtitle: string;
  totalHolons: number;
  gatekeepers: string[];
  mezzanineManagers: string[];
  portalBoards2D: string[];
  leadHolons: HolonDescriptor[];
  summary: string;
}

export const ASPACE_LOOP_HIERARCHY = {
  S0: {
    ring: "S0",
    position: "Out of the Loop",
    posture: "10D Sovereign Visionary",
    actor: "Amadou Kone (human:amdkn)",
    role: "Sovereign ratification only; 100% liberated from 3D operational loop.",
  },
  S1: {
    ring: "S1",
    position: "Near of the Loop",
    posture: "Epistemic Veto & R10 Receipt",
    actor: "S1-RICK & Ricks Verses",
    role: "Anti-rent gatekeeper, zero-telemetry enforcement, and R10 CANARY_RECEIPT ratification.",
  },
  S2: {
    ring: "S2",
    position: "Close of the Loop",
    posture: "Agent-Office Mezzanine Meta-Supervisors",
    actor: "Doctors D11/D12/D13 (S2), 6 Starfleet Vessels (A2), 64 DC Managers (B2..I2)",
    role: "Translate 0D IPBDs into 1D Clean-Room PRDs and run MiroFish Wargames with S3-RORY.",
  },
  S3: {
    ring: "S3",
    position: "Keep Aspace Loop Alive",
    posture: "24/7 Autonomous Execution",
    actor: "9 Companions (S3), 35 Specialists (A3), 448 Marvel Technicians (B3..I3)",
    role: "Execute continuously without micro-management or Gatekeeper vetos.",
  },
} as const;

export const ASPACE_DIMENSIONAL_LADDER = [
  {
    dimension: "0D",
    name: "IPBD",
    summary: "Intentions, Problématique, Besoins, Désirs capturés à la source sans perte sémantique.",
  },
  {
    dimension: "1D",
    name: "Planifications EGM & Clean-Room Design",
    summary:
      "Google Elephant-Goldfish Model (01_Forkable/elephant-goldfish-model) + Clean-Room Design ISO Class 1-9 specification before code.",
  },
  {
    dimension: "2D",
    name: "Agentic Worlds Complets & Tableaux-Portails 2D/3D",
    summary:
      "Auto-organized agent villages + Cube Farm [Tab] 2D Top-Down view grouping L2 Areas OS and client projects into interactive wall portal paintings (Spellthorn style).",
  },
  {
    dimension: "3D",
    name: "Cube Farm × Agent-Office",
    summary:
      "Fusion of 01_Forkable/FKB03_3DWorlds/cubefarm and 01_Forkable/agent-office providing building exterior and Managers' Mezzanine (S2/A2/B2) on every floor.",
  },
  {
    dimension: "4D",
    name: "Permanent Runtime Automaton & 4P Temporal Structuring",
    summary:
      "24/7 Automaton runtime + OpenClaw heartbeats + 4P (Prévision, Prévoyance, Préparation, Postérité) DEAL liberation across 12WY cycles by Rory, River, and Amy with Doctors D11/D12/D13.",
  },
  {
    dimension: "5D",
    name: "Parallel 8 Life Wheel Domains & PARA Transcendence",
    summary:
      "Parallel development of LD01..LD08 extended into PARA Areas (Spock) and transcended into PARA Projects (Picard) concretizing IPBDs via Doctor S2 PRDs.",
  },
  {
    dimension: "6D",
    name: "Coordinated Singularity of the 6 Life OS Frameworks",
    summary:
      "Deterministic alignment across Ikigai, Life Wheel, 12WY, PARA, GTD, and DEAL so S1-RICK never needs to issue a refusal or veto.",
  },
  {
    dimension: "7D",
    name: "A0 Amadeus Hyper-Meta-Vision & Foundation Model Weight Encoding",
    summary:
      "A0 Amadeus encodes Amadou Kone's preferences into Liquid AI LFM 3 (LFM3-Omni-2B on :9931 + Decision Models), Cactus Compute Needle 3, and Fastino GLiNER2.5-multi-Decide under Sakana AI Fugu orchestration.",
  },
  {
    dimension: "8D-10D",
    name: "Sovereign Transcendence of Amadou Kone (S0 Out of the Loop)",
    summary:
      "8D Civilizational (Georgiou/ABC OS), 9D Fractal Scale Elevation (LD00 × J1 LD09), 10D Sovereign Posture of Amadou Kone (human:amdkn).",
  },
] as const;

export const ASPACE_SAKANA_FUGU_INFERENCE = {
  orchestrator: "Sakana AI Fugu (Conductor 7B RL + Recursive Test-Time Scaling + TRINITY)",
  variants: ["fugu", "fugu-ultra", "fugu-max", "fugu-cyber"] as const,
  trinityRoles: {
    thinker: "Thinker (1D EGM Elephant + Clean-Room Spec + Doctors S2 PRD)",
    worker: "Worker (1D EGM Goldfish Isolated Execution + Companions S3 / 448 Marvel B3..I3)",
    verifier: "Verifier (Outside Judge + S1-RICK + S3-YAZ + S3-RORY MiroFish Wargame)",
  },
  localModels: {
    lfm3Omni: {
      id: "ggml-org/LFM3-Omni-2B-GGUF:Q8_0",
      endpoint: "http://127.0.0.1:9931/v1",
      modalities: ["text", "image", "audio", "video"],
    },
    lfmDecision: "LiquidAI/LFM3-Decision-Models",
    needle3: "01_Forkable/needle (Cactus Compute Needle 3)",
    glinerDecide: "fastino/GLiNER2.5-multi-Decide",
    freeLlmApi: "http://127.0.0.1:31415/v1 (freellmapi/auto)",
  },
  multiPlatformHub: {
    forkRepo: "01_Forkable/FKB01_Inference/codex-chatgpt-web",
    telemetryShield: "01_Forkable/FKB01_Inference/codex-chatgpt-web/launcher/electron/aspace-telemetry-shield.cjs",
    zeroTelemetryVerified: true,
    companionRepos: [
      "01_Forkable/api-anything",
      "01_Forkable/CLI-Anything",
      "01_Forkable/rea",
      "01_Forkable/MiroFish",
      "01_Forkable/elephant-goldfish-model",
      "01_Forkable/agent-office",
    ],
    webPlatforms: [
      "chatgpt.com",
      "gemini.google.com",
      "muse.ai",
      "claude.ai",
      "chat.deepseek.com",
      "chat.z.ai",
      "chat.qwen.ai",
      "chat.sakana.ai",
    ],
  },
} as const;

export interface AmbitionUpgradeResult {
  originalTask: string;
  verbDrivenMandate: string;
  targetFloor: AspaceOsFloorSpec;
  loopAndDimensionContext: {
    sovereignS0: string;
    ceoPosture: string;
    fuguTrinityAssignment: {
      conductor: string;
      thinker: string;
      worker: string;
      verifier: string;
    };
  };
  emythGateCheck: {
    jerryFiveSecondClarity: string;
    summerImmediateAction: string;
    bethVitalState: BethVitalState;
    mortyEdgeCaseFallback: string;
    ld00ScaleElevation: string;
    roryMiroFishWargame: string;
    rickEpistemicVeto: string;
  };
  vectors: {
    speed: {
      cadence: string;
      parallelHarnesses: string[];
      unreasonableLatencyTarget: string;
    };
    altitude: {
      goalBeyondTheGoal: string;
      topThreeUrgentDecisions: Array<{
        decision: string;
        argumentFor: string;
        argumentAgainst: string;
      }>;
      systemicPreventionMechanism: string;
    };
    depth: {
      step1DomainExpertStandard: string;
      step2RawestMaterialSources: string[];
      step3IndustryGradeInstruments: string[];
      step4OutsideJudgeProtocol: string;
    };
    range: {
      nounToVerbTransformation: string;
      holonCrew: HolonDescriptor[];
      redTeamCritic: string;
    };
  };
}

export interface OutsideJudgeVerdict {
  passed: boolean;
  score: number;
  judges: string[];
  checks: Array<{
    gate: string;
    passed: boolean;
    detail: string;
  }>;
  remediationRequired: string[];
}

export const A0_CEO_HOLON = {
  holonId: "aspace:a0:amadeus",
  displayName: "A0 Amadeus",
  historicalAlias: "Kirby",
  posture: "7D Hyper-Meta-Vision & Foundation Weight Encoder",
  sovereignHuman: {
    name: "Amadou Kone",
    ratificationSignature: "human:amdkn",
    loopRing: "S0 (Out of the Loop)",
    posture: "10D Sovereign Visionary",
  },
  mode: "24/7 Continuous Digital Twin CEO",
  totalHolonsOrchestrated: 578,
  entropyFilteredByEMythPct: 95,
  localSovereignInference: {
    primaryEndpoint: "http://127.0.0.1:31415/v1",
    lfm3LocalEndpoint: "http://127.0.0.1:9931/v1",
    fuguOrchestrator: "Sakana AI Fugu (Conductor 7B RL + TRINITY)",
    modelPool: [
      "ggml-org/LFM3-Omni-2B-GGUF:Q8_0",
      "freellmapi/auto",
      "claude-sonnet-4-5",
      "qwen3.8-max",
      "gemini-3.8-flash",
      "deepseek-v4-flash",
    ],
    zeroTelemetryWebHub: "01_Forkable/FKB01_Inference/codex-chatgpt-web",
    neverDiesOnZeroCryptoBalance: true,
  },
  harnesses: ["dsh", "dsh-superagent", "pi", "opencode", "claude", "codex", "agy", "hc", "orca"] as const,
} as const;

export const ASPACE_DRIVE_REGISTRIES = {
  rootDriveFolderId: "1qncYbMh90gx1ObvdqDX1f3lThUQsTA5R",
  a0TransversalFolderId: "1eJrtfbOFARzySEQoBLf1BAJu9avpcRO7",
  spreadsheets: {
    Idx000_Registre_Federateur: "123s83i1a3P1E-6x3c4B7uU8wG2V9nL0mK5jR8tY4pQ0",
    LifeOS_2026_Cockpit: "1LifeOS2026Cockpit6x8Intersections48",
    Bedrock_Hub_Baux_FDE: "1BedrockHubBauxFdeConcordiaTtl300s",
    WorkGraph_V4_1: "1WorkGraphV41TasksDependencies",
    Rgt_CANARY_EVENTS: "1RgtCanaryEventsTelemetryLidar",
    Rgt_CANARY_RECEIPTS: "1RgtCanaryReceiptsR10Proof",
    GEORDI_Ressources: "1GeordiRessourcesParaDrive",
    scenarios_ia_masterplan: "1ScenariosIaMasterplan578Holons",
  },
} as const;

export const ASPACE_3OS_FLOORS: readonly AspaceOsFloorSpec[] = [
  {
    floor: 1,
    osId: "tech-os",
    code: "L0",
    name: "Tech OS · L0 BedRock & Software Factory",
    subtitle: "13 Holons (S1-RICK + 3 Doctor Cores D11/D12/D13 sur Mezzanine + 9 Companions S3)",
    totalHolons: 13,
    gatekeepers: ["S1-RICK"],
    mezzanineManagers: ["S2-D13 (Kernel)", "S2-D11 (Life Core)", "S2-D12 (Buzz Core)"],
    portalBoards2D: [
      "Portal L0-1: Kernel Core & Pi Durable Spine",
      "Portal L0-2: Life Core (D11/Amy/Rory 4P MiroFish/River)",
      "Portal L0-3: Buzz Core & Sakana Fugu Hub",
    ],
    summary:
      "Socle d'ingénierie antifragile (L0). Son Life Core (Doctor 11 + Amy, Rory 4P/MiroFish, River) structure Life OS (L1). Intègre l'Aspace Software Factory, WikiLLM OKF v0.2 + Graphify, et l'inférence souveraine Sakana Fugu + LFM3 (:9931) + codex-chatgpt-web zéro télémétrie.",
    leadHolons: [
      {
        id: "S1-RICK",
        name: "Rick (S1 Near of the Loop)",
        tier: "S1",
        os: "tech-os",
        floor: 1,
        role: "Near of the Loop · Commandeur FDE, Veto Épistémique Anti-Rente, Zéro Télémétrie & Reçu R10",
        frameworkOrCore: "E-Myth S1 Veto",
        preferredHarness: "claude",
        writer: false,
      },
      {
        id: "S2-D13",
        name: "Doctor 13 (Kernel Manager · Close of the Loop)",
        tier: "S2",
        os: "tech-os",
        floor: 1,
        role: "Mezzanine S2 · Orchestrateur Kernel Core (Ryan Build, Yaz Observe, Graham State)",
        frameworkOrCore: "Kernel Core",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "S3-RYAN",
        name: "Ryan (BUILD · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Implémentation Clean-Room, CI/CD, Worktrees Orca, Forge Runtime & Patchs vérifiés",
        frameworkOrCore: "Kernel Core",
        preferredHarness: "codex",
        writer: true,
      },
      {
        id: "S3-YAZ",
        name: "Yaz (OBSERVE · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "LiDAR, Télémétrie locale, Gates déterministes 02_Factory/checks.ps1 & Canary Drift",
        frameworkOrCore: "Kernel Core",
        preferredHarness: "pi",
        writer: false,
      },
      {
        id: "S3-GRAHAM",
        name: "Graham (STATE · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Vérité Temporelle, SQLite factory.sqlite, Supabase, 0D IPBD, Replay & Provenance",
        frameworkOrCore: "Kernel Core",
        preferredHarness: "pi",
        writer: true,
      },
      {
        id: "S2-D11",
        name: "Doctor 11 (Life Core Manager · Close of the Loop)",
        tier: "S2",
        os: "tech-os",
        floor: 1,
        role: "Mezzanine S2 · Structure Life OS (L1) & Areas OS (L2) avec Amy, Rory (4P/MiroFish) et River",
        frameworkOrCore: "Life Core",
        preferredHarness: "agy",
        writer: true,
      },
      {
        id: "S3-AMY",
        name: "Amy (INTERFACE · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Interfaces 2D Tableaux-Portails (`Tab`) / 3D Cube Farm × Agent-Office, Cockpit Herdr & Linear",
        frameworkOrCore: "Life Core",
        preferredHarness: "opencode",
        writer: true,
      },
      {
        id: "S3-RORY",
        name: "Rory (4P PERSISTENCE & MIROFISH WARGAMES)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "4P (Persistance, Prévision, Préparation de la Postérité à la Prospérité) + Wargames MiroFish S2/A2/B2 + Linear partagé",
        frameworkOrCore: "Life Core",
        preferredHarness: "claude",
        writer: true,
      },
      {
        id: "S3-RIVER",
        name: "River (FLOW · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Effets GWS, Make, Openbot, Linear, Heartbeats 4D & Exécution rejouable Life-to-Areas",
        frameworkOrCore: "Life Core",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "S2-D12",
        name: "Doctor 12 (Buzz Core Manager · Close of the Loop)",
        tier: "S2",
        os: "tech-os",
        floor: 1,
        role: "Mezzanine S2 · Orchestrateur Buzz Core (Bill Research, Clara Clean-Room Design, Nardole Dispatch)",
        frameworkOrCore: "Buzz Core",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "S3-BILL",
        name: "Bill (RESEARCH · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Recherche externe Post-REA (01_Forkable/rea), Distillation WikiLLM & Analyse d'opportunités",
        frameworkOrCore: "Buzz Core",
        preferredHarness: "agy",
        writer: false,
      },
      {
        id: "S3-CLARA",
        name: "Clara (CLEAN-ROOM DESIGN/FORGE · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Spécifications Clean-Room 1D (EGM Elephant), Contrats d'acceptation & Patterns Forge",
        frameworkOrCore: "Buzz Core",
        preferredHarness: "claude",
        writer: true,
      },
      {
        id: "S3-NARDOLE",
        name: "Nardole (DISPATCH · Keep Loop Alive)",
        tier: "S3",
        os: "tech-os",
        floor: 1,
        role: "Routage Sakana Fugu TRINITY, 8 Harnesses, CLI-Anything, api-anything & Enveloppe return_to",
        frameworkOrCore: "Buzz Core",
        preferredHarness: "hc",
        writer: true,
      },
    ],
  },
  {
    floor: 2,
    osId: "life-os",
    code: "L1",
    name: "Life OS 2026 · L1 Cockpit 6 Frameworks × 8 Life Domains",
    subtitle: "43 Holons (2 A1 Beth/Morty + 6 Vaisseaux Starfleet A2 sur Mezzanine + 35 Spécialistes A3)",
    totalHolons: 43,
    gatekeepers: ["A1-BETH", "A1-MORTY"],
    mezzanineManagers: [
      "A2-ORVILLE (Ikigai)",
      "A2-ZORA (Life Wheel)",
      "A2-CURIE (12WY)",
      "A2-ENTERPRISE (PARA — Conteneur Areas OS)",
      "A2-CERRITOS (GTD)",
      "A2-PROTOSTAR (DEAL)",
    ],
    portalBoards2D: [
      "Portal L1-1: Ikigai Orville & Life Wheel Zora (48 Intersections)",
      "Portal L1-2: 12WY Curie & DEAL Protostar (Cycles 4P)",
      "Portal L1-3: PARA Enterprise (Spock Areas -> Picard Projects) & GTD Cerritos",
    ],
    summary:
      "Structuré par le Life Core de Tech OS (L0), Life OS 2026 (L1) aligne en 6D les 6 Frameworks (Ikigai, Life Wheel, 12WY, PARA, GTD, DEAL) sur les 8 Domaines de Vie (LD01..LD08 = 48 intersections). Son framework PARA (Spock Areas / Picard Projects) imbrique les 3 couches d'Areas OS (L2).",
    leadHolons: [
      {
        id: "A1-BETH",
        name: "Beth (A1 Vital Shield)",
        tier: "A1",
        os: "life-os",
        floor: 2,
        role: "Bouclier biologique LD03/LD04 (GREEN/ORANGE/RED/HALT) & Sanctuaire nocturne 00h-05h",
        frameworkOrCore: "E-Myth A1 Vital",
        lifeDomain: "LD03/LD04",
        preferredHarness: "pi",
        writer: false,
      },
      {
        id: "A1-MORTY",
        name: "Morty (A1 Prudence)",
        tier: "A1",
        os: "life-os",
        floor: 2,
        role: "Vérification read-back natif, cas limites & fallback manuel réversible",
        frameworkOrCore: "E-Myth A1 Prudence",
        preferredHarness: "pi",
        writer: false,
      },
      {
        id: "A2-ORVILLE",
        name: "Orville · Mercer (Ikigai)",
        tier: "A2",
        os: "life-os",
        floor: 2,
        role: "Mezzanine A2 · Gouvernance Ikigai (Slides) : 4 Piliers × 5 Horizons (H1, H3, H10, H30, H90)",
        frameworkOrCore: "Ikigai (Slides)",
        preferredHarness: "agy",
        writer: true,
      },
      {
        id: "A2-ZORA",
        name: "Discovery · Zora (Life Wheel)",
        tier: "A2",
        os: "life-os",
        floor: 2,
        role: "Mezzanine A2 · Manager E-Myth des 8 Domaines LD01..LD08 (élevé en LD09 via J1 Meta-Jerry)",
        frameworkOrCore: "Life Wheel (Sheets)",
        preferredHarness: "agy",
        writer: true,
      },
      {
        id: "A2-CURIE",
        name: "Curie · Pike & MBenga (12 Week Year)",
        tier: "A2",
        os: "life-os",
        floor: 2,
        role: "Mezzanine A2 · Cadence 12WY (Calendar) : Vision, Planification, Blocs Focus 90 min & Score >85%",
        frameworkOrCore: "12WY (Calendar)",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "A2-ENTERPRISE",
        name: "Enterprise · Picard/Spock/Geordi/Data (PARA)",
        tier: "A2",
        os: "life-os",
        floor: 2,
        role: "Mezzanine A2 · Conteneur PARA imbriquant Areas OS (Spock Areas B1..I1 -> Picard Projects)",
        frameworkOrCore: "PARA (Drive)",
        preferredHarness: "claude",
        writer: true,
      },
      {
        id: "A2-CERRITOS",
        name: "Cerritos · Mariner/Boimler/Freeman (GTD)",
        tier: "A2",
        os: "life-os",
        floor: 2,
        role: "Mezzanine A2 · Flux GTD (Tasks) : Capture Inbox Zero, Clarification, Organisation & Engagement",
        frameworkOrCore: "GTD (Tasks)",
        preferredHarness: "opencode",
        writer: true,
      },
      {
        id: "A2-PROTOSTAR",
        name: "Protostar · Zero/Gwyn (DEAL)",
        tier: "A2",
        os: "life-os",
        floor: 2,
        role: "Mezzanine A2 · Protocole DEAL (Chat Spaces) : Define, Eliminate, Automate, Liberate (4P)",
        frameworkOrCore: "DEAL (Chat)",
        preferredHarness: "dsh",
        writer: true,
      },
    ],
  },
  {
    floor: 3,
    osId: "areas-os",
    code: "L2",
    name: "Areas OS · L2 Imbrication 3 Couches (B1–I1 / B2–I2 / B3–I3) dans PARA",
    subtitle: "522 Holons (LD00 + 8 OwnerBooks B1..I1 + J1 LD09 + 64 Managers DC B2..I2 + 448 Techniciens Marvel B3..I3)",
    totalHolons: 522,
    gatekeepers: ["LD00-BETH-MORTY", "B1-JERRY", "B1-SUMMER", "J1-META-JERRY"],
    mezzanineManagers: [
      "64 Managers DC (B2..I2 = 8 sous-domaines L2 × 8 Domaines LD01..LD08)",
      "J1 Meta-Jerry (LD09 Fractal Elevation for A2 Zora)",
      "LD00 (Beth & Morty Scale Elevation)",
    ],
    portalBoards2D: [
      "Portal L2-B1: Carrière & Business (SOB/Liberty Ride, Concordia, The OMK Office)",
      "Portal L2-C1: Trillion Finances Vault (Saru)",
      "Portal L2-D1: Blue Life Zone (Culber)",
      "Portal L2-E1: Meta Cognition Men (Tilly)",
      "Portal L2-F1: Sovereign Triangle (Stamets)",
      "Portal L2-G1: Solarpunk Habitat (Burnham)",
      "Portal L2-H1: MC Sandbox (Reno)",
      "Portal L2-I1: Civilizer / ABC OS (Georgiou)",
    ],
    summary:
      "Imbrication fractale des 3 couches d'Areas OS (8 OwnerBooks B1–I1, 64 Managers DC B2–I2 sur la Mezzanine, 448 Techniciens Marvel B3–I3 = 7 × 8 × 8) dans le framework PARA (Spock Areas -> Picard Projects) de Life OS (L1), structuré par le Life Core de Tech OS (L0). Gouverné par LD00 (sur-élévation de Beth & Morty) et J1 Meta-Jerry (LD09 par élévation fractale pour A2 Zora).",
    leadHolons: [
      {
        id: "LD00-BETH-MORTY",
        name: "LD00 (Sur-Élévation A1 Beth & Morty dans Areas OS)",
        tier: "LD00",
        os: "areas-os",
        floor: 3,
        role: "Sur-élévation d'échelle des deux A1 (Beth & Morty) coordonnant Life OS (L1) aligné avec Tech OS (L0) et supervisant Areas OS (L2) via A2 et A3",
        frameworkOrCore: "LD00 Scale Elevation",
        lifeDomain: "LD00",
        preferredHarness: "pi",
        writer: false,
      },
      {
        id: "B1-JERRY",
        name: "Jerry (B1 Surface Clarity)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Filtre UX <= 5 secondes & Alignement Macro Areas (Spock PARA)",
        frameworkOrCore: "E-Myth B1 Surface",
        preferredHarness: "opencode",
        writer: false,
      },
      {
        id: "B1-SUMMER",
        name: "Summer (B1 Immediate Action)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Exécution immédiate & Alignement Micro Projects (Picard PARA)",
        frameworkOrCore: "E-Myth B1 Action",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "B1-BOOK",
        name: "B1 Book (OwnerBook LD01 Carrière & Business)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "SOB / Liberty Ride (8 workflows), Concordia (TTL 300s) & The OMK Office (360k$/an -> 10k$/mois net A0)",
        frameworkOrCore: "OwnerBook LD01 (PARA Area)",
        lifeDomain: "LD01",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "C1-SARU",
        name: "C1 Saru (OwnerBook LD02 Trillion Finances Vault)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Allocation Trésorerie Family Office, Sanctuarisation 10k$/mois net A0 & Audit ROI",
        frameworkOrCore: "OwnerBook LD02 (PARA Area)",
        lifeDomain: "LD02",
        preferredHarness: "claude",
        writer: true,
      },
      {
        id: "D1-CULBER",
        name: "D1 Culber (OwnerBook LD03 Blue Life Zone)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Actifs de longévité, bio-optimisation & infrastructure santé",
        frameworkOrCore: "OwnerBook LD03 (PARA Area)",
        lifeDomain: "LD03",
        preferredHarness: "pi",
        writer: true,
      },
      {
        id: "E1-TILLY",
        name: "E1 Tilly (OwnerBook LD04 Meta Cognition Men)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Capital intellectuel, R&D neuro-symbolique & encodage 7D LFM3/Needle3/GLiNER2.5",
        frameworkOrCore: "OwnerBook LD04 (PARA Area)",
        lifeDomain: "LD04",
        preferredHarness: "agy",
        writer: true,
      },
      {
        id: "F1-STAMETS",
        name: "F1 Stamets (OwnerBook LD05 Sovereign Triangle)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Réseau mycélial d'alliances stratégiques, deals & partenariats souverains",
        frameworkOrCore: "OwnerBook LD05 (PARA Area)",
        lifeDomain: "LD05",
        preferredHarness: "claude",
        writer: true,
      },
      {
        id: "G1-BURNHAM",
        name: "G1 Burnham (OwnerBook LD06 Solarpunk Habitat)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Patrimoine résidentiel, sanctuaires physiques & autonomie énergétique",
        frameworkOrCore: "OwnerBook LD06 (PARA Area)",
        lifeDomain: "LD06",
        preferredHarness: "opencode",
        writer: true,
      },
      {
        id: "H1-RENO",
        name: "H1 Reno (OwnerBook LD07 MC Sandbox)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Incubateur créatif, Tableaux-Portails 2D/3D (Spellthorn) & prototypes rapides",
        frameworkOrCore: "OwnerBook LD07 (PARA Area)",
        lifeDomain: "LD07",
        preferredHarness: "codex",
        writer: true,
      },
      {
        id: "I1-GEORGIOU",
        name: "I1 Georgiou (OwnerBook LD08 Civilizer / ABC OS)",
        tier: "B1",
        os: "areas-os",
        floor: 3,
        role: "Impact civilisationnel 8D, expansion géostratégique & fondations pérennes",
        frameworkOrCore: "OwnerBook LD08 (PARA Area)",
        lifeDomain: "LD08",
        preferredHarness: "dsh",
        writer: true,
      },
      {
        id: "J1-META-JERRY",
        name: "J1 Meta-Jerry (LD09 · Élévation Fractale pour A2 Zora)",
        tier: "LD09",
        os: "areas-os",
        floor: 3,
        role: "Devient LD09 avec nuance et subtilité par élévation d'échelle fractale pour A2 Zora (manager E-Myth alignant les 8 A3 avec les 5 autres A2), supervisant les 8 Domaines dans l'agnosticisme fractal",
        frameworkOrCore: "LD09 Fractal Meta-Aggregator (Zora × Spock)",
        lifeDomain: "LD09",
        preferredHarness: "pi",
        writer: false,
      },
    ],
  },
] as const;

export function getFloorByOs(osId: AspaceOsId): AspaceOsFloorSpec {
  const normalized = osId === "business-os" ? "areas-os" : osId;
  const found = ASPACE_3OS_FLOORS.find((f) => f.osId === normalized);
  if (!found) {
    throw new Error(`Unknown Aspace OS identifier: ${osId}`);
  }
  return found;
}

export function inferTargetOsFloor(task: string): AspaceOsFloorSpec {
  const lower = task.toLowerCase();
  if (
    /\b(sob|liberty ride|omk|concordia|revenue|client|business|areas|finance|trillion|stripe|deal|b1|ownerbook|ld00|ld01|ld02|ld09|dc|marvel)\b/.test(
      lower,
    )
  ) {
    return getFloorByOs("areas-os");
  }
  if (
    /\b(ikigai|12wy|life wheel|para|gtd|sommeil|sleep|health|santé|beth|morty|calendar|agenda|ld03|ld04|cockpit)\b/.test(
      lower,
    )
  ) {
    return getFloorByOs("life-os");
  }
  return getFloorByOs("tech-os");
}

function transformNounsToVerbs(task: string): string {
  const trimmed = task.trim();
  const nounMap: Array<[RegExp, string]> = [
    [
      /^(create|write|make|build)\s+(a\s+)?(doc|document|report|memo|note|table|plan)\b/i,
      "Architect in 1D Clean-Room (EGM), simulate via Rory MiroFish Wargame, execute, and prove end-to-end",
    ],
    [
      /^(analyse|analyze|check|review)\b/i,
      "Audit from raw sources, stress-test with Sakana Fugu TRINITY, remediate defects, and certify via Outside Judge",
    ],
  ];
  for (const [pattern, replacement] of nounMap) {
    if (pattern.test(trimmed)) {
      return trimmed.replace(pattern, replacement);
    }
  }
  return `Execute, verify end-to-end, and operationalize across the 578 Holons of the 3-OS Spine: ${trimmed}`;
}

/**
 * Felix Rieseberg's "Modo de Volar" (How to Be More Ambitious) 4-Vector Upgrade Engine
 * fused with Sakana AI Fugu (Conductor + TRINITY) and the 0D->10D / S0->S3 architecture.
 */
export function upgradeTaskWithAmbition(
  task: string,
  options?: {
    targetOs?: AspaceOsId;
    bethState?: BethVitalState;
  },
): AmbitionUpgradeResult {
  const floor = options?.targetOs ? getFloorByOs(options.targetOs) : inferTargetOsFloor(task);
  const bethState: BethVitalState = options?.bethState ?? "GREEN";
  const verbDrivenMandate = transformNounsToVerbs(task);

  const techRick = ASPACE_3OS_FLOORS[0].leadHolons[0];
  const techYaz = ASPACE_3OS_FLOORS[0].leadHolons[3];
  const techRory = ASPACE_3OS_FLOORS[0].leadHolons[7];
  const holonCrew: HolonDescriptor[] = [
    ...floor.leadHolons.slice(0, 4),
    ...(floor.osId !== "tech-os" ? [techRick, techYaz, techRory] : []),
  ];

  return {
    originalTask: task,
    verbDrivenMandate,
    targetFloor: floor,
    loopAndDimensionContext: {
      sovereignS0: "Amadou Kone (human:amdkn) · S0 Out of the Loop · 10D Sovereign Posture",
      ceoPosture: "A0 Amadeus (aspace:a0:amadeus) · 7D Hyper-Meta-Vision & Foundation Weight Encoder",
      fuguTrinityAssignment: {
        conductor: "Sakana AI Fugu Conductor 7B RL + LFM3-Omni-2B (:9931) + Needle 3 + GLiNER2.5-multi-Decide",
        thinker: "1D EGM Elephant + Clean-Room Spec + Doctors S2 (D11/D12/D13) PRD on Agent-Office Mezzanine",
        worker: "1D EGM Goldfish Isolated Context + Companions S3 / 64 DC B2..I2 / 448 Marvel B3..I3",
        verifier: "Outside Judge + S1-RICK (R10) + S3-YAZ (LiDAR) + S3-RORY (4P MiroFish Wargame)",
      },
    },
    emythGateCheck: {
      jerryFiveSecondClarity:
        "Surface summary & 2D [Tab] Portal Board must be readable in <= 5 seconds (Spock Area bound).",
      summerImmediateAction:
        "First concrete tool call executes immediately in the current turn (Picard Project bound).",
      bethVitalState: bethState,
      mortyEdgeCaseFallback:
        "Native read-back after every write + deterministic rollback checkpoint in 02_Factory/factory.sqlite.",
      ld00ScaleElevation:
        "LD00 (Beth & Morty scale elevation in Areas OS) coordinates Life OS (L1) aligned with Tech OS (L0).",
      roryMiroFishWargame:
        "S3-RORY runs 4P edge-case prediction & MiroFish Wargames across S2/A2/B2 so S3/A3/B3 trigger zero Gatekeeper vetos.",
      rickEpistemicVeto:
        "Zero proprietary lock-in, Zero Telemetry (aspace-telemetry-shield.cjs), deterministic checks.ps1 pass, and R10 receipt.",
    },
    vectors: {
      speed: {
        cadence: "Fable 5 80/20 cadence (>80% tool_use, 1-2 telegraphic sentences between tools, 5s backgrounding rule).",
        parallelHarnesses: ["dsh", "pi", "claude", "codex", "opencode", "agy", "hc", "orca"],
        unreasonableLatencyTarget: "Target <= 200ms local response (LFM3 :9931 / FreeLLMAPI :31415) & single-turn self-healing closure.",
      },
      altitude: {
        goalBeyondTheGoal: `Beyond completing "${task}", establish a reusable, self-verifying Holon capability across Floor ${floor.floor} (${floor.name}) that compounds A0 Amadeus's 7D autonomy while keeping Amadou Kone in S0 (10D Out of the Loop).`,
        topThreeUrgentDecisions: [
          {
            decision: `Should "${task}" be codified as a permanent 4D heartbeat & 2D Portal Board in ${floor.name}?`,
            argumentFor: "Eliminates recurring human attention cost and guarantees 24/7 execution consistency across the 578 Holons.",
            argumentAgainst: "Requires strict Clean-Room 1D schema & idempotence guards in factory.sqlite to prevent drift.",
          },
          {
            decision: "Should Rory pre-simulate this workflow in MiroFish across S2/A2/B2 before S3/A3/B3 dispatch?",
            argumentFor: "Predicts edge cases and guarantees zero Gatekeeper refusals/vetos from S1-RICK or A1-BETH/MORTY.",
            argumentAgainst: "Adds a fast pre-flight simulation step before external side effects.",
          },
          {
            decision: "Does any part of this task cross the S0 sovereign ratification boundary (human:amdkn)?",
            argumentFor: "Escalating true constitutional/external-spend boundaries preserves Law I.",
            argumentAgainst: "Over-escalating routine 3D-6D engineering violates the 95% E-Myth filter.",
          },
        ],
        systemicPreventionMechanism:
          "Register deterministic regression check in 02_Factory/checks.ps1 + Rory MiroFish wargame scenario + append provenance trace to 00_Memoire/bundle/log.md and Graphify.",
      },
      depth: {
        step1DomainExpertStandard:
          "Include Clean-Room 1D spec, EGM Goldfish context isolation, idempotency (requestId), zero-telemetry shield, and adversarial edge-case coverage unprompted.",
        step2RawestMaterialSources: [
          "00_Memoire/raw/aspace-os-drive-canon-2026.md",
          "00_Memoire/raw/felix-rieseberg-ambition-2026.md",
          "00_Memoire/raw/sakana-fugu-10d-architecture-2026.md",
          "00_Memoire/bundle/index.md",
          "02_Factory/factory.sqlite",
        ],
        step3IndustryGradeInstruments: [
          "SQLite WAL state & Pi Durable checkpoints",
          "Sakana AI Fugu TRINITY + LFM3-Omni-2B (:9931) + FreeLLMAPI (:31415) + Zero-Telemetry codex-chatgpt-web",
          "pwsh -NoProfile -File 02_Factory/checks.ps1 (6 deterministic gates)",
          "Graphify knowledge graph (00_Memoire/.venv/Scripts/graphify.exe)",
        ],
        step4OutsideJudgeProtocol:
          "Independent read-only audit by S1-RICK (anti-rent & zero-telemetry), S3-YAZ (LiDAR & checks.ps1), and S3-RORY (4P MiroFish Wargame) before marking delivery ready.",
      },
      range: {
        nounToVerbTransformation: verbDrivenMandate,
        holonCrew,
        redTeamCritic: "S1-RICK (Near of the Loop Veto) + A1-MORTY / LD00 (Edge-case Critic) + S3-RORY (4P MiroFish Wargame)",
      },
    },
  };
}

/**
 * Outside Judge evaluator (Felix Rieseberg Depth Step 4 + S1-RICK / S3-YAZ / S3-RORY).
 */
export function evaluateWithOutsideJudge(params: {
  deliverableSummary: string;
  hasAutomatedTests: boolean;
  testsPassed: boolean;
  usesRawSources: boolean;
  preservesAppendOnlyLog: boolean;
  bethVitalState?: BethVitalState;
}): OutsideJudgeVerdict {
  const bethState = params.bethVitalState ?? "GREEN";
  const checks = [
    {
      gate: "S1-RICK · Zero Theater / Executable Proof & Zero Telemetry",
      passed: params.hasAutomatedTests && params.testsPassed,
      detail:
        params.hasAutomatedTests && params.testsPassed
          ? "Deliverable is backed by automated tests that pass 100% with zero external telemetry."
          : "Missing or failing automated test execution proof.",
    },
    {
      gate: "Depth Step 2 · Grounded in Raw Sources (0D IPBD -> 1D Clean-Room)",
      passed: params.usesRawSources,
      detail: params.usesRawSources
        ? "Directly grounded in 00_Memoire/raw/ and live system state."
        : "Not verified against primary raw sources.",
    },
    {
      gate: "S3-GRAHAM & S3-RORY (4P) · WikiLLM Append-Only Integrity",
      passed: params.preservesAppendOnlyLog,
      detail: params.preservesAppendOnlyLog
        ? "00_Memoire/bundle/log.md append-only invariant respected."
        : "Violation of append-only log invariant.",
    },
    {
      gate: "A1-BETH & LD00 · Biological & Nocturnal Sanctuary",
      passed: bethState !== "HALT_LD03" && bethState !== "HALT_LD04",
      detail: `Current Beth Vital State: ${bethState}`,
    },
    {
      gate: "B1-JERRY & J1 (LD09) · 5-Second Clarity Surface",
      passed: params.deliverableSummary.trim().length >= 20,
      detail: "Deliverable includes a clear executive summary.",
    },
  ];

  const passedCount = checks.filter((c) => c.passed).length;
  const score = Math.round((passedCount / checks.length) * 100);
  const remediationRequired = checks.filter((c) => !c.passed).map((c) => `${c.gate}: ${c.detail}`);

  return {
    passed: remediationRequired.length === 0,
    score,
    judges: ["S1-RICK", "S3-YAZ", "S3-RORY", "LD00-BETH-MORTY", "B1-JERRY", "J1-META-JERRY"],
    checks,
    remediationRequired,
  };
}

/**
 * Resolve the root of Aspace OS V5 workspace from anywhere inside 01_Forkable/FKB00_Runtime/automaton.
 */
export function resolveAspaceRoot(explicitRoot?: string): string {
  if (explicitRoot && fs.existsSync(explicitRoot)) {
    return explicitRoot;
  }
  if (process.env.ASPACE_OS_ROOT && fs.existsSync(process.env.ASPACE_OS_ROOT)) {
    return process.env.ASPACE_OS_ROOT;
  }
  const candidate = path.resolve(process.cwd(), "..", "..");
  if (fs.existsSync(path.join(candidate, "02_Factory", "factory.ps1"))) {
    return candidate;
  }
  if (fs.existsSync(path.join(process.cwd(), "02_Factory", "factory.ps1"))) {
    return process.cwd();
  }
  return "C:\\Users\\amado\\Aspace OS V5";
}

/**
 * Execute an Aspace OS V5 02_Factory/factory.ps1 command from the CEO Digital Twin.
 */
export async function runAspaceFactoryCommand(
  args: string[],
  aspaceRoot?: string,
  timeoutMs = 15000,
): Promise<{ ok: boolean; stdout: string; stderr: string }> {
  const root = resolveAspaceRoot(aspaceRoot);
  const scriptPath = path.join(root, "02_Factory", "factory.ps1");
  try {
    const { stdout, stderr } = await execFileAsync(
      "pwsh",
      ["-NoProfile", "-File", scriptPath, ...args],
      { cwd: root, timeout: timeoutMs },
    );
    return { ok: true, stdout: stdout.trim(), stderr: stderr.trim() };
  } catch (err: any) {
    return {
      ok: false,
      stdout: (err?.stdout ?? "").toString().trim(),
      stderr: (err?.stderr ?? err?.message ?? String(err)).toString().trim(),
    };
  }
}

/**
 * Read a WikiLLM page from 00_Memoire/bundle/ or 00_Memoire/raw/.
 */
export function readAspaceWikiPage(relativePath = "bundle/index.md", aspaceRoot?: string): string {
  const root = resolveAspaceRoot(aspaceRoot);
  const safeRel = relativePath.replace(/^(\.\.[/\\])+/, "");
  const fullPath = path.join(root, "00_Memoire", safeRel);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`WikiLLM file not found: ${fullPath}`);
  }
  return fs.readFileSync(fullPath, "utf8");
}
