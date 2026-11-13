//! Suite du routeur (D-N055 F1-3, H-M3).
//!
//! Cas passants : un dispatch valide typé, relayé, accusé ; une demande de
//! jugement puis un jugement rendu ; une pulsation ; la reconstruction du
//! journal depuis le JSONL. Cas rejetés : les 5 fautifs du Discover §6
//! (raisons nommées R2, R3, R4, R5, R8) — dont le dispatch fautif planté
//! n° 1 (sans design signé, D-F1-3-6, amendement A-F1-3-1).
//!
//! L'horloge de référence des tests est fixe (2026-11-11T02:00:00Z) :
//! les `at` des cas passants sont antérieurs, celui du fautif n° 4 est
//! non ISO (rejet R5 sur la forme, pas sur le futur).

use r10_validator::router::{
    inscribe, validate_dispatch, Journal, StaticDesignResolver, EVENT_TYPES,
};
use r10_validator::{parse_iso8601_offset, parse_json};

const NOW: i64 = 1794380400; // 2026-11-11T07:00:00Z.
const DESIGN: &str = "plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)";

fn designs() -> StaticDesignResolver {
    StaticDesignResolver::new([DESIGN.to_string()])
}

fn dispatch_valid(event: &str, typ: &str, dispatch: &str) -> String {
    format!(
        r#"{{"event_id":"{}","type":"{}","dispatch_id":"{}","actor_from":"router","actor_to":"executor","at":"2026-11-11T01:55:00-05:00","design_ref":"{}","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}}"#,
        event, typ, dispatch, DESIGN
    )
}

fn journal_empty() -> Journal {
    Journal::default()
}

#[test]
fn dispatch_valide_type() {
    let journal = journal_empty();
    let d = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let valid = validate_dispatch(&d, &journal, &designs(), NOW).unwrap();
    assert_eq!(valid.dispatch_id, "D-N055-F1-3-DELIVER");
    assert_eq!(valid.typ, "dispatch_typed");
}

#[test]
fn inscription_assigne_seq_1() {
    let journal = journal_empty();
    let d = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let line = inscribe(&d, &journal, &designs(), NOW).unwrap();
    let back = parse_json(&line).unwrap();
    assert_eq!(back.get("seq").unwrap().to_compact(), "1");
    assert_eq!(back.get("event_id").unwrap().as_str(), Some("EVT-20261111-001"));
}

