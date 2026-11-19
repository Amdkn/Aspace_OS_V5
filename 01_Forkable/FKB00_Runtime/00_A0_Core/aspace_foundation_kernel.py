#!/usr/bin/env python3
"""
aspace_foundation_kernel.py — Noyau d'Interconnexion L0/L1 de la Fondation A'Space OS V5.

Aligné octet pour octet sur les contrats formels de `fondation-13-1` (`src/lib.rs`,
`src/router.rs`, `src/memory.rs`) afin que tout événement, reçu R10 ou citation
épistémique émis par les noyaux Python K1..K5 soit recevable sans erreur par les
validateurs Rust `r10-receive`, `route-dispatch` et `recall-fact` :
  - C1 : EventJournal (`DISPATCH_KEYS`, `EVENT_TYPES`, `FUNCTIONS_13`, règles R1–R8)
  - C2 : R10Ledger (`R10_KEYS`, `R10_SCHEMA="aspace.r10-receipt.v1"`, règles V1–V8)
  - C3 : EpistemicCitation (`STATUSES`, `JUDGMENT_MARKERS`, `MOVED_MARKERS`, règles M1–M8)
  - C4 : FiberContract (propriété exclusive des capacités `capabilities_owned`)

Zéro dépendance externe, zéro télémétrie.
"""

from __future__ import annotations

import calendar
import datetime as dt
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
ENTRY_ID_RE = re.compile(r"^G-(\d{4})(\d{2})(\d{2})-(\d{3})$")
EVENT_ID_RE = re.compile(r"^EVT-(\d{4})(\d{2})(\d{2})-(\d{3})$")
DELIVERABLE_RE = re.compile(r"(?:#\d+|[0-9a-fA-F]{7,40})")

KERNEL_IDS = ("K1", "K2", "K3", "K4", "K5")

# === Alignement exact sur fondation-13-1/src/lib.rs ===
R10_KEYS = (
    "entry_id",
    "issuer",
    "mission_id",
    "observed_at",
    "proof",
    "recorded_at",
    "schema",
    "sha",
    "summary",
)
R10_SCHEMA = "aspace.r10-receipt.v1"

# === Alignement exact sur fondation-13-1/src/router.rs ===
DISPATCH_KEYS = (
    "actor_from",
    "actor_to",
    "at",
    "design_ref",
    "dispatch_id",
    "event_id",
    "payload",
    "proof",
    "type",
)

EVENT_TYPES = (
    "closure_pulse",
    "correction",
    "dispatch_ack",
    "dispatch_relayed",
    "dispatch_typed",
    "fact_recalled",
    "judgment_rendered",
    "judgment_requested",
    "merge_executed",
    "pulse",
)

FUNCTIONS_13 = (
    "structurer",
    "judge",
    "executor",
    "router",
    "receiver",
    "verifier",
    "decider",
    "discoverer",
    "observer",
    "interfacer",
    "fluer",
    "memorizer",
    "fabricator",
)

# === Alignement exact sur fondation-13-1/src/memory.rs ===
EPISTEMIC_STATUSES = (
    "vérifié",
    "consigné",
    "périmé",
    "contredit",
    "absent",
    "à venir",
)
JUDGMENT_MARKERS = (
    "verdict",
    "tranche",
    "consigne un reçu",
    "écrit au registre",
    "corrige silencieusement",
)
MOVED_MARKERS = ("périmé", "bougée", "re-résol", "déplacée")
DENIAL_TOKENS = ("aucun", "ne ", "ni ", "pas ", "rien", "sans ", "jamais")

ENONCE_RELATIVE_PATH = Path("00_Memoire/bundle/fusion/FUSION-ENONCE.md")
ENONCE_EXPECTED_SHA256 = "41889edb9c468ea62ee4641328c0e6f4bac2c618b81da751eebd2af4c05f648d"


class ContractViolation(ValueError):
    """Rejet motivé (jamais de correction silencieuse), portant règle et champ."""

    def __init__(self, rule: str, field_name: str, detail: str) -> None:
        self.rule = rule
        self.field_name = field_name
        super().__init__(f"REJET {rule} — champ '{field_name}' : {detail}")


def _valid_ymd(year: int, month: int, day: int) -> bool:
    if not (1 <= month <= 12):
        return False
    _, max_day = calendar.monthrange(year, month)
    return 1 <= day <= max_day


