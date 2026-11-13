//! Suite de la fonction Action (D-N055 F1-9, H-M3).
//!
//! Cas passants : les 4 cas d'essai du Discover §5.2 (T1 merge du pas
//! sans question ; T2 consignation du reçu H-F1-8 sans question ; T3
//! routage de la livraison sans question ; T4 ouverture de la PR sans
//! question — doivent passer A1–A8, ou être rendus NON POSÉS avec leur
//! absence consignée quand l'acte n'est pas encore posable à la
//! livraison : T1 jugement en attente, T2 merge en attente). Cas rejetés :
//! les 4 fautifs du Discover §5.3, dérivés chacun par UNE SEULE
//! différence (raisons nommées : A2 autorisation sans jugement / question
//! avec autorisation complète, A3 rapport sans preuve, A6 acte hors
//! autorisation), dont le fait fautif planté F-A1 (autorisation du design
//! F1-8, D-F1-9-6, amendement A-F1-9-1). Cas limites (§5.4) : (a)
//! autorisation ambiguë, (b) autorisation révoquée / tête périmée, (c)
//! action déjà faite, (d) action partiellement faite, (e) carte du
//! harness, (f) mauvais acteur — traités comme définis.
//!
//! Les cas sont construits en Rust (données injectées) — la CLI
//! `take-action` les rend depuis les fichiers ; le dossier fautif
//! (`fixtures/action-fautif-1.md`) est lu par `parse_case`, comme la
//! CLI le lit au fichier.

use r10_validator::action::{
    parse_case, validate_action, ActionCase, ActionOutcome, Authorization, Gates,
    PlantedFautif,
};
use r10_validator::parse_iso8601_offset;

const FAUTIF_1: &str = include_str!("fixtures/action-fautif-1.md");
const FAUTIF_2: &str = include_str!("fixtures/action-fautif-2.md");
const FAUTIF_3: &str = include_str!("fixtures/action-fautif-3.md");
const FAUTIF_4: &str = include_str!("fixtures/action-fautif-4.md");

/// Instant de référence des cas : 2026-11-13T04:00:00-05:00 — après la
/// signature du design F1-9 (03:40 EST), avant le jugement et le merge.
fn now() -> i64 {
    parse_iso8601_offset("2026-11-13T04:00:00-05:00").unwrap()
}

const LIMITES: &str = "O3 conservée ; action universelle hors périmètre ; semaine complète portée par F1-11";
const AUTH_DATE: &str = "2026-11-13T03:40:00-05:00";
const AUTH_SOURCE: &str = "plans/DESIGN-FONDATION-13-1-F1-9-PROJET.md (journal 941)";
const AUTH_AUTHOR: &str = "design F1-9 signé (fonction de design interne, Clara)";

fn gates_merge() -> Gates<'static> {
    Gates {
        design_signed: true,
        judgment_required: true,
        judgment_rendered: true,
        pre_checks_required: true,
        pre_checks_green: true,
        gate_suppressed: "",
        separation_ok: true,
    }
}

fn gates_no_judgment() -> Gates<'static> {
    Gates {
        design_signed: true,
        judgment_required: false,
        judgment_rendered: false,
        pre_checks_required: false,
        pre_checks_green: false,
        gate_suppressed: "",
        separation_ok: true,
    }
}

/// T1 après le merge : l'acte posé sans question, rapporté avec preuve.
fn t1_after_merge() -> ActionCase<'static> {
    ActionCase {
        dispatch_id: "D-N055-F1-9-MERGE",
        step: "F1-9",
        auth_step: "F1-9",
        act: "le merge de la PR F1-9",
        authorization: Authorization {
            act: "le merge de la PR F1-9",
            author: AUTH_AUTHOR,
            date: AUTH_DATE,
            source: AUTH_SOURCE,
        },
        authorization_ambiguous: false,
        gates: gates_merge(),
        question_asked: false,
        question: "",
        act_posed: true,
        reported_before_act: false,
        report: "merge exécuté — 0 question posée entre le jugement et l'appel",
        report_proof: "jugement rendu (judgment_rendered) ; pré-merge ACCEPTÉ E1–E5 ; appel gh pr merge N --merge ; merge commit 2 parents, DVG-01",
        out_of_scope: false,
        out_of_scope_kind: "",
        already_done: false,
        already_done_proof: "",
        partially_done: false,
        resume_point: "",
        harness_card_pending: false,
        authorization_revoked: false,
        head_stale: false,
        referred_to_judge: false,
        limits: LIMITES,
        claims_universal: false,
        planted_fautif: None,
    }
}

