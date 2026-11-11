/**
 * @aspace/fiber-host — AspaceFiberManifest v1.
 *
 * Contract version 1 (design P1, D-2). Hand-rolled validator, zero dependencies.
 * The JSON Schema file (schemas/aspace-fiber-manifest-v1.json) is the reference;
 * this validator enforces the same rules in code so a bad manifest fails fast
 * with the offending field named.
 */
import { ManifestError } from './errors.ts'

export const CONTRACT_VERSION = '1'

export type FiberKind = 'service' | 'agent' | 'tool' | 'registry' | 'evaluator' | 'research'
export type TransportType = 'in-process' | 'unix-socket' | 'http-loopback'
export type EntryLanguage = 'ts' | 'rust' | 'python'

export interface FiberManifest {
  contract_version: string
  id: string
  kind: FiberKind
  version: string
  source: { repo: string, frozen_commit: string, license: string, provenance: string }
  entry: { language: EntryLanguage, path: string }
  adapter: { version: string, commit: string }
  capabilities: string[]
  requires: string[]
  coeffects: string[]
  permissions: { network: 'loopback' | 'none', shell: boolean, files: string[], secrets: string[] }
  transport: { type: TransportType, socket_path?: string, url?: string, ops: string[] }
  lifecycle: { prepare?: string, start: string, health: string, lease: { ttl_ms: number }, dispose: string, rollback?: string }
  state_owner: string
  holdouts: string[]
}

const ID_PATTERN = /^fiber:a0:[a-z0-9][a-z0-9-]*$/
const KINDS: FiberKind[] = ['service', 'agent', 'tool', 'registry', 'evaluator', 'research']
const TRANSPORTS: TransportType[] = ['in-process', 'unix-socket', 'http-loopback']
const LANGUAGES: EntryLanguage[] = ['ts', 'rust', 'python']

function fail(field: string, why: string): never {
  throw new ManifestError(`manifeste invalide — champ ${field} : ${why}`)
}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v)
}

function reqString(obj: Record<string, unknown>, field: string): string {
  const v = obj[field]
  if (typeof v !== 'string' || v.length === 0) fail(field, 'chaîne non vide exigée')
  return v as string
}

function reqStrings(obj: Record<string, unknown>, field: string): string[] {
  const v = obj[field]
  if (!Array.isArray(v) || v.some((x) => typeof x !== 'string')) fail(field, 'liste de chaînes exigée')
  return v as string[]
}

/** Validate an unknown value as a FiberManifest v1. Throws ManifestError. */
export function validateManifest(value: unknown): FiberManifest {
  if (!isRecord(value)) fail('(racine)', 'objet exigé')
  const m = value as Record<string, unknown>
  if (m.contract_version !== CONTRACT_VERSION) {
    fail('contract_version', `exigé "${CONTRACT_VERSION}", reçu ${JSON.stringify(m.contract_version)}`)
  }
  const id = reqString(m, 'id')
  if (!ID_PATTERN.test(id)) fail('id', `motif fiber:a0:<nom> exigé, reçu ${id}`)
  const kind = reqString(m, 'kind')
  if (!KINDS.includes(kind as FiberKind)) fail('kind', `l'un de ${KINDS.join(', ')} exigé`)
  reqString(m, 'version')
  if (!isRecord(m.source)) fail('source', 'objet exigé')
  for (const f of ['repo', 'frozen_commit', 'license', 'provenance']) reqString(m.source, f)
  if (!isRecord(m.entry)) fail('entry', 'objet exigé')
  const lang = reqString(m.entry, 'language')
  if (!LANGUAGES.includes(lang as EntryLanguage)) fail('entry.language', `l'une de ${LANGUAGES.join(', ')} exigée`)
  reqString(m.entry, 'path')
  if (!isRecord(m.adapter)) fail('adapter', 'objet exigé')
  reqString(m.adapter, 'version')
  reqString(m.adapter, 'commit')
  const capabilities = reqStrings(m, 'capabilities')
  const requires = reqStrings(m, 'requires')
  const coeffects = reqStrings(m, 'coeffects')
  if (!isRecord(m.permissions)) fail('permissions', 'objet exigé')
  const network = reqString(m.permissions, 'network')
  if (network !== 'loopback' && network !== 'none') fail('permissions.network', 'loopback ou none exigé')
  if (typeof m.permissions.shell !== 'boolean') fail('permissions.shell', 'booléen exigé')
  const files = reqStrings(m.permissions, 'files')
  const secrets = reqStrings(m.permissions, 'secrets')
  if (!isRecord(m.transport)) fail('transport', 'objet exigé')
  const ttype = reqString(m.transport, 'type')
  if (!TRANSPORTS.includes(ttype as TransportType)) fail('transport.type', `l'un de ${TRANSPORTS.join(', ')} exigé`)
  if (ttype === 'unix-socket' && typeof m.transport.socket_path !== 'string') {
    fail('transport.socket_path', 'chemin de socket exigé pour unix-socket')
  }
  if (ttype === 'http-loopback' && typeof m.transport.url !== 'string') {
    fail('transport.url', 'URL exigée pour http-loopback')
  }
  const ops = reqStrings(m.transport, 'ops')
  if (!isRecord(m.lifecycle)) fail('lifecycle', 'objet exigé')
  reqString(m.lifecycle, 'start')
  reqString(m.lifecycle, 'health')
  reqString(m.lifecycle, 'dispose')
  if (!isRecord(m.lifecycle.lease)) fail('lifecycle.lease', 'objet exigé')
  const ttl = m.lifecycle.lease.ttl_ms
  if (typeof ttl !== 'number' || !Number.isFinite(ttl) || ttl <= 0) {
    fail('lifecycle.lease.ttl_ms', 'nombre > 0 exigé')
  }
  reqString(m, 'state_owner')
  const holdouts = reqStrings(m, 'holdouts')
  return {
    contract_version: CONTRACT_VERSION,
    id,
    kind: kind as FiberKind,
    version: m.version as string,
    source: m.source as FiberManifest['source'],
    entry: m.entry as FiberManifest['entry'],
    adapter: m.adapter as FiberManifest['adapter'],
    capabilities,
    requires,
    coeffects,
    permissions: { network: network as 'loopback' | 'none', shell: m.permissions.shell as boolean, files, secrets },
    transport: m.transport as FiberManifest['transport'],
    lifecycle: m.lifecycle as FiberManifest['lifecycle'],
    state_owner: m.state_owner as string,
    holdouts,
  }
}
