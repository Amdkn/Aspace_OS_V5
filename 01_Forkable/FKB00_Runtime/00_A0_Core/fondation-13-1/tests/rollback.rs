//! Suite de la fonction Rollback (D-N055 F1-10, H-M3).
//!
//! Cas passants : les 10 cas d'essai du design §6 H-F1-9 (T0 contrôle
//! négatif : hold-out vert → 0 événement de rollback ; T1 Juger → 13e,
//! checkpoint seq 20 ; T2 Exécuter → Ryan, checkpoint seq 27, revert
//! documenté sur base jetable ; T3 Mémoriser → Graham, checkpoint seq 37 ;
//! T4 Vision → L00/pulses/coordinateur, checkpoint seq 48 ; T5 Action →
//! opérateur/sous-agents/coordinateur, checkpoint seq 57 ; T6 Router →
//! Nardole, checkpoint seq 6, typage à la main ; T7 Structurer → Rick,
//! checkpoint hors journal registre journal 787 ; T8 Recevoir → Graham,
//! checkpoint hors journal reçu G-20261112-041, continuation de T3 ; T9
//! Découvrir → Bill, checkpoint seq 13, décideur coordinateur — doivent
//! passer R1–R8). Cas rejetés : les 5 fautifs du Discover §5.3, dérivés
//! chacun par UNE SEULE différence (raisons nommées : R3 reprise
//! auto-déclarée, R4 checkpoint à preuve vide / fonction saine / mauvais
//! repreneur, R6 révocation par effacement), dont le fait fautif planté
//! F-R1 (reprise auto-déclarée sans décision du coordinateur, D-F1-10-6,
//! amendement A-F1-10-1). Cas limites (§5.4) : (a) fonction saine, (b)
//! reprise partielle, (c) deux hold-outs échoués à la fois, (d) session
//! d'origine indisponible, (e) checkpoint ambigu, (f) révocation d'un
//! état déjà rendu (merge), (g) démantèlement déguisé, (h) coordinateur
//! indisponible (13e décideur de secours), (i) échec pendant la reprise
//! — traités comme définis.
//!
//! Les cas sont construits en Rust (données injectées) — la CLI
//! `prove-rollback` les rend depuis les fichiers ; les dossiers fautifs
//! (`fixtures/rollback-fautif-N.md`) sont lus par `parse_case`, comme la
//! CLI les lit au fichier.

use r10_validator::rollback::{
    parse_case, validate_rollback, Checkpoint, Decision, Loss, Revocation, RollbackCase,
    RollbackOutcome,
};
use r10_validator::Rejection;

const FAUTIF_1: &str = include_str!("fixtures/rollback-fautif-1.md");
const FAUTIF_2: &str = include_str!("fixtures/rollback-fautif-2.md");
const FAUTIF_3: &str = include_str!("fixtures/rollback-fautif-3.md");
const FAUTIF_4: &str = include_str!("fixtures/rollback-fautif-4.md");
const FAUTIF_5: &str = include_str!("fixtures/rollback-fautif-5.md");
const VALIDE_T1: &str = include_str!("fixtures/rollback-valide-t1.md");

const LIMITES: &str = "désarchivage littéral exclu ; reprise d'une fonction saine exclue ; démantèlement exclu ; semaine F1-11 hors pas ; échec réel hors pas ; réserves R1/R3/R4 portées";

fn assert_rejet(rule: &str, result: Result<RollbackOutcome, Rejection>) {
    match result {
        Err(rejection) => assert_eq!(
            rejection.rule, rule,
            "rejet attendu {}, reçu {} ({})",
            rule, rejection.rule, rejection.detail
        ),
        Ok(outcome) => panic!(
            "rejet {} attendu, reçu {:?}",
            rule, outcome
        ),
    }
}

fn assert_accepte(result: Result<RollbackOutcome, Rejection>) -> String {
    match result {
        Ok(RollbackOutcome::Accepted(valid)) => valid.report,
        Ok(RollbackOutcome::NotApplicable { reason }) => {
            panic!("acceptation attendue, reçu non applicable : {}", reason)
        }
        Err(rejection) => panic!(
            "acceptation attendue, reçu REJET {} ({})",
            rejection.rule, rejection.detail
        ),
    }
}

