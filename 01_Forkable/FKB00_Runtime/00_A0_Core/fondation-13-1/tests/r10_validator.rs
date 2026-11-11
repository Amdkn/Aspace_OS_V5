//! Suite du validateur R10 v1 (H-M3, D-N055 F1-2).
//!
//! Cas passants : les dépôts 001, 002, 026 rejoués comme dépôts — ils
//! doivent passer (un rejet de l'un d'eux bloque la montée d'état, R5).
//! Cas rejetés : les 4 fautifs du Discover §6 — ils doivent être rejetés
//! avec la raison nommée (dont le dépôt fautif planté n° 1, SHA court).
//!
//! Les fixtures sont les reçus lus au fichier dans le ledger
//! (`anchor-*.json` = copies exactes) et les dépôts fautifs construits
//! depuis 002 avec les amendements A-F1-2-1 / A-F1-2-2 (entry_id +
//! mission_id FRAIS pour les fautifs n° 1, 2, 3 ; le n° 4 garde ceux
//! de 002). `ledger.json` = union des branches `work-dn*-ledger`
//! (66 entry_id, 59 mission_id) à l'instantané F1-2.
//!
//! Suite par la commande du daemon (`cargo test`), jamais par une
//! invocation nue.

use r10_validator::{
    consign, format_iso_utc, now_unix, parse_iso8601_offset, parse_json, validate, Ledger,
    ShaResolver, StaticShaResolver,
};
use std::collections::HashSet;

// SHA ancrés (Discover F1-2 §1) — les seuls que le résolveur de la suite
// connaît : ils résolvent (vérifiés à l'API dans le Discover).
const ANCHOR_SHAS: [&str; 3] = [
    "3cd41aa1035b1b74ebe15471a649a0383b8f5f94", // 001
    "22f374ddcce1e1231dac5ae99e71fb074cb7d0e7", // 002
    "e715312025903370422cb7bda50c66bf33a45b6f", // 026
];

fn resolver() -> StaticShaResolver {
    StaticShaResolver::new(ANCHOR_SHAS.iter().map(|s| s.to_string()))
}

/// Ledger de la suite, moins le dépôt sous test (l'état du ledger au
/// moment du dépôt : un reçu ne se valide pas contre lui-même).
fn ledger_without(entry_id: &str, mission_id: &str) -> Ledger {
    let mut ledger = Ledger::from_json(include_str!("fixtures/ledger.json")).unwrap();
    ledger.entry_ids.remove(entry_id);
    ledger.mission_ids.remove(mission_id);
    ledger
}

fn ledger_full() -> Ledger {
    Ledger::from_json(include_str!("fixtures/ledger.json")).unwrap()
}

fn deposit(text: &str) -> r10_validator::Json {
    parse_json(text).expect("fixture JSON valide")
}

/// Horloge de consignation de la suite : après tous les observed_at
/// ancrés (002 : 00:27:43 EST), avant l'heure réelle d'exécution.
fn now() -> i64 {
    parse_iso8601_offset("2026-11-11T00:45:00-05:00").unwrap()
}

// ---------------------------------------------------------------------------
// Cas passants — les 3 reçus ancrés rejoués comme dépôts (R5)
// ---------------------------------------------------------------------------

#[test]
fn anchor_001_passes() {
    let d = deposit(include_str!("fixtures/anchor-001.json"));
    let ledger = ledger_without("G-20261111-001", "RYAN-FAB-D-N055-001");
    let valid = validate(&d, &ledger, &resolver(), now()).expect("001 doit passer");
    assert_eq!(valid.entry_id, "G-20261111-001");
    assert_eq!(valid.sha, "3cd41aa1035b1b74ebe15471a649a0383b8f5f94");
}

#[test]
fn anchor_002_passes() {
    let d = deposit(include_str!("fixtures/anchor-002.json"));
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    let valid = validate(&d, &ledger, &resolver(), now()).expect("002 doit passer");
    assert_eq!(valid.entry_id, "G-20261111-002");
    assert_eq!(valid.sha, "22f374ddcce1e1231dac5ae99e71fb074cb7d0e7");
}

#[test]
fn anchor_026_passes() {
    let d = deposit(include_str!("fixtures/anchor-026.json"));
    let ledger = ledger_without("G-20261110-026", "RYAN-FAB-D-N052-004");
    let valid = validate(&d, &ledger, &resolver(), now()).expect("026 doit passer");
    assert_eq!(valid.entry_id, "G-20261110-026");
    assert_eq!(valid.sha, "e715312025903370422cb7bda50c66bf33a45b6f");
}

// ---------------------------------------------------------------------------
// Cas rejetés — les 4 fautifs du Discover §6 (H-M3)
// ---------------------------------------------------------------------------

