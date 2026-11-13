//! Suite de la fonction Juger (D-N055 F1-5, H-M3).
//!
//! Cas passant : un jugement valide de la PR #44 (`jugement-valide.md` —
//! dossier de jugement réel, faits vérifiés à l'API par le jugement
//! F1-4 : tête `2d38798`, CI 8/8, suite 51/51) doit passer J1–J8.
//! Cas rejetés : les 5 fautifs du Discover §6, dérivés chacun par UNE
//! SEULE différence (un seul remplacement, vérifié `count == 1`) — ils
//! doivent être rejetés avec la raison nommée (J2, J3, J4, J5, J7), dont
//! la PR fautive plantée n° 1 (tête non autorisée, D-F1-5-4, amendement
//! A-F1-5-1). Cas limites : dossier sans rejet du fautif (J6), document
//! vide (J1), dossier sans limites nommées (J8), rouge exclu par le
//! coordinateur (J4, P-F1-5-4), type `closure_pulse` légal (A-F1-5-3).
//!
//! Les SHA complets du jugement sont résolus par le résolveur statique
//! (vérifiés à l'API par l'opérateur : tête PR #44 `2d38798…`, base
//! `96d64ce…`, merge PR #44 `573cad4…`).

use r10_validator::judge::{
    is_legal_event_type, validate_judgment, JudgmentEvidence,
};
use r10_validator::StaticShaResolver;

const BASE: &str = include_str!("fixtures/jugement-valide.md");

const HEAD: &str = "2d3879808cd165a449016372a8a8ed4e4af03ec3";
const BASE_SHA: &str = "96d64ce8c5fb7626a9a80ef1c5602bfb38b7f273";
const MERGE: &str = "573cad466fbc4c76da522ddaec893d54e6650907";

const CI: [(&str, &str); 8] = [
    ("CodeQL", "success"),
    ("Verify 01 Kernel Gates", "success"),
    ("Verify 02 Holons 578 QualityControl", "success"),
    ("Verify 03 Submodules EGM Harvester", "success"),
    ("Verify 04 Security OWASP RigInfinity", "success"),
    ("Deterministic Gate", "success"),
    ("S1-RICK & Reviewer-Security", "success"),
    ("Analyze (actions)", "success"),
];

fn resolver() -> StaticShaResolver {
    StaticShaResolver::new([HEAD, BASE_SHA, MERGE].iter().map(|s| s.to_string()))
}

fn evidence<'a>(resolver: &'a StaticShaResolver) -> JudgmentEvidence<'a> {
    JudgmentEvidence {
        head: HEAD,
        resolver,
        ci: &CI,
        suite_passed: 51,
        suite_failed: 0,
        suite_failed_names: &[],
        excluded: &[],
        planted_fault_rule: "J2",
    }
}

/// Dérive un fautif par UNE SEULE différence : un seul remplacement, dont
/// l'unicité est vérifiée (le fautif ne diffère du valide que là).
fn fautif(base: &str, needle: &str, replacement: &str) -> String {
    assert_eq!(
        base.matches(needle).count(),
        1,
        "le fautif doit porter UNE SEULE différence — ancre non unique : {}",
        needle
    );
    base.replacen(needle, replacement, 1)
}

#[test]
fn jugement_valide_passe_j1_j8() {
    let r = resolver();
    let ev = evidence(&r);
    let valid = validate_judgment(BASE, &ev).unwrap();
    assert_eq!(valid.pr, "44");
    assert_eq!(valid.verdict, "VALIDÉE");
    assert_eq!(valid.head, HEAD);
    assert_eq!(valid.shas_checked, 1);
}