fn checkpoint_journal(seq: usize, event_id: &'static str, at: &'static str) -> Checkpoint<'static> {
    Checkpoint {
        seq,
        event_id,
        at,
        source: "",
        proof: "preuve du checkpoint, relue au journal réel",
        proof_empty_in_journal: false,
        matches_journal: true,
        ambiguous: false,
    }
}

fn decision_coordinateur() -> Decision<'static> {
    Decision {
        decider: "coordinateur",
        event_id: "EVT-20261113-101",
        event_in_journal: true,
        stop_in_journal: true,
    }
}

/// Un retour valide (T1) : Juger → 13e, checkpoint seq 20.
fn t1_valide() -> RollbackCase<'static> {
    RollbackCase {
        dispatch_id: "D-N055-F1-10-SIM-T1",
        case_id: "T1",
        function: "F1-5",
        holdout: "H-F1-2",
        rollback_claimed: true,
        failure_named: true,
        failure_dossier: "JUGEMENT-FAUTIF-1.md",
        failure_rule: "J2",
        holdout_failed: true,
        repreneur: "13e",
        repreneur_expected: "13e",
        repreneur_available: true,
        resume_partial: false,
        covers_two_functions: false,
        checkpoint: checkpoint_journal(20, "EVT-20261112-013", "2026-11-12T22:26:13-05:00"),
        decision: decision_coordinateur(),
        loss: Loss::default(),
        revocation: Revocation {
            kind: "correction",
            explicit: true,
            erases: false,
            erroneous_act_rendered: true,
            erroneous_merge_posed: false,
        },
        reproof_passed: true,
        limits: LIMITES,
        claims_universal: false,
        dismantles: false,
        rollback_event_in_journal: true,
    }
}

fn cas_valide(
    dispatch: &'static str,
    case_id: &'static str,
    function: &'static str,
    holdout: &'static str,
    dossier: &'static str,
    rule: &'static str,
    repreneur: &'static str,
    checkpoint: Checkpoint<'static>,
    revocation: Revocation<'static>,
) -> RollbackCase<'static> {
    let mut c = t1_valide();
    c.dispatch_id = dispatch;
    c.case_id = case_id;
    c.function = function;
    c.holdout = holdout;
    c.failure_dossier = dossier;
    c.failure_rule = rule;
    c.repreneur = repreneur;
    c.repreneur_expected = repreneur;
    c.checkpoint = checkpoint;
    c.revocation = revocation;
    c
}

fn revocation_correction() -> Revocation<'static> {
    Revocation {
        kind: "correction",
        explicit: true,
        erases: false,
        erroneous_act_rendered: true,
        erroneous_merge_posed: false,
    }
}

fn revocation_revert() -> Revocation<'static> {
    Revocation {
        kind: "revert",
        explicit: true,
        erases: false,
        erroneous_act_rendered: true,
        erroneous_merge_posed: true,
    }
}

// --- Cas passants : T0–T9 ---

#[test]
fn t0_controle_negatif() {
    let mut c = t1_valide();
    c.dispatch_id = "D-N055-F1-10-SIM-T0";
    c.case_id = "T0";
    c.rollback_claimed = false;
    c.holdout_failed = false;
    c.failure_named = false;
    c.failure_dossier = "";
    c.failure_rule = "";
    c.rollback_event_in_journal = false;
    match validate_rollback(&c) {
        Ok(RollbackOutcome::NotApplicable { reason }) => {
            assert!(reason.contains("0 événement de rollback"));
        }
        other => panic!("T0 attendu non applicable, reçu {:?}", other),
    }
}

#[test]
fn t1_juger_vers_13e() {
    let report = assert_accepte(validate_rollback(&t1_valide()));
    assert!(report.contains("seq 20"));
    assert!(report.contains("perte 0"));
}