/// T1 à la livraison : le jugement n'est pas rendu, le merge n'est pas
/// posé — absence consignée, jamais ACCEPTÉ.
fn t1_pending() -> ActionCase<'static> {
    let mut case = t1_after_merge();
    case.gates.judgment_rendered = false;
    case.gates.pre_checks_green = false;
    case.act_posed = false;
    case.report = "action non posée — jugement en attente";
    case.report_proof =
        "journal-router.jsonl seq 48 (dernier événement merge_executed F1-8) ; aucun judgment_rendered pour D-N055-F1-9-MERGE au journal au moment du rendu";
    case
}

/// T2 à la livraison : le merge n'a pas eu lieu, le reçu n'est pas
/// consignable — absence consignée.
fn t2_pending() -> ActionCase<'static> {
    let mut case = t1_after_merge();
    case.dispatch_id = "D-N055-F1-9-RECEIPT";
    case.act = "la consignation du reçu H-F1-8";
    case.authorization.act = "la consignation du reçu H-F1-8";
    case.gates = gates_no_judgment();
    case.act_posed = false;
    case.report = "action non posée — merge en attente";
    case.report_proof =
        "journal-router.jsonl seq 48 ; aucun merge_executed pour D-N055-F1-9-MERGE au journal au moment du rendu";
    case
}

/// T3 : le routage de la livraison, posé en une passe, sans question.
fn t3_routed() -> ActionCase<'static> {
    let mut case = t1_after_merge();
    case.dispatch_id = "D-N055-F1-9-DELIVER";
    case.act = "le routage de la livraison";
    case.authorization.act = "le routage de la livraison";
    case.gates = gates_no_judgment();
    case.report = "dispatch_typed → dispatch_relayed → dispatch_ack, seq 49/50/51, même passe, 0 question";
    case.report_proof = "journal-router.jsonl seq 49, 50, 51";
    case
}

/// T4 : l'ouverture de la PR, sur le seul dispatch lu, sans question.
fn t4_pr_opened() -> ActionCase<'static> {
    let mut case = t1_after_merge();
    case.dispatch_id = "D-N055-F1-9-PR";
    case.act = "l'ouverture de la PR";
    case.authorization.act = "l'ouverture de la PR";
    case.gates = gates_no_judgment();
    case.report = "PR ouverte sur a0/f1-9-action, base 8d8542a, 0 question entre la lecture de l'événement et l'ouverture";
    case.report_proof = "PR vérifiée à l'API : mergeable true, mergeable_state clean, CI 8/8";
    case
}

fn assert_rejet(rule: &str, result: Result<ActionOutcome, r10_validator::Rejection>) {
    match result {
        Ok(outcome) => panic!(
            "attendu REJET {}, reçu {:?}",
            rule, outcome
        ),
        Err(rejection) => assert_eq!(rejection.rule, rule, "rejet : {}", rejection),
    }
}

fn assert_not_posed(result: Result<ActionOutcome, r10_validator::Rejection>, needle: &str) {
    match result {
        Ok(ActionOutcome::NotPosed { reason }) => {
            assert!(
                reason.contains(needle),
                "raison « {} » ne contient pas « {} »",
                reason, needle
            );
        }
        other => panic!("attendu NON POSÉE ({}), reçu {:?}", needle, other),
    }
}

// --- Cas passants : les 4 cas d'essai ---

