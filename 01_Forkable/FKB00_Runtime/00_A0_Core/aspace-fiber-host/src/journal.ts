/**
 * @aspace/fiber-host — receipt journal (JSONL).
 *
 * Append-only, synchronous writes: a crash of the calling process cannot lose
 * an event already returned. `observed_at` (when the fact happened) and
 * `recorded_at` (when the journal line was written) are separate, ISO 8601
 * with offset, `recorded_at >= observed_at`.
 */
import { appendFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { dirname, join } from 'node:path'

export type JournalEventType =
  | 'invoke-start'
  | 'invoke-complete'
  | 'receipt'
  | 'lease-grant'
  | 'lease-expire'
  | 'rollback'
  | 'reconcile'
  | 'cleanup'
  | 'activation-rollback'
  | 'crash-recovery'

export interface JournalEvent {
  seq: number
  type: JournalEventType
  request_id?: string
  fiber_id?: string
  observed_at: string
  recorded_at: string
  detail: Record<string, unknown>
}

export function isoNow(): string {
  const d = new Date()
  const tz = -d.getTimezoneOffset()
  const sign = tz >= 0 ? '+' : '-'
  const pad = (n: number) => String(Math.abs(n)).padStart(2, '0')
  const ms = String(d.getMilliseconds()).padStart(3, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}.${ms}${sign}${pad(Math.floor(Math.abs(tz) / 60))}:${pad(Math.abs(tz) % 60)}`
}

/** SHA-256 of a canonical (key-sorted) JSON value — payload identity for replay. */
export function payloadHash(payload: unknown): string {
  const canon = (v: unknown): unknown => {
    if (Array.isArray(v)) return v.map(canon)
    if (v !== null && typeof v === 'object') {
      return Object.fromEntries(Object.entries(v as Record<string, unknown>).sort(([a], [b]) => (a < b ? -1 : 1)).map(([k, val]) => [k, canon(val)]))
    }
    return v
  }
  return createHash('sha256').update(JSON.stringify(canon(payload))).digest('hex')
}

export class Journal {
  readonly path: string
  private seq = 0

  constructor(dir: string) {
    mkdirSync(dir, { recursive: true })
    this.path = join(dir, 'fiber-host.journal.jsonl')
    if (existsSync(this.path)) {
      for (const line of readFileSync(this.path, 'utf-8').split('\n')) {
        if (!line.trim()) continue
        try {
          const ev = JSON.parse(line) as JournalEvent
          if (typeof ev.seq === 'number' && ev.seq > this.seq) this.seq = ev.seq
        } catch {
          // A torn last line (crash mid-write) is skipped, never fatal.
        }
      }
    }
  }

  /** Read all well-formed events, in file order. */
  readAll(): JournalEvent[] {
    if (!existsSync(this.path)) return []
    const out: JournalEvent[] = []
    for (const line of readFileSync(this.path, 'utf-8').split('\n')) {
      if (!line.trim()) continue
      try {
        out.push(JSON.parse(line) as JournalEvent)
      } catch {
        // torn line — skip
      }
    }
    return out
  }

  append(type: JournalEventType, detail: Record<string, unknown>, opts: { request_id?: string, fiber_id?: string } = {}): JournalEvent {
    const observed = isoNow()
    const ev: JournalEvent = {
      seq: ++this.seq,
      type,
      ...(opts.request_id ? { request_id: opts.request_id } : {}),
      ...(opts.fiber_id ? { fiber_id: opts.fiber_id } : {}),
      observed_at: observed,
      recorded_at: isoNow(),
      detail,
    }
    appendFileSync(this.path, JSON.stringify(ev) + '\n')
    return ev
  }

  /** Last seq written (0 when the journal is empty). */
  get lastSeq(): number {
    return this.seq
  }

  /** The stored receipt for a completed request_id, if any (with its payload hash). */
  completedReceipt(requestId: string): Record<string, unknown> | null {
    let found: Record<string, unknown> | null = null
    for (const ev of this.readAll()) {
      if (ev.type === 'invoke-complete' && ev.request_id === requestId) {
        found = { ...(ev.detail.receipt as Record<string, unknown>), payload_hash: ev.detail.payload_hash }
      }
    }
    return found
  }

  /** request_ids started but never completed (crash in flight). */
  orphanedStarts(): JournalEvent[] {
    const completed = new Set<string>()
    const started: JournalEvent[] = []
    for (const ev of this.readAll()) {
      if (ev.type === 'invoke-complete' && ev.request_id) completed.add(ev.request_id)
      if (ev.type === 'invoke-start' && ev.request_id) started.push(ev)
    }
    return started.filter((ev) => ev.request_id && !completed.has(ev.request_id))
  }
}

export function journalFileName(): string {
  return 'fiber-host.journal.jsonl'
}