def parse_iso8601_utc(value: Any, rule: str = "V4", field_name: str = "observed_at") -> dt.datetime:
    """Parse une date ISO-8601 avec offset timezone explicite (Z ou ±HH:MM)."""
    if not isinstance(value, str) or not value.strip():
        raise ContractViolation(rule, field_name, "horodatage ISO-8601 vide")
    norm = value.strip()
    if norm.endswith("Z"):
        norm = norm[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(norm)
    except ValueError as exc:
        raise ContractViolation(rule, field_name, f"format ISO-8601 invalide: {value}") from exc
    if parsed.tzinfo is None:
        raise ContractViolation(rule, field_name, f"offset timezone obligatoire: {value}")
    return parsed.astimezone(dt.timezone.utc)


def verify_frozen_enonce(repo_root: Path) -> str:
    """Vérifie que FUSION-ENONCE.md existe et correspond exactement au SHA-256 gelé."""
    enonce_path = repo_root / ENONCE_RELATIVE_PATH
    if not enonce_path.exists():
        raise ContractViolation("M2", "enonce", f"ÉNONCÉ absent: {enonce_path}")
    digest = hashlib.sha256(enonce_path.read_bytes()).hexdigest().lower()
    if digest != ENONCE_EXPECTED_SHA256:
        raise ContractViolation(
            "M2",
            "enonce_sha256",
            f"ÉNONCÉ modifié: attendu={ENONCE_EXPECTED_SHA256}, observé={digest}",
        )
    return digest


# =============================================================================
# C1 — EVENT JOURNAL (fondation-13-1/src/router.rs : R1 -> R8)
# =============================================================================

class EventJournal:
    """Journal d'événements append-only conforme à fondation-13-1/src/router.rs."""

    def __init__(self, signed_designs: Optional[set[str]] = None) -> None:
        self.records: List[Dict[str, Any]] = []
        self.signed_designs = signed_designs or set()
        self.event_ids: set[str] = set()
        self.typed: set[str] = set()
        self.requested: set[str] = set()

    @classmethod
    def from_jsonl(cls, text: str, signed_designs: Optional[set[str]] = None) -> "EventJournal":
        import json

        j = cls(signed_designs=signed_designs)
        for line in text.splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            j.records.append(obj)
            eid = str(obj.get("event_id", ""))
            did = str(obj.get("dispatch_id", ""))
            typ = str(obj.get("type", ""))
            if eid:
                j.event_ids.add(eid)
            if typ == "dispatch_typed":
                j.typed.add(did)
            elif typ == "judgment_requested":
                j.requested.add(did)
        return j

    def validate_dispatch(
        self, raw_submission: Dict[str, Any], now_utc: Optional[dt.datetime] = None
    ) -> Dict[str, Any]:
        """Applique R1 -> R2 -> R3 -> R4 -> R5 -> R6 -> R7 -> R8 sans correction silencieuse."""
        if not isinstance(raw_submission, dict):
            raise ContractViolation("R1", "(dispatch)", "le dispatch doit être un objet JSON")
        if sorted(raw_submission.keys()) != sorted(DISPATCH_KEYS):
            missing = sorted(set(DISPATCH_KEYS) - set(raw_submission.keys()))
            unknown = sorted(set(raw_submission.keys()) - set(DISPATCH_KEYS))
            raise ContractViolation(
                "R1", "(clés)", f"manquantes={missing} ; inconnues={unknown}"
            )

        for k in ("event_id", "type", "dispatch_id", "actor_from", "actor_to", "at", "design_ref", "payload"):
            if not isinstance(raw_submission[k], str):
                raise ContractViolation("R1", k, "le champ doit être une chaîne")

        proof = raw_submission["proof"]
        if not isinstance(proof, list) or not all(isinstance(p, str) for p in proof):
            raise ContractViolation("R7", "proof", "proof doit être une liste de chaînes")

        event_id = raw_submission["event_id"]
        typ = raw_submission["type"]
        dispatch_id = raw_submission["dispatch_id"]
        actor_from = raw_submission["actor_from"]
        actor_to = raw_submission["actor_to"]
        at = raw_submission["at"]
        design_ref = raw_submission["design_ref"]
        payload = raw_submission["payload"]

        # R2 — Design signé référencé
        if not design_ref.strip():
            raise ContractViolation("R2", "design_ref", "aucun design signé référencé")
        if self.signed_designs and design_ref not in self.signed_designs:
            raise ContractViolation("R2", "design_ref", f"design non signé: {design_ref}")

        # R3 — event_id EVT-AAAAMMJJ-NNN et unicité
        m_evt = EVENT_ID_RE.match(event_id)
        if not m_evt or not _valid_ymd(int(m_evt.group(1)), int(m_evt.group(2)), int(m_evt.group(3))):
            raise ContractViolation("R3", "event_id", "event_id doit avoir la forme EVT-AAAAMMJJ-NNN")
        if event_id in self.event_ids:
            raise ContractViolation("R3", "event_id", f"event_id déjà inscrit: {event_id}")
        if typ == "dispatch_typed" and dispatch_id in self.typed:
            raise ContractViolation("R3", "dispatch_id", f"dispatch_id déjà typé: {dispatch_id}")

        # R4 — actor_from et actor_to dans FUNCTIONS_13 (jamais une session)
        if actor_to not in FUNCTIONS_13:
            raise ContractViolation("R4", "actor_to", f"doit appartenir à FUNCTIONS_13, reçu: {actor_to}")
        if actor_from not in FUNCTIONS_13:
            raise ContractViolation("R4", "actor_from", f"doit appartenir à FUNCTIONS_13, reçu: {actor_from}")

        # R5 — at ISO-8601 avec offset, pas dans le futur
        at_dt = parse_iso8601_utc(at, rule="R5", field_name="at")
        ref_now = (now_utc or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
        if at_dt > ref_now + dt.timedelta(seconds=5):
            raise ContractViolation("R5", "at", "at est dans le futur")

        # R6 — payload nomme l'acte (au moins 2 mots)
        if len(payload.split()) < 2:
            raise ContractViolation("R6", "payload", "payload doit nommer l'acte (>= 2 mots)")

        # R7 — proof[] non vide pour dispatch_ack et judgment_rendered
        if typ in ("dispatch_ack", "judgment_rendered") and (
            not proof or any(not p.strip() for p in proof)
        ):
            raise ContractViolation("R7", "proof", f"proof[] non vide requis pour {typ}")

        # R8 — type connu et transition légale
        if typ not in EVENT_TYPES:
            raise ContractViolation("R8", "type", f"type inconnu: {typ}")
        if typ == "dispatch_relayed" and dispatch_id not in self.typed and dispatch_id not in self.requested:
            raise ContractViolation("R8", "dispatch_id", "dispatch_relayed sans dispatch_typed ni judgment_requested")
        if typ == "dispatch_ack" and dispatch_id not in self.typed:
            raise ContractViolation("R8", "dispatch_id", "dispatch_ack sans dispatch_typed préalable")
        if typ == "judgment_rendered" and dispatch_id not in self.requested:
            raise ContractViolation("R8", "dispatch_id", "judgment_rendered sans judgment_requested préalable")

        return dict(raw_submission)

    def inscribe(self, raw_submission: Dict[str, Any], now_utc: Optional[dt.datetime] = None) -> Dict[str, Any]:
        """Valide R1..R8 puis inscrit l'événement avec seq = len + 1."""
        valid = self.validate_dispatch(raw_submission, now_utc=now_utc)
        record = dict(valid)
        record["seq"] = len(self.records) + 1
        self.records.append(record)
        self.event_ids.add(record["event_id"])
        if record["type"] == "dispatch_typed":
            self.typed.add(record["dispatch_id"])
        elif record["type"] == "judgment_requested":
            self.requested.add(record["dispatch_id"])
        return record


# =============================================================================
# C2 — R10 RECEIPT LEDGER (fondation-13-1/src/lib.rs : V1 -> V8 -> V7 -> V2..V6)
# =============================================================================

class R10Ledger:
    """Validateur & consignateur R10 v1 aligné sur fondation-13-1/src/lib.rs."""

    def __init__(self, valid_shas: Optional[set[str]] = None) -> None:
        self.entry_ids: set[str] = set()
        self.mission_ids: set[str] = set()
        self.entries: Dict[str, Dict[str, Any]] = {}
        self.valid_shas = valid_shas

    def validate_and_consign(
        self, deposit: Dict[str, Any], now_utc: Optional[dt.datetime] = None
    ) -> Dict[str, Any]:
        """Applique V1 -> V8 -> V7 -> V2 -> V3 -> V4 -> V5 -> V6 et pose recorded_at UTC."""
        # V1 — Exactement les 9 clés R10_KEYS
        if not isinstance(deposit, dict):
            raise ContractViolation("V1", "(dépôt)", "le dépôt doit être un objet JSON")
        if sorted(deposit.keys()) != sorted(R10_KEYS):
            missing = sorted(set(R10_KEYS) - set(deposit.keys()))
            unknown = sorted(set(deposit.keys()) - set(R10_KEYS))
            raise ContractViolation("V1", "(clés)", f"manquantes={missing} ; inconnues={unknown}")

        # V8 — schema exact
        schema = deposit["schema"]
        if schema != R10_SCHEMA:
            raise ContractViolation("V8", "schema", f"attendu '{R10_SCHEMA}', reçu '{schema}'")

        # V7 — entry_id G-AAAAMMJJ-NNN, date valide et non réécrit
        entry_id = deposit["entry_id"]
        if not isinstance(entry_id, str):
            raise ContractViolation("V7", "entry_id", "doit être une chaîne G-AAAAMMJJ-NNN")
        m_ent = ENTRY_ID_RE.match(entry_id)
        if not m_ent or not _valid_ymd(int(m_ent.group(1)), int(m_ent.group(2)), int(m_ent.group(3))):
            raise ContractViolation("V7", "entry_id", f"forme invalide: {entry_id}")
        if entry_id in self.entry_ids:
            raise ContractViolation("V7", "entry_id", f"entry_id déjà consigné (jamais réécrit): {entry_id}")

        # V2 — mission_id non vide et unique
        mission_id = deposit["mission_id"]
        if not isinstance(mission_id, str) or not mission_id.strip():
            raise ContractViolation("V2", "mission_id", "mission_id vide")
        if mission_id in self.mission_ids:
            raise ContractViolation("V2", "mission_id", f"mission_id déjà consigné: {mission_id}")

        # V3 — sha 40 hex [0-9a-f] résolvant
        sha = deposit["sha"]
        if not isinstance(sha, str) or not SHA40_RE.match(sha):
            raise ContractViolation("V3", "sha", f"SHA court ou mal formé (40 hex requis): {sha}")
        if self.valid_shas is not None and sha not in self.valid_shas:
            raise ContractViolation("V3", "sha", f"SHA non résolu: {sha}")

        # V4 — observed_at ISO-8601 avec offset, pas dans le futur
        obs_dt = parse_iso8601_utc(deposit["observed_at"], rule="V4", field_name="observed_at")
        rec_dt = (now_utc or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
        if obs_dt > rec_dt + dt.timedelta(seconds=5):
            raise ContractViolation("V4", "observed_at", "observed_at est dans le futur")

        # V5 — proof[] non vide de chaînes non vides
        proof = deposit["proof"]
        if not isinstance(proof, list) or not proof or not all(isinstance(p, str) and p.strip() for p in proof):
            raise ContractViolation("V5", "proof", "proof doit être une liste non vide de chaînes non vides")

        # V6 — summary non vide nommant un livrable (#PR ou SHA >= 7 hex) ; issuer non vide
        issuer = deposit["issuer"]
        if not isinstance(issuer, str) or not issuer.strip():
            raise ContractViolation("V6", "issuer", "issuer ne peut pas être vide")
        summary = deposit["summary"]
        if not isinstance(summary, str) or not summary.strip():
            raise ContractViolation("V6", "summary", "summary ne peut pas être vide")
        if not DELIVERABLE_RE.search(summary):
            raise ContractViolation("V6", "summary", "summary doit nommer un livrable (#PR ou SHA >= 7 hex)")

        stored = dict(deposit)
        stored["recorded_at"] = rec_dt.isoformat()
        self.entry_ids.add(entry_id)
        self.mission_ids.add(mission_id)
        self.entries[entry_id] = stored
        return stored


# =============================================================================
# C3 — EPISTEMIC CITATION (fondation-13-1/src/memory.rs : M1 -> M7 -> M2..M8)
# =============================================================================

@dataclass
class CitationEvidence:
    source_exists: bool
    source_line_text: str
    source_date: str
    corroborations: List[Tuple[str, str, str]] = field(default_factory=list)
    planted_fautif: Optional[Tuple[str, str, str]] = None


def _section_named(text: str, keyword: str) -> str:
    lines = text.splitlines()
    start = None
    end = len(lines)
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            if start is not None:
                end = i
                break
            if keyword in ln[3:]:
                start = i
    return "\n".join(lines[start:end]) if start is not None else ""


def _field_in(section: str, marker: str) -> Optional[str]:
    for ln in section.splitlines():
        if ln.startswith(marker):
            return ln[len(marker) :].strip()
    return None


def _denied_before(text: str, idx: int) -> bool:
    line_start = text.rfind("\n", 0, idx) + 1
    before = text[line_start:idx]
    return any(tok in before for tok in DENIAL_TOKENS)


def validate_citation(citation_md: str, evidence: CitationEvidence) -> Dict[str, str]:
    """Implémente M1 -> M7 -> M2 -> M3 -> M4 -> M5 -> M6 -> M8 de memory.rs."""
    # M1 — En-tête + Citation + 4 sections
    for marker in ("**Fonction :**", "**Date de la citation :**", "**Fait demandé :**", "**Mécanisme :**"):
        if marker not in citation_md:
            raise ContractViolation("M1", "en-tête", f"marqueur manquant: {marker}")

    sec_cit = _section_named(citation_md, "Citation")
    if not sec_cit:
        raise ContractViolation("M1", "citation", "section Citation absente")
    statement = _field_in(sec_cit, "**Énoncé :**")
    source = _field_in(sec_cit, "**Source :**")
    date_val = _field_in(sec_cit, "**Date :**")
    status = _field_in(sec_cit, "**Statut :**")
    for fn, val in (("énoncé", statement), ("source", source), ("date", date_val), ("statut", status)):
        if val is None or not val:
            raise ContractViolation("M1", fn, f"champ {fn} manquant")

    for req_sec in (
        "Vérification au fichier",
        "Corroborations et contradictions",
        "Ce que cette citation ne prouve pas",
        "Ce que la fonction n'a pas fait",
    ):
        if not _section_named(citation_md, req_sec):
            raise ContractViolation("M1", "section", f"section '{req_sec}' absente")

    # M7 — La mémoire ne juge pas
    sec_not_done = _section_named(citation_md, "Ce que la fonction n'a pas fait")
    if not [ln for ln in sec_not_done.splitlines()[1:] if ln.strip()]:
        raise ContractViolation("M7", "ce que la fonction n'a pas fait", "section vide")
    lowered = citation_md.lower()
    for jm in JUDGMENT_MARKERS:
        pos = 0
        while True:
            idx = lowered.find(jm, pos)
            if idx == -1:
                break
            if not _denied_before(lowered, idx):
                raise ContractViolation("M7", "jugement", f"marqueur non nié: {jm}")
            pos = idx + len(jm)

    # M2 — Source exacte = source vérifiée
    sec_verif = _section_named(citation_md, "Vérification au fichier")
    if status == "absent":
        if evidence.source_exists:
            raise ContractViolation("M2", "source", "statut 'absent' mais source existante")
        if not any(tok in sec_verif for tok in ("absent", "0 octet", "perdue")):
            raise ContractViolation("M2", "vérification", "absence non nommée dans Vérification")
    else:
        if not evidence.source_exists:
            raise ContractViolation("M2", "source", f"source citée inexistante: {source}")
        norm_line = " ".join(evidence.source_line_text.split())
        norm_stmt = " ".join(statement.split())
        if norm_stmt not in norm_line:
            raise ContractViolation("M2", "énoncé", "énoncé absent de la ligne source relue")

    # M3 — Date portée par la source
    if date_val != "inconnue":
        if (
            date_val not in evidence.source_line_text
            and evidence.source_date != date_val
            and date_val not in evidence.source_date
        ):
            raise ContractViolation("M3", "date", f"date '{date_val}' non portée par la source ({evidence.source_date})")

    # M4 — Statut dans les 6 autorisés & contraintes temporelles
    if status not in EPISTEMIC_STATUSES:
        raise ContractViolation("M4", "statut", f"statut invalide: {status}")
    if status == "contredit" and not evidence.corroborations:
        raise ContractViolation("M4", "statut", "statut 'contredit' sans corroborations")
    if status in ("à venir", "périmé"):
        if len(date_val) < 10 or not re.match(r"^\d{4}-\d{2}-\d{2}", date_val):
            raise ContractViolation("M4", "date", f"statut temporel '{status}' exige une date AAAA-MM-JJ")
        cit_line = _field_in(citation_md, "**Date de la citation :**") or ""
        m_today = re.search(r"(\d{4}-\d{2}-\d{2})", cit_line)
        if not m_today:
            raise ContractViolation("M4", "date de la citation", "date de citation introuvable")
        cited_d, today_d = date_val[:10], m_today.group(1)
        if status == "à venir" and cited_d <= today_d:
            raise ContractViolation("M4", "date", f"statut 'à venir' mais {cited_d} <= {today_d}")
        if status == "périmé":
            if cited_d >= today_d:
                raise ContractViolation("M4", "date", f"statut 'périmé' mais {cited_d} >= {today_d}")
            if not any(mk in sec_verif for mk in MOVED_MARKERS):
                raise ContractViolation("M4", "vérification", "déplacement non nommé pour statut 'périmé'")

    # M5 — Contradiction portée
    sec_corr = _section_named(citation_md, "Corroborations et contradictions")
    diverging = [cd for _, cd, _ in evidence.corroborations if cd != date_val]
    if diverging:
        if status != "contredit":
            raise ContractViolation("M5", "statut", f"corroboration divergente ({diverging}) impose statut 'contredit'")
        for d in diverging:
            if d not in sec_corr:
                raise ContractViolation("M5", "corroborations", f"date divergente '{d}' non listée")

    # M6 — Fautif planté rejeté
    if evidence.planted_fautif and (statement, source, date_val) == evidence.planted_fautif:
        raise ContractViolation("M6", "fait cité", "le fait cité est le fautif planté")

    # M8 — Limites nommées
    sec_lim = _section_named(citation_md, "Ce que cette citation ne prouve pas")
    if not [ln for ln in sec_lim.splitlines()[1:] if ln.strip()]:
        raise ContractViolation("M8", "limites", "section 'Ce que cette citation ne prouve pas' vide")

    return {"statement": statement, "source": source, "date": date_val, "status": status}


# =============================================================================
# C4 — REGISTRE L0 D'INTERCONNEXION DES 5 NOYAUX (K1..K5)
# =============================================================================

@dataclass
class FoundationKernelRegistry:
    """Fédère les 5 Noyaux K1..K5 sur les contrats L0 exacts de fondation-13-1."""

    repo_root: Path
    journal: EventJournal
    ledger: R10Ledger
    capabilities_owner: Dict[str, str] = field(default_factory=dict)
    kernel_receipts: Dict[str, List[str]] = field(default_factory=lambda: {k: [] for k in KERNEL_IDS})

    def register_capability(self, kernel: str, fiber_id: str, capability: str) -> None:
        if kernel not in KERNEL_IDS:
            raise ContractViolation("C4", "kernel", f"Noyau inconnu: {kernel}")
        if capability in self.capabilities_owner and self.capabilities_owner[capability] != fiber_id:
            raise ContractViolation(
                "C4",
                "capability",
                f"capacité '{capability}' déjà détenue par {self.capabilities_owner[capability]}",
            )
        self.capabilities_owner[capability] = fiber_id

    def record_kernel_action(
        self,
        kernel: str,
        dispatch_submission: Dict[str, Any],
        r10_deposit: Dict[str, Any],
        now_utc: Optional[dt.datetime] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if kernel not in KERNEL_IDS:
            raise ContractViolation("C4", "kernel", f"Noyau inconnu: {kernel}")
        evt = self.journal.inscribe(dispatch_submission, now_utc=now_utc)
        rec = self.ledger.validate_and_consign(r10_deposit, now_utc=now_utc)
        self.kernel_receipts[kernel].append(rec["entry_id"])
        return evt, rec

    def verify_all_kernels_connected(self) -> Dict[str, int]:
        counts = {k: len(v) for k, v in self.kernel_receipts.items()}
        missing = [k for k, c in counts.items() if c == 0]
        if missing:
            raise ContractViolation("C4", "kernels", f"Noyaux sans acte L0 vérifié: {missing}")
        return counts
