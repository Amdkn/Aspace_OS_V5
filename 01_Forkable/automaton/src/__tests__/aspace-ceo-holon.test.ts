import { describe, expect, it } from "vitest";
import {
  A0_CEO_HOLON,
  ASPACE_3OS_FLOORS,
  ASPACE_DIMENSIONAL_LADDER,
  ASPACE_LOOP_HIERARCHY,
  ASPACE_SAKANA_FUGU_INFERENCE,
  evaluateWithOutsideJudge,
  getFloorByOs,
  inferTargetOsFloor,
  upgradeTaskWithAmbition,
} from "../aspace/holon-topology.js";
import { createBuiltinTools } from "../agent/tools.js";
import { BUILTIN_TASKS } from "../heartbeat/tasks.js";

describe("A0 Amadeus 24/7 Digital Twin CEO (7D) & 3-OS Holon Topology (578 Holons)", () => {
  it("exposes the canonical A0 Amadeus CEO (7D), S0 Amadou Kone (10D), and 578 Holons across 3 OS floors", () => {
    expect(A0_CEO_HOLON.holonId).toBe("aspace:a0:amadeus");
    expect(A0_CEO_HOLON.posture).toContain("7D");
    expect(A0_CEO_HOLON.sovereignHuman.name).toBe("Amadou Kone");
    expect(A0_CEO_HOLON.sovereignHuman.ratificationSignature).toBe("human:amdkn");
    expect(A0_CEO_HOLON.sovereignHuman.loopRing).toContain("S0");
    expect(A0_CEO_HOLON.sovereignHuman.posture).toContain("10D");
    expect(A0_CEO_HOLON.localSovereignInference.neverDiesOnZeroCryptoBalance).toBe(true);

    expect(ASPACE_LOOP_HIERARCHY.S0.position).toBe("Out of the Loop");
    expect(ASPACE_LOOP_HIERARCHY.S1.position).toBe("Near of the Loop");
    expect(ASPACE_LOOP_HIERARCHY.S2.position).toBe("Close of the Loop");
    expect(ASPACE_LOOP_HIERARCHY.S3.position).toBe("Keep Aspace Loop Alive");
    expect(ASPACE_DIMENSIONAL_LADDER).toHaveLength(9);
    expect(ASPACE_SAKANA_FUGU_INFERENCE.multiPlatformHub.zeroTelemetryVerified).toBe(true);

    expect(ASPACE_3OS_FLOORS).toHaveLength(3);
    expect(ASPACE_3OS_FLOORS[0].osId).toBe("tech-os");
    expect(ASPACE_3OS_FLOORS[0].totalHolons).toBe(13);
    expect(ASPACE_3OS_FLOORS[1].osId).toBe("life-os");
    expect(ASPACE_3OS_FLOORS[1].totalHolons).toBe(43);
    expect(ASPACE_3OS_FLOORS[2].osId).toBe("areas-os");
    expect(ASPACE_3OS_FLOORS[2].totalHolons).toBe(522);
    expect(getFloorByOs("business-os").osId).toBe("areas-os");

    const totalHolons = ASPACE_3OS_FLOORS.reduce((acc, f) => acc + f.totalHolons, 0);
    expect(totalHolons).toBe(578);
  });

  it("infers the right OS floor and upgrades tasks across Felix Rieseberg's 4 vectors + Sakana Fugu TRINITY", () => {
    expect(inferTargetOsFloor("Deploy OMK Office Stripe pipeline for LD01").osId).toBe("areas-os");
    expect(inferTargetOsFloor("Sync 12WY calendar focus blocks and Beth sleep shield").osId).toBe("life-os");
    expect(inferTargetOsFloor("Fix SQLite writerLock in Pi Durable subagents").osId).toBe("tech-os");

    const upgraded = upgradeTaskWithAmbition("Create a doc for OMK Office client onboarding");
    expect(upgraded.targetFloor.osId).toBe("areas-os");
    expect(upgraded.verbDrivenMandate).toContain("Clean-Room (EGM)");
    expect(upgraded.loopAndDimensionContext.fuguTrinityAssignment.conductor).toContain("Sakana AI Fugu");
    expect(upgraded.emythGateCheck.roryMiroFishWargame).toContain("MiroFish");
    expect(upgraded.vectors.altitude.topThreeUrgentDecisions).toHaveLength(3);
    expect(upgraded.vectors.depth.step4OutsideJudgeProtocol).toContain("S1-RICK");
    expect(upgraded.vectors.range.holonCrew.some((h) => h.id === "S1-RICK")).toBe(true);
    expect(upgraded.vectors.range.holonCrew.some((h) => h.id === "S3-RORY")).toBe(true);
  });

  it("enforces the Outside Judge gate and blocks when tests fail or Beth/LD00 is in HALT state", () => {
    const passing = evaluateWithOutsideJudge({
      deliverableSummary: "3-OS Holon Cube Farm × Agent-Office floor architecture verified with unit tests.",
      hasAutomatedTests: true,
      testsPassed: true,
      usesRawSources: true,
      preservesAppendOnlyLog: true,
      bethVitalState: "GREEN",
    });
    expect(passing.passed).toBe(true);
    expect(passing.score).toBe(100);
    expect(passing.judges).toContain("S3-RORY");
    expect(passing.judges).toContain("LD00-BETH-MORTY");
    expect(passing.judges).toContain("J1-META-JERRY");

    const halted = evaluateWithOutsideJudge({
      deliverableSummary: "Late-night intrusive deployment",
      hasAutomatedTests: true,
      testsPassed: false,
      usesRawSources: true,
      preservesAppendOnlyLog: true,
      bethVitalState: "HALT_LD03",
    });
    expect(halted.passed).toBe(false);
    expect(halted.remediationRequired.length).toBeGreaterThanOrEqual(2);
  });

  it("registers the Aspace Holon tools and 24/7 heartbeat tasks in Automaton", () => {
    const tools = createBuiltinTools("sandbox-aspace");
    const names = tools.map((t) => t.name);
    expect(names).toContain("aspace_3os_holon_map");
    expect(names).toContain("aspace_ambition_upgrade");
    expect(names).toContain("aspace_outside_judge");
    expect(names).toContain("aspace_factory_spine");
    expect(names).toContain("aspace_wiki_memory");

    expect(typeof BUILTIN_TASKS.aspace_ceo_3os_sync).toBe("function");
    expect(typeof BUILTIN_TASKS.aspace_beth_homeostasis).toBe("function");
  });
});
