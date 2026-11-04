import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "@earendil-works/pi-ai";
import { execFileSync } from "node:child_process";

function runPwsh(args: string[], cwd: string): string {
  try {
    return execFileSync("pwsh", ["-NoProfile", "-ExecutionPolicy", "Bypass", ...args], {
      cwd,
      encoding: "utf8",
      timeout: 30000,
    });
  } catch (err: any) {
    return (err?.stdout || "") + "\n" + (err?.stderr || err?.message || String(err));
  }
}

export default function (pi: ExtensionAPI) {
  // 1. Unified `subagents` tool implementing `pi-durable-subagents` + `earendil.com/posts/pi-durable` natively on Windows & across all V5 harnesses
  pi.registerTool({
    name: "subagents",
    label: "Durable Subagents (Pi Durable + DeepSeek Superagent + Herdr/Orca)",
    description:
      "Crash-safe, idempotent durable subagents that never lose work and never do it twice. Supports action='agents'|'status'|'send'|'resume', single agent/task run, sequential chain (with {previous}), worktree writer locks, and tail/grep output filtering.",
    parameters: Type.Object({
      action: Type.Optional(
        Type.String({
          description: "Action: 'agents' | 'status' | 'run' | 'chain' | 'send' | 'resume' (default: inferred from fields)",
        })
      ),
      agent: Type.Optional(Type.String({ description: "Subagent role (worker, reviewer, builder, spec-writer, intake-assessor, etc.)" })),
      harness: Type.Optional(Type.String({ description: "Target harness: pi, dsh, dsh-superagent, opencode, claude-code, codex" })),
      task: Type.Optional(Type.String({ description: "Task prompt for a single durable subagent run" })),
      chain: Type.Optional(
        Type.Array(
          Type.Object({
            agent: Type.String(),
            task: Type.String({ description: "Task prompt; supports {previous} interpolation" }),
            writer: Type.Optional(Type.Boolean()),
          }),
          { description: "Sequential durable pipeline of subagents" }
        )
      ),
      wid: Type.Optional(Type.String({ description: "Workflow ID for status or resume" })),
      to: Type.Optional(Type.String({ description: "Target '<wid>/<key>' for action='send'" })),
      kind: Type.Optional(Type.String({ description: "'steer' (replaces older steers) or 'notify' for action='send'" })),
      message: Type.Optional(Type.String({ description: "Steering or notification message for action='send'" })),
      requestId: Type.Optional(Type.String({ description: "Idempotency key so retries after a crash never duplicate work" })),
      writer: Type.Optional(Type.Boolean({ description: "Whether this subagent writes to the worktree (acquires writerLock)" })),
      tail: Type.Optional(Type.Number({ description: "Return last N lines of output in status" })),
      grep: Type.Optional(Type.String({ description: "Filter output lines by regex in status" })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      let act = params.action || "status";
      if (!params.action) {
        if (params.chain && params.chain.length > 0) act = "chain";
        else if (params.task) act = "run";
        else if (params.to && params.message) act = "send";
      }
      const args = ["-File", "factory/factory.ps1", "subagents", "-Action", act];
      if (params.agent) args.push("-Agent", params.agent);
      if (params.harness) args.push("-Harness", params.harness);
      if (params.task) args.push("-Task", params.task);
      if (params.chain) args.push("-ChainJson", JSON.stringify(params.chain));
      if (params.wid) args.push("-Wid", params.wid);
      if (params.to) args.push("-To", params.to);
      if (params.kind) args.push("-Kind", params.kind);
      if (params.message) args.push("-Message", params.message);
      if (params.requestId) args.push("-RequestId", params.requestId);
      if (params.writer !== undefined) args.push("-Writer", params.writer ? "$true" : "$false");
      if (params.tail) args.push("-Tail", String(params.tail));
      if (params.grep) args.push("-Grep", params.grep);

      const out = runPwsh(args, ctx.cwd);
      return { content: [{ type: "text", text: out.trim() }], details: {} };
    },
  });

  // 2. `handoff` & `search_history` tools from Pi Durable (earendil.com/posts/pi-durable/)
  pi.registerTool({
    name: "handoff",
    label: "Pi Durable Handoff",
    description: "Commit a durable handoff checkpoint note to SQLite while keeping all prior history searchable via search_history.",
    parameters: Type.Object({
      note: Type.String({ description: "Structured handoff note summarizing state, completed checkpoints, and next Mandate" }),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const out = runPwsh(["-File", "factory/factory.ps1", "subagents", "-Action", "handoff", "-Note", params.note], ctx.cwd);
      return { content: [{ type: "text", text: out.trim() }], details: {} };
    },
  });

  pi.registerTool({
    name: "search_history",
    label: "Pi Durable Search History",
    description: "Search older events, tickets, and prior handoff snapshots stored in factory.sqlite.",
    parameters: Type.Object({
      text: Type.String({ description: "Substring or keyword to search in durable history" }),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const out = runPwsh(["-File", "factory/factory.ps1", "subagents", "-Action", "search-history", "-Query", params.text], ctx.cwd);
      return { content: [{ type: "text", text: out.trim() }], details: {} };
    },
  });

  // 3. Aspace Software Factory tools
  pi.registerTool({
    name: "factory_status",
    label: "Factory Status",
    description: "Get the Aspace Software Factory Mission Control status (DeepSeek 3-Question Panel + Pi Durable Workflows)",
    parameters: Type.Object({}),
    async execute(_toolCallId, _params, _signal, _onUpdate, ctx) {
      const out = runPwsh(["-File", "factory/factory.ps1", "status"], ctx.cwd);
      return { content: [{ type: "text", text: out.trim() }], details: {} };
    },
  });

  pi.registerTool({
    name: "factory_gate",
    label: "Factory Deterministic Gate",
    description: "Run the 6 deterministic quality, security, DOX, and WikiLLM checks (factory/checks.ps1)",
    parameters: Type.Object({}),
    async execute(_toolCallId, _params, _signal, _onUpdate, ctx) {
      const out = runPwsh(["-File", "factory/checks.ps1"], ctx.cwd);
      return { content: [{ type: "text", text: out.trim() }], details: {} };
    },
  });

  pi.registerTool({
    name: "factory_intake",
    label: "Factory Intake Ticket",
    description: "Create a new durable Ticket with Mandate in the Aspace Software Factory SQLite spine",
    parameters: Type.Object({
      title: Type.String({ description: "Ticket title" }),
      mandate: Type.String({ description: "Concrete Mandate and acceptance criteria" }),
      harness: Type.Optional(Type.String({ description: "Harness (pi, dsh, dsh-superagent, opencode, claude-code, codex)" })),
      requestId: Type.Optional(Type.String({ description: "Optional idempotent requestId" })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const args = [
        "-File",
        "factory/factory.ps1",
        "intake",
        "-Title",
        params.title,
        "-Mandate",
        params.mandate,
        "-Harness",
        params.harness || "pi",
        "-Source",
        "pi:extension",
      ];
      if (params.requestId) args.push("-RequestId", params.requestId);
      const out = runPwsh(args, ctx.cwd);
      return { content: [{ type: "text", text: out.trim() }], details: {} };
    },
  });

  pi.registerCommand("factory", {
    description: "Run Aspace Software Factory status & gate check",
    handler: async (_args, ctx) => {
      const out = runPwsh(["-File", "factory/factory.ps1", "status"], ctx.cwd);
      ctx.ui.notify(out.split("\n").slice(0, 5).join(" | "), "info");
    },
  });

  pi.registerCommand("subagents", {
    description: "List durable subagents workflows & writer locks",
    handler: async (_args, ctx) => {
      const out = runPwsh(["-File", "factory/factory.ps1", "subagents", "-Action", "status"], ctx.cwd);
      ctx.ui.notify(out.slice(0, 300), "info");
    },
  });
}