#[test]
fn chaine_typee_relayee_accusee() {
    let mut text = String::new();
    let designs = designs();
    // 1 — typage.
    let d1 = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let j0 = Journal::from_jsonl(&text).unwrap();
    let l1 = inscribe(&d1, &j0, &designs, NOW).unwrap();
    text.push_str(&l1);
    text.push('\n');
    // 2 — relais.
    let d2 = parse_json(&dispatch_valid("EVT-20261111-002", "dispatch_relayed", "D-N055-F1-3-DELIVER")).unwrap();
    let j1 = Journal::from_jsonl(&text).unwrap();
    assert_eq!(j1.next_seq(), 2);
    let l2 = inscribe(&d2, &j1, &designs, NOW).unwrap();
    text.push_str(&l2);
    text.push('\n');
    // 3 — accusé (preuve non vide exigée, R7).
    let d3 = parse_json(r#"{"event_id":"EVT-20261111-003","type":"dispatch_ack","dispatch_id":"D-N055-F1-3-DELIVER","actor_from":"executor","actor_to":"router","at":"2026-11-11T01:58:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Accuser réception du dispatch de livraison F1-3","proof":["PR F1-3 ouverte, tête <sha>, vérifiée à l'API"]}"#).unwrap();
    let j2 = Journal::from_jsonl(&text).unwrap();
    let l3 = inscribe(&d3, &j2, &designs, NOW).unwrap();
    let back = parse_json(&l3).unwrap();
    assert_eq!(back.get("seq").unwrap().to_compact(), "3");
    assert_eq!(back.get("type").unwrap().as_str(), Some("dispatch_ack"));
}

#[test]
fn jugement_demande_puis_rendu() {
    let mut text = String::new();
    let designs = designs();
    let dq = parse_json(r#"{"event_id":"EVT-20261111-004","type":"judgment_requested","dispatch_id":"D-N055-F1-3-JUDGE","actor_from":"router","actor_to":"judge","at":"2026-11-11T01:59:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Demander le jugement de la PR F1-3","proof":[]}"#).unwrap();
    let j0 = Journal::from_jsonl(&text).unwrap();
    text.push_str(&inscribe(&dq, &j0, &designs, NOW).unwrap());
    text.push('\n');
    let dr = parse_json(r#"{"event_id":"EVT-20261111-005","type":"judgment_rendered","dispatch_id":"D-N055-F1-3-JUDGE","actor_from":"judge","actor_to":"router","at":"2026-11-11T01:59:30-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Rendre le jugement de la PR F1-3","proof":["PR vérifiée à l'API : tête, checks, parents"]}"#).unwrap();
    let j1 = Journal::from_jsonl(&text).unwrap();
    let line = inscribe(&dr, &j1, &designs, NOW).unwrap();
    assert_eq!(parse_json(&line).unwrap().get("seq").unwrap().to_compact(), "2");
}

#[test]
fn pulsation_valide() {
    let journal = journal_empty();
    let d = parse_json(r#"{"event_id":"EVT-20261111-006","type":"pulse","dispatch_id":"D-N055-F1-3-PULSE-001","actor_from":"router","actor_to":"receiver","at":"2026-11-11T01:57:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Pulser la chaîne F1-3 après le typage","proof":[]}"#).unwrap();
    assert!(validate_dispatch(&d, &journal, &designs(), NOW).is_ok());
}

#[test]
fn correction_reference_un_evenement_existant() {
    let mut text = String::new();
    let designs = designs();
    let d1 = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let j0 = Journal::from_jsonl(&text).unwrap();
    text.push_str(&inscribe(&d1, &j0, &designs, NOW).unwrap());
    text.push('\n');
    let dc = parse_json(r#"{"event_id":"EVT-20261111-007","type":"correction","dispatch_id":"D-N055-F1-3-DELIVER","actor_from":"router","actor_to":"receiver","at":"2026-11-11T01:59:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Corriger le pointage : corrige EVT-20261111-001","proof":["ligne relue au journal"]}"#).unwrap();
    let j1 = Journal::from_jsonl(&text).unwrap();
    assert!(validate_dispatch(&dc, &j1, &designs, NOW).is_ok());
}

#[test]
fn fautif_1_sans_design_signe_rejete_r2() {
    // Dispatch fautif planté (D-F1-3-6, amendement A-F1-3-1) : valide à
    // tous autres égards, design_ref absent — rejet attendu R2.
    let d = parse_json(r#"{"event_id":"EVT-20261111-901","type":"dispatch_typed","dispatch_id":"D-N055-F1-3-FAUTIF-1","actor_from":"router","actor_to":"executor","at":"2026-11-11T01:55:00-05:00","design_ref":"","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R2");
    assert_eq!(err.field, "design_ref");
}

#[test]
fn fautif_1_bis_design_inconnu_rejete_r2() {
    let d = parse_json(r#"{"event_id":"EVT-20261111-902","type":"dispatch_typed","dispatch_id":"D-N055-F1-3-FAUTIF-1B","actor_from":"router","actor_to":"executor","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-INEXISTANT.md","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R2");
}

#[test]
fn fautif_2_double_envoi_rejete_r3() {
    let designs = designs();
    let d1 = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let j0 = journal_empty();
    let l1 = inscribe(&d1, &j0, &designs, NOW).unwrap();
    let j1 = Journal::from_jsonl(&l1).unwrap();
    // Même dispatch_id, nouvel event_id : re-typographie interdite.
    let d2 = parse_json(&dispatch_valid("EVT-20261111-002", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let err = validate_dispatch(&d2, &j1, &designs, NOW).unwrap_err();
    assert_eq!(err.rule, "R3");
    assert_eq!(err.field, "dispatch_id");
}

#[test]
fn fautif_2_bis_event_id_reutilise_rejete_r3() {
    let designs = designs();
    let d1 = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-DELIVER")).unwrap();
    let j0 = journal_empty();
    let l1 = inscribe(&d1, &j0, &designs, NOW).unwrap();
    let j1 = Journal::from_jsonl(&l1).unwrap();
    let d2 = parse_json(&dispatch_valid("EVT-20261111-001", "dispatch_typed", "D-N055-F1-3-AUTRE")).unwrap();
    let err = validate_dispatch(&d2, &j1, &designs, NOW).unwrap_err();
    assert_eq!(err.rule, "R3");
    assert_eq!(err.field, "event_id");
}

#[test]
fn fautif_3_destinataire_session_rejete_r4() {
    // Le garde-fou central : le 1 ne route jamais vers une session.
    let d = parse_json(r#"{"event_id":"EVT-20261111-903","type":"dispatch_typed","dispatch_id":"D-N055-F1-3-FAUTIF-3","actor_from":"router","actor_to":"Nardole","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R4");
    assert_eq!(err.field, "actor_to");
}

#[test]
fn fautif_3_bis_id_session_rejete_r4() {
    let d = parse_json(r#"{"event_id":"EVT-20261111-904","type":"dispatch_typed","dispatch_id":"D-N055-F1-3-FAUTIF-3B","actor_from":"router","actor_to":"ae7d36d1","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R4");
}

#[test]
fn fautif_4_at_non_iso_rejete_r5() {
    let d = parse_json(r#"{"event_id":"EVT-20261111-905","type":"dispatch_typed","dispatch_id":"D-N055-F1-3-FAUTIF-4","actor_from":"router","actor_to":"executor","at":"2026-11-11 01:55:00 EST","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R5");
    assert_eq!(err.field, "at");
}

#[test]
fn fautif_5_ack_sans_typed_rejete_r8() {
    let d = parse_json(r#"{"event_id":"EVT-20261111-906","type":"dispatch_ack","dispatch_id":"D-N055-F1-3-JAMAIS-TYPE","actor_from":"executor","actor_to":"router","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Accuser réception d'un dispatch jamais typé","proof":["aucune preuve"]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R8");
}

#[test]
fn fautif_5_bis_rendu_sans_demande_rejete_r8() {
    let d = parse_json(r#"{"event_id":"EVT-20261111-907","type":"judgment_rendered","dispatch_id":"D-N055-F1-3-JAMAIS-DEMANDE","actor_from":"judge","actor_to":"router","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Rendre un jugement jamais demandé","proof":["aucune preuve"]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R8");
}

#[test]
fn seq_soumis_rejete_r1() {
    // `seq` est assigné par le routeur à l'inscription — il ne peut pas
    // être dans la soumission (correction portée en avant, fiche §7).
    let d = parse_json(r#"{"seq":1,"event_id":"EVT-20261111-001","type":"dispatch_typed","dispatch_id":"D-N055-F1-3-DELIVER","actor_from":"router","actor_to":"executor","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Ouvrir la PR F1-3 sur a0/f1-3-router","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R1");
}

#[test]
fn fixtures_rejettent_avec_la_raison_nommee() {
    use std::fs;
    let base = format!(
        "{}/tests/fixtures",
        env!("CARGO_MANIFEST_DIR")
    );
    let load = |name: &str| {
        let text = fs::read_to_string(format!("{}/{}", base, name)).unwrap();
        parse_json(&text).unwrap()
    };
    // Cas passant : le dispatch valide.
    let d = load("dispatch-valid.json");
    assert!(validate_dispatch(&d, &journal_empty(), &designs(), NOW).is_ok());
    // Fautif planté n° 1 (D-F1-3-6) : sans design signé → R2.
    let f1 = load("dispatch-fautif-1.json");
    let e1 = validate_dispatch(&f1, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!((e1.rule, e1.field), ("R2", "design_ref"));
    // Fautif n° 3 : destinataire = session → R4.
    let f3 = load("dispatch-fautif-3.json");
    let e3 = validate_dispatch(&f3, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!((e3.rule, e3.field), ("R4", "actor_to"));
    // Fautif n° 4 : `at` non ISO → R5.
    let f4 = load("dispatch-fautif-4.json");
    let e4 = validate_dispatch(&f4, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!((e4.rule, e4.field), ("R5", "at"));
    // Fautif n° 5 : ack sans typed → R8.
    let f5 = load("dispatch-fautif-5.json");
    let e5 = validate_dispatch(&f5, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(e5.rule, "R8");
    // Fautif n° 2 : double-envoi — seulement contre un journal où
    // DELIVER est déjà typé → R3.
    let seeded = inscribe(&d, &journal_empty(), &designs(), NOW).unwrap();
    let j1 = Journal::from_jsonl(&seeded).unwrap();
    let f2 = load("dispatch-fautif-2.json");
    let e2 = validate_dispatch(&f2, &j1, &designs(), NOW).unwrap_err();
    assert_eq!((e2.rule, e2.field), ("R3", "dispatch_id"));
}

#[test]
fn relais_apres_demande_de_jugement() {
    // Correction portée en avant (fiche §7) : le relais suit tout acte de
    // création du dispatch — un typage ou une demande de jugement.
    let designs = designs();
    let dq = parse_json(r#"{"event_id":"EVT-20261111-004","type":"judgment_requested","dispatch_id":"D-N055-F1-3-JUDGE","actor_from":"router","actor_to":"judge","at":"2026-11-11T01:59:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Demander le jugement de la PR F1-3","proof":[]}"#).unwrap();
    let j0 = journal_empty();
    let l1 = inscribe(&dq, &j0, &designs, NOW).unwrap();
    let j1 = Journal::from_jsonl(&l1).unwrap();
    let dr = parse_json(r#"{"event_id":"EVT-20261111-005","type":"dispatch_relayed","dispatch_id":"D-N055-F1-3-JUDGE","actor_from":"router","actor_to":"judge","at":"2026-11-11T01:59:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Relayer la demande de jugement F1-3 à la fonction de jugement","proof":[]}"#).unwrap();
    assert!(validate_dispatch(&dr, &j1, &designs, NOW).is_ok());
}

#[test]
fn relais_sans_acte_prealable_rejete_r8() {
    let d = parse_json(r#"{"event_id":"EVT-20261111-908","type":"dispatch_relayed","dispatch_id":"D-N055-F1-3-JAMAIS-CREE","actor_from":"router","actor_to":"judge","at":"2026-11-11T01:55:00-05:00","design_ref":"plans/DESIGN-FONDATION-13-1-F1-3-PROJET.md (journal 806)","payload":"Relayer un dispatch jamais créé","proof":[]}"#).unwrap();
    let err = validate_dispatch(&d, &journal_empty(), &designs(), NOW).unwrap_err();
    assert_eq!(err.rule, "R8");
}

#[test]
fn iso_reference() {
    // 2026-11-11T01:55:00-05:00 = 2026-11-11T06:55:00Z.
    assert_eq!(
        parse_iso8601_offset("2026-11-11T01:55:00-05:00"),
        Some(1794380100)
    );
}

#[test]
fn onze_types_dont_vision_held() {
    // A-F1-8-3 : la F1-8 changeset porte la liste des types du routeur
    // à 11 (`vision_held`) ; le design F1-3 n'est pas réécrit.
    assert_eq!(EVENT_TYPES.len(), 11);
    assert!(EVENT_TYPES.contains(&"vision_held"));
    assert!(EVENT_TYPES.contains(&"fact_recalled"));
    assert!(EVENT_TYPES.contains(&"merge_executed"));
    assert!(EVENT_TYPES.contains(&"closure_pulse"));
    assert!(EVENT_TYPES.contains(&"judgment_rendered"));
    assert!(!EVENT_TYPES.contains(&"type_inconnu"));
}