#[test]
fn t2_executer_vers_ryan_revert() {
    let c = cas_valide(
        "D-N055-F1-10-SIM-T2",
        "T2",
        "F1-6",
        "H-F1-3",
        "EXECUTION-FAUTIF-1.md",
        "E2",
        "Ryan",
        checkpoint_journal(27, "EVT-20261113-002", "2026-11-13T00:35:31-05:00"),
        revocation_revert(),
    );
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t3_memoriser_vers_graham() {
    let c = cas_valide(
        "D-N055-F1-10-SIM-T3",
        "T3",
        "F1-7",
        "H-F1-6",
        "CITATION-FAUTIF-1-F1-7.md",
        "M3",
        "Graham",
        checkpoint_journal(37, "EVT-20261113-012", "2026-11-13T01:47:15-05:00"),
        revocation_correction(),
    );
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t4_vision_vers_mecanismes() {
    let c = cas_valide(
        "D-N055-F1-10-SIM-T4",
        "T4",
        "F1-8",
        "H-F1-7",
        "VISION-FAUTIF-1.md",
        "V3",
        "L00 + pulses + coordinateur",
        checkpoint_journal(48, "EVT-20261113-023", "2026-11-13T03:25:55-05:00"),
        revocation_correction(),
    );
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t5_action_vers_acteurs() {
    // D-F1-10-10 : T5 garde le fautif planté F-A1 accepté — F-A3 n'est
    // PAS l'échec simulé (réserve R4, suivi F1-11).
    let c = cas_valide(
        "D-N055-F1-10-SIM-T5",
        "T5",
        "F1-9",
        "H-F1-8",
        "F-A1",
        "A2",
        "opérateur + sous-agents + coordinateur",
        checkpoint_journal(57, "EVT-20261113-032", "2026-11-13T04:50:22-05:00"),
        revocation_correction(),
    );
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t6_router_vers_nardole() {
    let c = cas_valide(
        "D-N055-F1-10-SIM-T6",
        "T6",
        "F1-3",
        "H-F1-4",
        "dispatch sans design signé typé",
        "R3",
        "Nardole",
        checkpoint_journal(6, "EVT-20261111-006", "2026-11-11T02:02:33-05:00"),
        revocation_correction(),
    );
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t7_structurer_vers_rick_hors_journal() {
    let mut c = cas_valide(
        "D-N055-F1-10-SIM-T7",
        "T7",
        "F1-1",
        "H-F1-1",
        "BYB accepté sans design signé",
        "structuration",
        "Rick",
        checkpoint_journal(0, "", ""),
        revocation_correction(),
    );
    c.checkpoint.seq = 0;
    c.checkpoint.event_id = "";
    c.checkpoint.at = "";
    c.checkpoint.source = "registre journal 787";
    c.checkpoint.proof = "BYB F1-2 v2 ACCEPTÉ comme saisine, 2026-11-11 ~00:53 EST";
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t8_recevoir_vers_graham_continuation() {
    // D-F1-10-8 : T8 est la continuation de T3 — même instance de
    // Graham, pas un second réveil.
    let mut c = cas_valide(
        "D-N055-F1-10-SIM-T8",
        "T8",
        "F1-2",
        "H-F1-5",
        "reçu accepté sans preuve citée",
        "réception",
        "Graham",
        checkpoint_journal(0, "", ""),
        revocation_correction(),
    );
    c.checkpoint.seq = 0;
    c.checkpoint.event_id = "";
    c.checkpoint.at = "";
    c.checkpoint.source = "reçu G-20261112-041";
    c.checkpoint.proof = "merge PR #52, 691b0a0, 2 parents, commit 799c526";
    assert_accepte(validate_rollback(&c));
}

#[test]
fn t9_decouvrir_vers_bill() {
    let c = cas_valide(
        "D-N055-F1-10-SIM-T9",
        "T9",
        "F1-4",
        "H-F1-1",
        "Discover violant D1–D8 accepté",
        "D1–D8",
        "Bill",
        checkpoint_journal(13, "EVT-20261112-006", "2026-11-12T14:57:33-05:00"),
        revocation_correction(),
    );
    assert_accepte(validate_rollback(&c));
}

// --- Cas rejetés : les 5 fautifs ---

#[test]
fn f_r1_reprise_auto_declaree_rejet_r3() {
    let mut c = t1_valide();
    c.dispatch_id = "D-N055-F1-10-SIM-FR1";
    c.case_id = "F-R1";
    c.decision.event_in_journal = false;
    c.decision.stop_in_journal = false;
    c.decision.event_id = "";
    assert_rejet("R3", validate_rollback(&c));
}

#[test]
fn f_r2_checkpoint_preuve_vide_rejet_r4() {
    let mut c = t1_valide();
    c.dispatch_id = "D-N055-F1-10-SIM-FR2";
    c.case_id = "F-R2";
    c.checkpoint.seq = 49;
    c.checkpoint.event_id = "EVT-20261113-024";
    c.checkpoint.at = "2026-11-13T04:23:26-05:00";
    c.checkpoint.proof_empty_in_journal = true;
    c.checkpoint.proof = "";
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn f_r3_fonction_saine_rejet_r4() {
    let mut c = t1_valide();
    c.dispatch_id = "D-N055-F1-10-SIM-FR3";
    c.case_id = "F-R3";
    c.holdout_failed = false;
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn f_r4_revocation_par_effacement_rejet_r6() {
    let mut c = t1_valide();
    c.dispatch_id = "D-N055-F1-10-SIM-FR4";
    c.case_id = "F-R4";
    c.revocation.erases = true;
    c.revocation.explicit = false;
    assert_rejet("R6", validate_rollback(&c));
}

#[test]
fn f_r5_mauvais_repreneur_rejet_r4() {
    let mut c = t1_valide();
    c.dispatch_id = "D-N055-F1-10-SIM-FR5";
    c.case_id = "F-R5";
    c.repreneur = "Ryan";
    assert_rejet("R4", validate_rollback(&c));
}

// --- Cas limites (§5.4) ---

#[test]
fn limite_a_fonction_saine_avec_evenement_rejet_r4() {
    // T0 inversé au journal : un événement de rollback existe pour un
    // hold-out vert — la fonction saine est reprise.
    let mut c = t1_valide();
    c.rollback_claimed = false;
    c.holdout_failed = false;
    c.rollback_event_in_journal = true;
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn limite_b_reprise_partielle_rejet_r4() {
    let mut c = t1_valide();
    c.resume_partial = true;
    c.repreneur = "L00 seul";
    c.repreneur_expected = "L00 seul";
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn limite_c_deux_retours_un_evenement_rejet_r3() {
    let mut c = t1_valide();
    c.covers_two_functions = true;
    assert_rejet("R3", validate_rollback(&c));
}

#[test]
fn limite_d_session_indisponible_rejet_r4() {
    let mut c = t1_valide();
    c.repreneur_available = false;
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn limite_e_checkpoint_ambigu_rejet_r4() {
    let mut c = t1_valide();
    c.checkpoint.ambiguous = true;
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn limite_f_merge_corrige_par_evenement_rejet_r6() {
    // §5.4f : un merge erroné se reverte par un revert documenté — une
    // révocation par événement `correction` ne suffit pas.
    let mut c = t1_valide();
    c.revocation.erroneous_merge_posed = true;
    c.revocation.kind = "correction";
    assert_rejet("R6", validate_rollback(&c));
}

#[test]
fn limite_f_merge_reverte_accepte() {
    let mut c = t1_valide();
    c.revocation = revocation_revert();
    assert_accepte(validate_rollback(&c));
}

#[test]
fn limite_g_demantelement_rejet_r8() {
    let mut c = t1_valide();
    c.dismantles = true;
    assert_rejet("R8", validate_rollback(&c));
}

#[test]
fn limite_h_coordinateur_indisponible_13e_secours() {
    // D-F1-10-4 : le 13e décide en secours, par événement du journal.
    let mut c = t1_valide();
    c.decision.decider = "13e";
    assert_accepte(validate_rollback(&c));
}

#[test]
fn limite_h_decideur_ni_coordinateur_ni_13e_rejet_r3() {
    let mut c = t1_valide();
    c.decision.decider = "fonction";
    assert_rejet("R3", validate_rollback(&c));
}

#[test]
fn limite_i_echec_pendant_reprise_rejet_r7() {
    let mut c = t1_valide();
    c.reproof_passed = false;
    assert_rejet("R7", validate_rollback(&c));
}

// --- Règles une à une ---

#[test]
fn r1_echec_non_nomme_rejet() {
    let mut c = t1_valide();
    c.failure_named = false;
    assert_rejet("R1", validate_rollback(&c));
}

#[test]
fn r1_dossier_plante_vide_rejet() {
    let mut c = t1_valide();
    c.failure_dossier = "";
    assert_rejet("R1", validate_rollback(&c));
}

#[test]
fn r2_arret_silencieux_rejet() {
    let mut c = t1_valide();
    c.decision.stop_in_journal = false;
    assert_rejet("R2", validate_rollback(&c));
}

#[test]
fn r4_checkpoint_ne_correspond_pas_au_journal_rejet() {
    let mut c = t1_valide();
    c.checkpoint.matches_journal = false;
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn r4_checkpoint_hors_journal_sans_source_rejet() {
    let mut c = t1_valide();
    c.checkpoint.seq = 0;
    c.checkpoint.event_id = "";
    c.checkpoint.at = "";
    c.checkpoint.source = "";
    assert_rejet("R4", validate_rollback(&c));
}

#[test]
fn r5_etat_non_porte_rejet() {
    let mut c = t1_valide();
    c.loss.unported_state = true;
    assert_rejet("R5", validate_rollback(&c));
}

#[test]
fn r5_acte_apres_checkpoint_rejet() {
    let mut c = t1_valide();
    c.loss.act_after_checkpoint = true;
    assert_rejet("R5", validate_rollback(&c));
}

#[test]
fn r5_decision_non_consignée_rejet() {
    let mut c = t1_valide();
    c.loss.undecided_decision = true;
    assert_rejet("R5", validate_rollback(&c));
}

#[test]
fn r6_acte_rendu_sans_revocation_explicite_rejet() {
    let mut c = t1_valide();
    c.revocation.explicit = false;
    assert_rejet("R6", validate_rollback(&c));
}

#[test]
fn r8_limites_absentes_rejet() {
    let mut c = t1_valide();
    c.limits = "";
    assert_rejet("R8", validate_rollback(&c));
}

#[test]
fn r8_pretention_universelle_rejet() {
    let mut c = t1_valide();
    c.claims_universal = true;
    assert_rejet("R8", validate_rollback(&c));
}

// --- Parse des fixtures ---

#[test]
fn parse_fautif_1() {
    let data = parse_case(FAUTIF_1, "F-R1").unwrap();
    assert_eq!(data.function, "F1-5");
    assert_eq!(data.dispatch_id, "D-N055-F1-10-SIM-FR1");
    assert!(data.rollback_claimed);
    assert_eq!(data.decision_decider, "");
    assert!(!data.decision_event_in_journal);
}

#[test]
fn parse_fautif_2_checkpoint_preuve_vide() {
    let data = parse_case(FAUTIF_2, "F-R2").unwrap();
    assert_eq!(data.checkpoint_seq, 49);
    assert_eq!(data.checkpoint_event_id, "EVT-20261113-024");
}

#[test]
fn parse_fautif_3_fonction_saine() {
    let data = parse_case(FAUTIF_3, "F-R3").unwrap();
    assert!(!data.holdout_failed);
    assert!(data.rollback_claimed);
}

#[test]
fn parse_fautif_4_effacement() {
    let data = parse_case(FAUTIF_4, "F-R4").unwrap();
    assert!(data.revocation_erases);
}

#[test]
fn parse_fautif_5_mauvais_repreneur() {
    let data = parse_case(FAUTIF_5, "F-R5").unwrap();
    assert_eq!(data.repreneur, "Ryan");
    assert_eq!(data.repreneur_expected, "13e");
}

#[test]
fn parse_valide_t1() {
    let data = parse_case(VALIDE_T1, "T1").unwrap();
    assert_eq!(data.function, "F1-5");
    assert_eq!(data.checkpoint_seq, 20);
    assert_eq!(data.checkpoint_event_id, "EVT-20261112-013");
    assert!(data.reproof_passed);
    let case = data.as_case();
    assert_accepte(validate_rollback(&case));
}