#[test]
fn faulty_1_short_sha_rejected_v3() {
    // Dépôt fautif planté (D-F1-2-6, amendement A-F1-2-1) : identique à 002
    // sauf sha = 22f374d (7 car.) et entry_id + mission_id FRAIS.
    let d = deposit(include_str!("fixtures/depot-fautif-1.json"));
    let err = validate(&d, &ledger_full(), &resolver(), now()).expect_err("fautif 1 rejeté");
    assert_eq!(err.rule, "V3", "rejet attendu : V3, reçu : {}", err);
    assert_eq!(err.field, "sha");
    assert_eq!(err.received, "22f374d");
}

#[test]
fn faulty_2_non_iso_observed_at_rejected_v4() {
    // Amendement A-F1-2-2 : entry_id + mission_id FRAIS, observed_at non ISO.
    let d = deposit(include_str!("fixtures/depot-fautif-2.json"));
    let err = validate(&d, &ledger_full(), &resolver(), now()).expect_err("fautif 2 rejeté");
    assert_eq!(err.rule, "V4", "rejet attendu : V4, reçu : {}", err);
    assert_eq!(err.field, "observed_at");
    assert_eq!(err.received, "2026-11-11 00:27:43 EST");
}

#[test]
fn faulty_3_empty_proof_rejected_v5() {
    // Amendement A-F1-2-2 : entry_id + mission_id FRAIS, proof[] vide.
    let d = deposit(include_str!("fixtures/depot-fautif-3.json"));
    let err = validate(&d, &ledger_full(), &resolver(), now()).expect_err("fautif 3 rejeté");
    assert_eq!(err.rule, "V5", "rejet attendu : V5, reçu : {}", err);
    assert_eq!(err.field, "proof");
}

#[test]
fn faulty_4_rewrite_rejected_v7_and_v2() {
    // Garde-fou central : entry_id + mission_id de 002 — jamais réécrit.
    // Premier violé attendu : V7, V2 nommé aussi.
    let d = deposit(include_str!("fixtures/depot-fautif-4.json"));
    let err = validate(&d, &ledger_full(), &resolver(), now()).expect_err("fautif 4 rejeté");
    assert_eq!(err.rule, "V7", "rejet attendu : V7, reçu : {}", err);
    assert_eq!(err.field, "entry_id");
    assert_eq!(err.received, "G-20261111-002");
    assert!(
        err.also_violated.contains(&"V2"),
        "V2 doit être nommé aussi, reçu : {}",
        err
    );
}

// ---------------------------------------------------------------------------
// Règles une à une (couverture V1, V2, V3, V6, V8)
// ---------------------------------------------------------------------------

#[test]
fn v1_extra_key_rejected() {
    // Ajout d'une 10e clé (livrable — n'existe pas en R10 v1).
    let text = include_str!("fixtures/anchor-002.json").replace(
        "\"schema\":\"aspace.r10-receipt.v1\"",
        "\"schema\":\"aspace.r10-receipt.v1\",\"livrable\":\"PR #23\"",
    );
    let d = deposit(&text);
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    let err = validate(&d, &ledger, &resolver(), now()).expect_err("10 clés rejetées");
    assert_eq!(err.rule, "V1");
}

#[test]
fn v8_wrong_schema_rejected() {
    let text = include_str!("fixtures/anchor-002.json")
        .replace("aspace.r10-receipt.v1", "aspace.r10-receipt.v2");
    let d = deposit(&text);
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    let err = validate(&d, &ledger, &resolver(), now()).expect_err("schema v2 rejeté");
    assert_eq!(err.rule, "V8");
    assert_eq!(err.field, "schema");
}

#[test]
fn v2_duplicate_mission_rejected() {
    // entry_id frais, mais mission_id déjà consigné (celui de 002).
    let text = include_str!("fixtures/anchor-002.json").replace(
        "\"entry_id\":\"G-20261111-002\"",
        "\"entry_id\":\"G-20261111-904\"",
    );
    let d = deposit(&text);
    let err = validate(&d, &ledger_full(), &resolver(), now()).expect_err("mission dup rejetée");
    assert_eq!(err.rule, "V2");
    assert_eq!(err.field, "mission_id");
}

#[test]
fn v3_full_sha_that_does_not_resolve_rejected() {
    let text = include_str!("fixtures/anchor-002.json").replace(
        "22f374ddcce1e1231dac5ae99e71fb074cb7d0e7",
        "0000000000000000000000000000000000000000",
    );
    let d = deposit(&text);
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    let err = validate(&d, &ledger, &resolver(), now()).expect_err("SHA inconnu rejeté");
    assert_eq!(err.rule, "V3");
}

#[test]
fn v4_future_observed_at_rejected() {
    let text = include_str!("fixtures/anchor-002.json")
        .replace("2026-11-11T00:27:43-05:00", "2027-01-01T00:00:00-05:00");
    let d = deposit(&text);
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    let err = validate(&d, &ledger, &resolver(), now()).expect_err("futur rejeté");
    assert_eq!(err.rule, "V4");
}