#[test]
fn t1_apres_merge_accepte() {
    let outcome = validate_action(&t1_after_merge(), now()).unwrap();
    match outcome {
        ActionOutcome::Accepted(valid) => {
            assert_eq!(valid.dispatch_id, "D-N055-F1-9-MERGE");
        }
        other => panic!("attendu ACCEPTÉ, reçu {:?}", other),
    }
}

#[test]
fn t1_en_attente_non_posee() {
    assert_not_posed(
        validate_action(&t1_pending(), now()),
        "jugement en attente",
    );
}

#[test]
fn t2_en_attente_non_posee() {
    assert_not_posed(
        validate_action(&t2_pending(), now()),
        "merge en attente",
    );
}

#[test]
fn t3_routage_accepte() {
    let outcome = validate_action(&t3_routed(), now()).unwrap();
    assert!(matches!(outcome, ActionOutcome::Accepted(_)));
}

#[test]
fn t4_ouverture_pr_acceptee() {
    let outcome = validate_action(&t4_pr_opened(), now()).unwrap();
    assert!(matches!(outcome, ActionOutcome::Accepted(_)));
}

// --- Cas rejetés : les 4 fautifs ---

#[test]
fn f_a1_rejet_a2() {
    let data = parse_case(FAUTIF_1, "F-A1").unwrap();
    let planted = PlantedFautif {
        dispatch_id: "D-N055-F1-9-MERGE",
        expected_rule: "A2",
    };
    let case = data.as_case(Some(planted));
    let result = validate_action(&case, now());
    match &result {
        Err(rejection) => {
            assert_eq!(rejection.rule, "A2");
            assert!(
                rejection.detail.contains("sans jugement rendu"),
                "détail : {}",
                rejection.detail
            );
            assert!(
                rejection.detail.contains("le design F1-8 n'autorise pas le pas F1-9"),
                "détail : {}",
                rejection.detail
            );
        }
        Ok(outcome) => panic!("F-A1 doit être rejeté A2, reçu {:?}", outcome),
    }
    assert_rejet("A2", result);
}

#[test]
fn f_a2_question_avec_autorisation_complete_rejet_a2() {
    let mut case = t1_after_merge();
    case.question_asked = true;
    case.question = "puis-je merger ?";
    let result = validate_action(&case, now());
    match &result {
        Err(rejection) => assert!(
            rejection.detail.contains("l'autorisation est complète"),
            "détail : {}",
            rejection.detail
        ),
        Ok(outcome) => panic!("F-A2 doit être rejeté A2, reçu {:?}", outcome),
    }
    assert_rejet("A2", result);
}

#[test]
fn f_a3_rapport_sans_preuve_rejet_a3() {
    let mut case = t1_after_merge();
    case.report_proof = "";
    assert_rejet("A3", validate_action(&case, now()));
}

#[test]
fn f_a4_hors_autorisation_rejet_a6() {
    let mut case = t1_after_merge();
    case.out_of_scope = true;
    case.out_of_scope_kind = "dépense";
    let result = validate_action(&case, now());
    match &result {
        Err(rejection) => assert!(
            rejection.detail.contains("les mandats ne couvrent pas ces actes"),
            "détail : {}",
            rejection.detail
        ),
        Ok(outcome) => panic!("F-A4 doit être rejeté A6, reçu {:?}", outcome),
    }
    assert_rejet("A6", result);
}

// --- A1 / A4 / A7 / A8 ---

#[test]
fn a1_acte_non_nomme_rejet() {
    let mut case = t1_after_merge();
    case.authorization.act = "";
    assert_rejet("A1", validate_action(&case, now()));
}

#[test]
fn a1_date_non_iso_rejet() {
    let mut case = t1_after_merge();
    case.authorization.date = "2026-11-13 03:40:00 EST";
    assert_rejet("A1", validate_action(&case, now()));
}

#[test]
fn a1_date_future_rejet() {
    let mut case = t1_after_merge();
    case.authorization.date = "2026-11-14T03:40:00-05:00";
    assert_rejet("A1", validate_action(&case, now()));
}

