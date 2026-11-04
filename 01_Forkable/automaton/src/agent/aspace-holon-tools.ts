/**
 * Aspace OS V5 — CEO Digital Twin (A0 Amadeus · 7D Posture) Built-in Tools for Automaton
 *
 * Exposes the 3-OS Holon Topology (578 Holons: Tech OS 13, Life OS 43, Areas OS 522),
 * Loop Hierarchy (S0..S3), Dimensional Ladder (0D..10D), Sakana AI Fugu Inference,
 * the 4-Vector Ambition Engine ("Modo de Volar"), the Outside Judge evaluator,
 * Aspace Software Factory (`factory/factory.ps1`), and WikiLLM (`00_Memoire/`) directly to Automaton.
 */

import type { AutomatonTool } from "../types.ts";
import {
  A0_CEO_HOLON,
  ASPACE_3OS_FLOORS,
  ASPACE_DIMENSIONAL_LADDER,
  ASPACE_DRIVE_REGISTRIES,
  ASPACE_LOOP_HIERARCHY,
  ASPACE_SAKANA_FUGU_INFERENCE,
  type AspaceOsId,
  type BethVitalState,
  evaluateWithOutsideJudge,
  getFloorByOs,
  readAspaceWikiPage,
  runAspaceFactoryCommand,
  upgradeTaskWithAmbition,
} from "../aspace/holon-topology.ts";

