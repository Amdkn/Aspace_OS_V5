/**
 * @aspace/fiber-host — public surface.
 *
 * The upstream Cordis API is isolated behind @aspace/cordis-adapter; this
 * package only re-exports the adapter's pinned constants and adds the host's
 * own pinned surface (PINNED_HOST_SURFACE).
 */
export { createFiberHost, AspaceFiberHost, PINNED_HOST_SURFACE } from './host.ts'
export type {
  Envelope,
  InvokeResult,
  Lease,
  CoeffectHandler,
  FiberState,
  FiberRecord,
  HealthReport,
} from './host.ts'
export { validateManifest, CONTRACT_VERSION } from './manifest.ts'
export type { FiberManifest, FiberKind, TransportType, EntryLanguage } from './manifest.ts'
export { Journal, isoNow, payloadHash } from './journal.ts'
export type { JournalEvent, JournalEventType } from './journal.ts'
export { UnixSocketTransport, HttpLoopbackTransport, InProcessTransport, RIG_OPS, defaultRigSocketPath } from './transports.ts'
export type { Transport, InProcessImpl, RigOp } from './transports.ts'
export {
  FiberHostError,
  ManifestError,
  UnknownFiberError,
  DependencyError,
  LeaseExpiredError,
  LeaseRequiredError,
  TransportError,
  StateError,
} from './errors.ts'
export { ADAPTER_VERSION, PINNED_CORDIS_COMMIT, PINNED_HMR_VERSION, PINNED_HMR_SURFACE } from '@aspace/cordis-adapter'