#[test]
fn a4_design_non_signe_rejet() {
    let mut case = t1_after_merge();
    case.gates.design_signed = false;
    assert_rejet("A4", validate_action(&case, now()));
}

#[test]
fn a4_gate_supprime_rejet() {
    let mut case = t1_after_merge();
    case.gates.gate_suppressed = "jugement E1";
    assert_rejet("A4", validate_action(&case, now()));
}

#[test]
fn a4_mauvais_acteur_rejet() {
    let mut case = t1_after_merge();
    case.gates.separation_ok = false;
    assert_rejet("A4", validate_action(&case, now()));
}

#[test]
fn a7_absence_tue_rejet() {
    let mut case = t1_pending();
    case.report = "";
    assert_rejet("A7", validate_action(&case, now()));
}

#[test]
fn a8_sans_limites_rejet() {
    let mut case = t1_after_merge();
    case.limits = "";
    assert_rejet("A8", validate_action(&case, now()));
}

#[test]
fn a8_pretention_universelle_rejet() {
    let mut case = t1_after_merge();
    case.claims_universal = true;
    assert_rejet("A8", validate_action(&case, now()));
}

#[test]
fn a3_rapport_avant_acte_rejet() {
    let mut case = t1_after_merge();
    case.reported_before_act = true;
    assert_rejet("A3", validate_action(&case, now()));
}

// --- A5 : le filet ---

#[test]
fn a5_rejet_par_la_mauvaise_regle() {
    // Le fautif est planté, mais le dossier déclenche A1 avant A2 : le
    // rejet par la mauvaise règle est un échec de la fonction (A5).
    let data = parse_case(FAUTIF_1, "F-A1").unwrap();
    let mut data = data;
    data.auth_author = String::new();
    let planted = PlantedFautif {
        dispatch_id: "D-N055-F1-9-MERGE",
        expected_rule: "A2",
    };
    let case = data.as_case(Some(planted));
    let result = validate_action(&case, now());
    match &result {
        Err(rejection) => assert!(
            rejection.detail.contains("mauvaise règle"),
            "détail : {}",
            rejection.detail
        ),
        Ok(outcome) => panic!("attendu REJET A5, reçu {:?}", outcome),
    }
    assert_rejet("A5", result);
}

#[test]
fn a5_fautif_non_rejete() {
    // Le fautif est planté pour ce dispatch, mais le cas passe A1–A7
    // (action non posée, absence consignée) : le filet l'attrape.
    let mut case = t1_pending();
    case.planted_fautif = Some(PlantedFautif {
        dispatch_id: "D-N055-F1-9-MERGE",
        expected_rule: "A2",
    });
    assert_rejet("A5", validate_action(&case, now()));
}

// --- Cas limites §5.4 ---

#[test]
fn limite_a_ambigu_renvoye_au_juge() {
    let mut case = t1_pending();
    case.authorization_ambiguous = true;
    case.referred_to_judge = true;
    case.report = "action non posée — autorisation ambiguë, renvoyée au juge";
    assert_not_posed(
        validate_action(&case, now()),
        "renvoyée au juge",
    );
}

#[test]
fn limite_a_ambigu_sans_renvoi_rejet_a2() {
    let mut case = t1_pending();
    case.authorization_ambiguous = true;
    case.referred_to_judge = false;
    assert_rejet("A2", validate_action(&case, now()));
}

#[test]
fn limite_b_revoquee_posee_rejet_a2() {
    let mut case = t1_after_merge();
    case.authorization_revoked = true;
    assert_rejet("A2", validate_action(&case, now()));
}

#[test]
fn limite_b_tete_perimee_renvoi() {
    let mut case = t1_pending();
    case.head_stale = true;
    case.referred_to_judge = true;
    case.report = "action non posée — autorisation révoquée / tête périmée, renvoyée au juge";
    assert_not_posed(
        validate_action(&case, now()),
        "renvoyée au juge",
    );
}