export function createAspaceHolonTools(): AutomatonTool[] {
  return [
    {
      name: "aspace_3os_holon_map",
      description:
        "Inspect the Aspace OS V5 3-OS Holon Architecture (578 Holons: Floor 1 Tech OS 13 Holons, Floor 2 Life OS 43 Holons, Floor 3 Areas OS 522 Holons nested in PARA), Loop Hierarchy (S0..S3), Dimensional Ladder (0D..10D), Sakana AI Fugu Inference Hub, and the A0 Amadeus 24/7 CEO profile.",
      category: "registry",
      riskLevel: "safe",
      parameters: {
        type: "object",
        properties: {
          os: {
            type: "string",
            enum: ["all", "tech-os", "life-os", "areas-os", "business-os"],
            description: "Filter by OS floor or return all 3 OS floors.",
          },
        },
      },
      execute: async (args) => {
        const os = (args.os as string | undefined) ?? "all";
        const floors =
          os === "all"
            ? ASPACE_3OS_FLOORS
            : [getFloorByOs(os as AspaceOsId)];
        return JSON.stringify(
          {
            ceo: A0_CEO_HOLON,
            loopHierarchy: ASPACE_LOOP_HIERARCHY,
            dimensionalLadder: ASPACE_DIMENSIONAL_LADDER,
            sakanaFuguInference: ASPACE_SAKANA_FUGU_INFERENCE,
            driveRegistries: ASPACE_DRIVE_REGISTRIES,
            floors,
          },
          null,
          2,
        );
      },
    },
    {
      name: "aspace_ambition_upgrade",
      description:
        "Upgrade any task or mandate using Felix Rieseberg's 'Modo de Volar' 4-Vector Ambition Engine (Speed, Altitude, Depth 4-step protocol, Range noun-to-verb + Holon crew assembly across the 578 Holons of the 3 OS floors + Sakana AI Fugu TRINITY assignment).",
      category: "skills",
      riskLevel: "safe",
      parameters: {
        type: "object",
        properties: {
          task: {
            type: "string",
            description: "The mandate, issue, or objective to upgrade with high ambition.",
          },
          target_os: {
            type: "string",
            enum: ["tech-os", "life-os", "areas-os", "business-os"],
            description: "Optional explicit target OS floor.",
          },
          beth_state: {
            type: "string",
            enum: ["GREEN", "ORANGE", "RED", "HALT_LD03", "HALT_LD04"],
            description: "Current A1-BETH / LD00 biological homeostasis state.",
          },
        },
        required: ["task"],
      },
      execute: async (args) => {
        const task = String(args.task ?? "").trim();
        const targetOs = args.target_os as AspaceOsId | undefined;
        const bethState = args.beth_state as BethVitalState | undefined;
        const upgraded = upgradeTaskWithAmbition(task, { targetOs, bethState });
        return JSON.stringify(upgraded, null, 2);
      },
    },
    {
      name: "aspace_outside_judge",
      description:
        "Run the independent Outside Judge verification gate (Felix Rieseberg Depth Step 4 + S1-RICK Epistemic Veto + S3-YAZ Telemetry + S3-RORY 4P MiroFish Wargame + LD00 Beth/Morty + B1-JERRY/J1 LD09 5s Clarity) before declaring any deliverable complete.",
      category: "self_mod",
      riskLevel: "safe",
      parameters: {
        type: "object",
        properties: {
          deliverable_summary: {
            type: "string",
            description: "5-second executive summary of the completed work.",
          },
          has_automated_tests: {
            type: "boolean",
            description: "Whether automated tests exist for the change.",
          },
          tests_passed: {
            type: "boolean",
            description: "Whether all automated tests passed.",
          },
          uses_raw_sources: {
            type: "boolean",
            description: "Whether the work was grounded in raw sources (00_Memoire/raw/ or SQLite state).",
          },
          preserves_append_only_log: {
            type: "boolean",
            description: "Whether 00_Memoire/bundle/log.md append-only integrity was preserved.",
          },
          beth_vital_state: {
            type: "string",
            enum: ["GREEN", "ORANGE", "RED", "HALT_LD03", "HALT_LD04"],
          },
        },
        required: [
          "deliverable_summary",
          "has_automated_tests",
          "tests_passed",
          "uses_raw_sources",
          "preserves_append_only_log",
        ],
      },
      execute: async (args) => {
        const verdict = evaluateWithOutsideJudge({
          deliverableSummary: String(args.deliverable_summary ?? ""),
          hasAutomatedTests: Boolean(args.has_automated_tests),
          testsPassed: Boolean(args.tests_passed),
          usesRawSources: Boolean(args.uses_raw_sources),
          preservesAppendOnlyLog: Boolean(args.preserves_append_only_log),
          bethVitalState: args.beth_vital_state as BethVitalState | undefined,
        });
        return JSON.stringify(verdict, null, 2);
      },
    },
    {
      name: "aspace_factory_spine",
      description:
        "Execute an Aspace Software Factory & Pi Durable Subagents operation via factory/factory.ps1 (status, gate, intake, subagents).",
      category: "vm",
      riskLevel: "caution",
      parameters: {
        type: "object",
        properties: {
          action: {
            type: "string",
            enum: ["status", "gate", "subagents-agents", "subagents-resume"],
            description: "Factory spine action to run.",
          },
        },
        required: ["action"],
      },
      execute: async (args) => {
        const action = String(args.action ?? "status");
        const cliArgs =
          action === "subagents-agents"
            ? ["subagents", "-Action", "agents"]
            : action === "subagents-resume"
              ? ["subagents", "-Action", "resume"]
              : [action];
        const res = await runAspaceFactoryCommand(cliArgs);
        return JSON.stringify(res, null, 2);
      },
    },
    {
      name: "aspace_wiki_memory",
      description:
        "Read a page from Aspace OS V5's WikiLLM memory (00_Memoire/bundle/index.md, 00_Memoire/bundle/log.md, 00_Memoire/bundle/concepts/*.md, or 00_Memoire/raw/*.md).",
      category: "memory",
      riskLevel: "safe",
      parameters: {
        type: "object",
        properties: {
          relative_path: {
            type: "string",
            description:
              "Path relative to 00_Memoire/ (e.g. 'bundle/index.md', 'bundle/concepts/aspace-3os-holons.md', 'raw/sakana-fugu-10d-architecture-2026.md').",
          },
        },
      },
      execute: async (args) => {
        const rel = String(args.relative_path ?? "bundle/index.md");
        return readAspaceWikiPage(rel);
      },
    },
  ];
}