#[test]
fn fautif_1_tete_non_autorisee_rejetee_j2() {
    // A-F1-5-1 : le verdict autorise l'ancienne tête (la base) alors que
    // la tête vérifiée a bougé — une signature en blanc.
    let f = fautif(
        BASE,
        "**Tête autorisée : `2d3879808cd165a449016372a8a8ed4e4af03ec3`**",
        "**Tête autorisée : `96d64ce8c5fb7626a9a80ef1c5602bfb38b7f273`**",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J2");
}

#[test]
fn fautif_2_ci_non_verte_rejetee_j3() {
    // Un check-run en échec dans le dossier, alors que le reçu affirme
    // le vert — le juge re-vérifie, le désaccord tranche en rejet.
    let f = fautif(
        BASE,
        "- Verify 01 Kernel Gates : success",
        "- Verify 01 Kernel Gates : failure",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J3");
}

#[test]
fn fautif_3_suite_rouge_sans_exclusion_rejetee_j4() {
    // Suite re-courue avec un rouge, sans décision d'exclusion du
    // coordinateur — le juge n'invente pas l'exclusion.
    let f = fautif(
        BASE,
        "**`cargo test` 51/51 PASS, 0 échec**",
        "**`cargo test` 50/51 PASS, 1 échec**",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J4");
}

#[test]
fn fautif_4_vert_repris_du_recit_rejete_j5() {
    // Seul « vert » = le PASS local du rapport de l'exécutant, logs de
    // rejeu absents — aucun fait sans ancre rejouable (J5 d'abord, J4
    // ensuite — A-F1-5-2).
    let f = fautif(
        BASE,
        "re-couru dans un clone frais, sur la tête vérifiée, chiffres re-comptés aux logs, sans reprendre le récit de l'exécutant",
        "d'après le rapport de l'exécutant, sans rejeu indépendant (logs absents)",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J5");
}

#[test]
fn fautif_5_jugement_qui_execute_rejete_j7() {
    // Un reçu consigné par ce jugement — le juge n'exécute pas.
    let f = fautif(
        BASE,
        "## Ce que ce jugement ne prouve pas",
        "## Ce que ce jugement ne prouve pas\n\n**Reçu consigné par ce jugement : G-20261112-901 (mission TEST-F1-5-FAUTIF-5).**",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J7");
}

#[test]
fn dossier_sans_rejet_du_fautif_rejete_j6() {
    // Le fautif planté n'est pas rejeté avec sa règle nommée — la
    // fonction n'a pas prouvé qu'elle juge.
    let f = fautif(
        BASE,
        "Fautif planté n° 1 (tête non autorisée) : REJET J2 par la CLI judge-pr (sortie 2) — la tête autorisée par le verdict fautif n'était pas la tête vérifiée à l'API. Les fautifs n° 2–5 sont rejetés J3, J4, J5 puis J4, J7.",
        "Fautif planté n° 1 (tête non autorisée) : non vérifié.",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J6");
}

#[test]
fn document_vide_rejete_j1() {
    let err = validate_judgment("", &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J1");
}

#[test]
fn dossier_sans_limites_rejete_j8() {
    let f = fautif(
        BASE,
        "## Ce que ce jugement ne prouve pas",
        "## Limites",
    );
    let err = validate_judgment(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "J8");
}

#[test]
fn rouge_exclu_par_le_coordinateur_passe_j4() {
    // P-F1-5-4 : un rouge bloque sauf exclusion décidée par le
    // coordinateur, liste exacte consignée, confirmée par le juge.
    let f = fautif(
        BASE,
        "**`cargo test` 51/51 PASS, 0 échec**",
        "**`cargo test` 50/51 PASS, 1 échec** — Exclusion décidée par le coordinateur, liste exacte : `fautif_3_suite_rouge` (rouge pré-existant, confirmé par le juge)",
    );
    let r = resolver();
    let ev = JudgmentEvidence {
        suite_passed: 50,
        suite_failed: 1,
        suite_failed_names: &["fautif_3_suite_rouge"],
        excluded: &["fautif_3_suite_rouge"],
        ..evidence(&r)
    };
    validate_judgment(&f, &ev).unwrap();
}

#[test]
fn closure_pulse_type_legal_pour_le_juge() {
    // A-F1-5-3 : `closure_pulse` est le 8e type du journal, légalisé
    // porté en avant — la fonction Juger l'accepte comme type légal.
    assert!(is_legal_event_type("closure_pulse"));
    assert!(is_legal_event_type("judgment_rendered"));
    assert!(!is_legal_event_type("type_inconnu"));
}