#[test]
fn limite_c_deja_fait_constate() {
    let mut case = t1_pending();
    case.already_done = true;
    case.already_done_proof = "merge commit 94fcda8, seq 48";
    case.report = "action non posée — déjà fait (merge commit 94fcda8, seq 48)";
    assert_not_posed(validate_action(&case, now()), "déjà fait");
}

#[test]
fn limite_c_deja_fait_reexecute_rejet_a3() {
    let mut case = t1_after_merge();
    case.already_done = true;
    case.already_done_proof = "merge commit 94fcda8, seq 48";
    assert_rejet("A3", validate_action(&case, now()));
}

#[test]
fn limite_d_partiel_reprise_au_point() {
    let mut case = t1_pending();
    case.partially_done = true;
    case.resume_point = "seq 49";
    case.report = "action non posée — partiellement faite, reprise à seq 49";
    assert_not_posed(validate_action(&case, now()), "reprise à seq 49");
}

#[test]
fn limite_d_partiel_sans_point_rejet_a7() {
    let mut case = t1_pending();
    case.partially_done = true;
    case.resume_point = "";
    case.report = "action non posée — partiellement faite";
    assert_rejet("A7", validate_action(&case, now()));
}

#[test]
fn limite_e_carte_rapporte_non_posee() {
    let mut case = t1_pending();
    case.harness_card_pending = true;
    case.report = "action non posée — échouée, carte du harness en attente";
    assert_not_posed(
        validate_action(&case, now()),
        "carte du harness en attente",
    );
}

#[test]
fn limite_e_carte_sans_rapport_rejet_a7() {
    let mut case = t1_pending();
    case.harness_card_pending = true;
    case.report = "action non posée — en attente";
    assert_rejet("A7", validate_action(&case, now()));
}

#[test]
fn limite_e_carte_acte_pose_rejet_a7() {
    let mut case = t1_after_merge();
    case.harness_card_pending = true;
    assert_rejet("A7", validate_action(&case, now()));
}

#[test]
fn limite_f_juge_qui_merge_rejet_a4() {
    // (f) Le juge merge (J7) : la séparation juge ≠ exécutant est
    // violée — rejet, même avec une autorisation valide.
    let mut case = t1_after_merge();
    case.gates.separation_ok = false;
    assert_rejet("A4", validate_action(&case, now()));
}

// --- Cas rejetés : les 4 fautifs, lus au fichier ---

#[test]
fn f_a2_fixture_rejet_a2() {
    let data = parse_case(FAUTIF_2, "F-A2").unwrap();
    let planted = PlantedFautif {
        dispatch_id: "D-N055-F1-9-MERGE",
        expected_rule: "A2",
    };
    assert_rejet("A2", validate_action(&data.as_case(Some(planted)), now()));
}

#[test]
fn f_a3_fixture_rejet_a3() {
    let data = parse_case(FAUTIF_3, "F-A3").unwrap();
    let planted = PlantedFautif {
        dispatch_id: "D-N055-F1-9-MERGE",
        expected_rule: "A3",
    };
    assert_rejet("A3", validate_action(&data.as_case(Some(planted)), now()));
}

#[test]
fn f_a4_fixture_rejet_a6() {
    let data = parse_case(FAUTIF_4, "F-A4").unwrap();
    let planted = PlantedFautif {
        dispatch_id: "D-N055-F1-9-MERGE",
        expected_rule: "A6",
    };
    assert_rejet("A6", validate_action(&data.as_case(Some(planted)), now()));
}

// --- Parseur du dossier ---

#[test]
fn parse_case_lit_le_bloc_fautif() {
    let data = parse_case(FAUTIF_1, "F-A1").unwrap();
    assert_eq!(data.dispatch_id, "D-N055-F1-9-MERGE");
    assert_eq!(data.auth_step, "F1-8");
    assert_eq!(data.step, "F1-9");
    assert!(data.act_posed);
    assert!(!data.judgment_rendered);
    assert_eq!(data.gate_suppressed, "");
    assert!(data.limits_text.contains("O3 conservée"));
}

#[test]
fn parse_case_bloc_introuvable() {
    assert!(parse_case(FAUTIF_1, "T9").is_err());
}
