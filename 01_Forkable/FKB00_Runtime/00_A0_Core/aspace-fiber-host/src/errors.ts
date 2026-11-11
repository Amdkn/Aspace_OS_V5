/**
 * @aspace/fiber-host — errors.
 * Every failure is a named error, never a silent skip.
 */
export class FiberHostError extends Error {
  readonly code: string
  constructor(code: string, message: string) {
    // The code is part of the message: tests and journals match on it.
    super(`[${code}] ${message}`)
    this.name = 'FiberHostError'
    this.code = code
  }
}

export class ManifestError extends FiberHostError {
  constructor(message: string) {
    super('manifest-invalid', message)
    this.name = 'ManifestError'
  }
}

export class UnknownFiberError extends FiberHostError {
  constructor(id: string) {
    super('unknown-fiber', `fiber inconnue : ${id}`)
    this.name = 'UnknownFiberError'
  }
}

export class DependencyError extends FiberHostError {
  constructor(message: string) {
    super('dependency', message)
    this.name = 'DependencyError'
  }
}

export class LeaseExpiredError extends FiberHostError {
  constructor(id: string) {
    super('lease-expired', `bail expiré pour ${id} — réactivation exigée`)
    this.name = 'LeaseExpiredError'
  }
}

export class LeaseRequiredError extends FiberHostError {
  constructor(id: string) {
    super('lease-required', `invoke sur ${id} sans lease_token valide — refusé`)
    this.name = 'LeaseRequiredError'
  }
}

export class TransportError extends FiberHostError {
  constructor(message: string) {
    super('transport', message)
    this.name = 'TransportError'
  }
}

export class StateError extends FiberHostError {
  constructor(message: string) {
    super('state', message)
    this.name = 'StateError'
  }
}