#[test]
fn v6_summary_without_reference_rejected() {
    // Remplacement du summary entier (dernière clé du JSON) par un résumé
    // générique qui ne nomme ni PR ni SHA.
    let text = include_str!("fixtures/anchor-002.json");
    let marker = "\"summary\":\"";
    let start = text.find(marker).expect("summary présent");
    let head = &text[..start + marker.len()];
    let tail = "Dépôt Ryan consigné — travail terminé.\"}";
    let text = format!("{}{}", head, tail);
    let d = deposit(&text);
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    let err = validate(&d, &ledger, &resolver(), now()).expect_err("résumé générique rejeté");
    assert_eq!(err.rule, "V6");
    assert_eq!(err.field, "summary");
}

// ---------------------------------------------------------------------------
// Consignation — recorded_at posé par la fonction, jamais repris (D-F1-2-1)
// ---------------------------------------------------------------------------

#[test]
fn consign_stamps_recorded_at_from_clock() {
    let d = deposit(include_str!("fixtures/anchor-002.json"));
    let ledger = ledger_without("G-20261111-002", "RYAN-FAB-D-N055-002");
    // Horloge de consignation fixée : 2026-11-11T01:30:00-05:00.
    let at = now();
    let receipt = consign(&d, &ledger, &resolver(), at).expect("consignation");
    let out = parse_json(&receipt).unwrap();
    // recorded_at = l'horloge de consignation (UTC), pas celle du dépôt.
    assert_eq!(
        out.get("recorded_at").unwrap().as_str(),
        Some(format_iso_utc(at).as_str())
    );
    assert_ne!(
        out.get("recorded_at").unwrap().as_str(),
        Some("2026-11-11T00:29:00-05:00"),
        "recorded_at du dépôt ne doit jamais être repris"
    );
    // recorded_at >= observed_at (V4 + invariant R10-OK).
    let recorded = parse_iso8601_offset(out.get("recorded_at").unwrap().as_str().unwrap()).unwrap();
    let observed = parse_iso8601_offset(out.get("observed_at").unwrap().as_str().unwrap()).unwrap();
    assert!(recorded >= observed);
    // Les 9 clés, exactement.
    let mut keys: Vec<&str> = match &out {
        r10_validator::Json::Obj(pairs) => pairs.iter().map(|(k, _)| k.as_str()).collect(),
        _ => panic!("le reçu est un objet"),
    };
    keys.sort_unstable();
    assert_eq!(
        keys,
        vec![
            "entry_id", "issuer", "mission_id", "observed_at", "proof", "recorded_at", "schema",
            "sha", "summary"
        ]
    );
    // Les autres champs sont repris du dépôt validé.
    assert_eq!(out.get("sha").unwrap().as_str(), Some(ANCHOR_SHAS[1]));
    assert_eq!(
        out.get("entry_id").unwrap().as_str(),
        Some("G-20261111-002")
    );
}

#[test]
fn consign_rejects_faulty_deposit() {
    let d = deposit(include_str!("fixtures/depot-fautif-1.json"));
    let err = consign(&d, &ledger_full(), &resolver(), now()).expect_err("fautif 1 non consigné");
    assert_eq!(err.rule, "V3");
}

#[test]
fn ledger_fixture_covers_numbered_receipts() {
    // La fixture couvre les 41 reçus numérotés (11 + 26 + 4) et les 66
    // entry_id uniques mesurés à l'exécution (H-M1).
    let ledger = ledger_full();
    assert_eq!(ledger.entry_ids.len(), 66);
    assert_eq!(ledger.mission_ids.len(), 59);
    for id in ["G-20261111-001", "G-20261111-002", "G-20261111-003", "G-20261111-004"] {
        assert!(ledger.entry_ids.contains(id), "{} présent", id);
    }
    // Les SHA ancrés ne sont pas dans le résolveur de la suite par hasard :
    // ils résolvent (vérifiés à l'API dans le Discover).
    let r = resolver();
    for sha in ANCHOR_SHAS {
        assert!(r.resolves(sha), "{} résout", sha);
    }
    // L'horloge système réelle est après l'horloge de consignation de la
    // suite (00:45 EST) — les observed_at ancrés sont dans le passé.
    assert!(now_unix() > now());
}

#[test]
fn short_sha_prefix_of_real_commit_still_rejected() {
    // Leçon AGENTS.md 2026-11-10 : le court 422, le complet résout — le
    // rejet porte sur la forme, pas sur l'existence. 22f374d est le préfixe
    // du vrai merge 002 : il doit quand même être rejeté (V3).
    let mut known = HashSet::new();
    known.insert("22f374d".to_string());
    let r = StaticShaResolver::new(known);
    let text = include_str!("fixtures/depot-fautif-1.json");
    let d = deposit(text);
    let err = validate(&d, &ledger_full(), &r, now()).expect_err("court rejeté même si connu");
    assert_eq!(err.rule, "V3");
}
