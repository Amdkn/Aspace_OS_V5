//! Suite de la fonction Preuve finale (D-N055 F1-11, H-M3).
//!
//! Cas passants : le rejeu conjoint — la preuve complète (suite 213/213
//! + tests neufs, 10 jugements VALIDÉ/ACCEPTÉ, 9 merges true merge, 6
//! absorptions avec preuves, 20 ancres généralisées, F-V5 rejeté V9,
//! régressions F-V1..F-V4 conformes, 2 états de vision acceptés sans
//! contradiction, 1 acte autorisé sans question, 0 routeur, F-A3 rejeté
//! A3, R3 aligné, fiche/manifeste corrigés, coordinateur disponible,
//! limites avec DETTE-H-F1-7-SEMAINE — doit passer P1–P8). Cas
//! rejetés : (a) semaine exigée (claims_universal → P8), (b) routeur
//! non nul (P5), (c) absorption sans preuve (P2), (d) ancre non
//! généralisée (P6), (e) F-A3 rejeté par une autre règle (P7 ; A2 avec
//! raison passe), (f) fiche en retard au merge (P7), (g) coordinateur
//! indisponible (P7). Cas limites (§5.4) : l'absence d'acte consignée
//! passe P4 (honnêteté A7) ; un merge squash (1 parent) rejette P1 ;
//! un état de vision rejeté rejette P3 ; des journaux de même taille
//! rejettent P3.
//!
//! Les cas sont construits en Rust (données injectées) — la CLI
//! `prove-final` les rend depuis les fichiers.

use r10_validator::r#final::{
    validate_final, Absorption, Act, FinalProof, JudgmentRef, MergeRef, VisionReplay,
};
use r10_validator::Rejection;

fn assert_rejet(rule: &str, result: Result<r10_validator::r#final::ValidFinal, Rejection>) {
    match result {
        Err(rejection) => assert_eq!(
            rejection.rule, rule,
            "rejet attendu {}, reçu {} ({})",
            rule, rejection.rule, rejection.detail
        ),
        Ok(valid) => panic!("rejet {} attendu, reçu {:?}", rule, valid),
    }
}

fn judgments() -> Vec<JudgmentRef<'static>> {
    vec![
        JudgmentRef { step: "F1-1", source: "registre journal 787", verdict: "ACCEPTÉ" },
        JudgmentRef { step: "F1-2", source: "registre journal 791", verdict: "VALIDÉE pour merge" },
        JudgmentRef { step: "F1-3", source: "JUGEMENT-F1-3.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-4", source: "JUGEMENT-F1-4.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-5", source: "JUGEMENT-F1-5.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-6", source: "JUGEMENT-F1-6.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-7", source: "JUGEMENT-F1-7.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-8", source: "JUGEMENT-F1-8.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-9", source: "JUGEMENT-F1-9.md", verdict: "VALIDÉE" },
        JudgmentRef { step: "F1-10", source: "JUGEMENT-F1-10.md", verdict: "VALIDÉE AVEC RÉSERVES" },
    ]
}

fn merges() -> Vec<MergeRef<'static>> {
    let parents = [
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    ];
    let shas = [
        "1f89b56123456789012345678901234567890123",
        "4668305123456789012345678901234567890123",
        "573cad4123456789012345678901234567890123",
        "4a68288123456789012345678901234567890123",
        "e2e9c14123456789012345678901234567890123",
        "055745b853495c38f0aaa0ae6c3d2adad9e89177",
        "94fcda8123456789012345678901234567890123",
        "691b0a0123456789012345678901234567890123",
        "28d32f7123456789012345678901234567890123",
    ];
    let prs = [26, 30, 44, 47, 49, 50, 51, 52, 53];
    prs.iter()
        .zip(shas.iter())
        .map(|(pr, sha)| MergeRef {
            pr: *pr,
            sha,
            parent1: parents[0],
            parent2: parents[1],
        })
        .collect()
}

fn absorptions() -> Vec<Absorption<'static>> {
    vec![
        Absorption { function: "vérifier", proof: "DVG-01 + CI 8/8 dans les 8 jugements F1-3..F1-10" },
        Absorption { function: "décider", proof: "designs signés journaux 790/806/923/931/934/937/939/941/943" },
        Absorption { function: "observer", proof: "L00 tête Run #711 + N2 Run #487 re-mesurés" },
        Absorption { function: "interfacer", proof: "surface unique main + WhatsApp, chat.list re-vérifié" },
        Absorption { function: "fluer", proof: "journal 90 événements, seq 1–90, 0 trou" },
        Absorption { function: "fabriquer", proof: "9 merges true merge, commits 1f89b56..28d32f7" },
    ]
}

fn preuve() -> FinalProof<'static> {
    FinalProof {
        suite_total: 213,
        suite_passed: 213,
        judgments: Box::leak(judgments().into_boxed_slice()),
        merges: Box::leak(merges().into_boxed_slice()),
        absorptions: Box::leak(absorptions().into_boxed_slice()),
        anchors_generalized: 20,
        fautif_v5_rejected: true,
        fautif_v5_rule: "V9",
        vision_regressions: Box::leak(
            vec![("F-V1", "V3"), ("F-V2", "V2"), ("F-V3", "V1"), ("F-V4", "V4")]
                .into_boxed_slice(),
        ),
        vision_states: Box::leak(
            vec![
                VisionReplay { journal_lines: 47, accepted: true, contradictions: 0 },
                VisionReplay { journal_lines: 90, accepted: true, contradictions: 0 },
            ]
            .into_boxed_slice(),
        ),
        acts: Box::leak(
            vec![Act {
                act: "ouverture de la PR F1-11",
                authorized: true,
                questions_asked: 0,
                dispatch_id: "D-N055-F1-11-DELIVER",
            }]
            .into_boxed_slice(),
        ),
        absence_consigned: false,
        router_nardole_events: 0,
        router_routing_total: 5,
        router_routing_as_events: 5,
        f_a3_rule: "A3",
        f_a3_reason: "",
        r3_aligned: true,
        fiche_manifeste_corrected: true,
        coordinator_available: true,
        limits: Box::leak(
            vec![
                "DETTE-H-F1-7-SEMAINE — la tenue vision + action sur 7 jours consécutifs n'est pas prouvée",
                "mémoire universelle non prouvée",
                "démantèlement non prouvé",
                "rollback réel non prouvé",
                "H-F8-9 NON MESURÉ",
                "bascule non prouvée",
            ]
            .into_boxed_slice(),
        ),
        claims_universal: false,
    }
}

#[test]
fn rejeu_conjoint_passe_p1_p8() {
    let valid = validate_final(&preuve()).unwrap();
    assert_eq!(valid.suite_passed, 213);
    assert_eq!(valid.judgments, 10);
    assert_eq!(valid.merges, 9);
    assert_eq!(valid.absorptions, 6);
    assert_eq!(valid.vision_states, 2);
    assert_eq!(valid.acts, 1);
    assert_eq!(valid.routings_as_events, 5);
}

#[test]
fn cas_limite_semaine_exigee_rejet_p8() {
    let mut p = preuve();
    p.claims_universal = true;
    assert_rejet("P8", validate_final(&p));
}

#[test]
fn cas_limite_routeur_non_nul_rejet_p5() {
    let mut p = preuve();
    p.router_nardole_events = 2;
    assert_rejet("P5", validate_final(&p));
}

#[test]
fn cas_limite_absorption_sans_preuve_rejet_p2() {
    let mut p = preuve();
    let mut a = absorptions();
    a[3].proof = "";
    p.absorptions = Box::leak(a.into_boxed_slice());
    assert_rejet("P2", validate_final(&p));
}

#[test]
fn cas_limite_ancre_non_generalisee_rejet_p6() {
    let mut p = preuve();
    p.anchors_generalized = 19;
    assert_rejet("P6", validate_final(&p));
}

#[test]
fn cas_limite_f_a3_autre_regle_rejet_p7() {
    let mut p = preuve();
    p.f_a3_rule = "A6";
    assert_rejet("P7", validate_final(&p));
}

#[test]
fn cas_limite_f_a3_a2_avec_raison_passe() {
    let mut p = preuve();
    p.f_a3_rule = "A2";
    p.f_a3_reason = "le rapport n'est pas rendu sur le dispatch de l'acte (le merge F1-9 est au journal, la preuve du rapport ne le cite pas)";
    assert!(validate_final(&p).is_ok());
}

#[test]
fn cas_limite_fiche_en_retard_rejet_p7() {
    let mut p = preuve();
    p.fiche_manifeste_corrected = false;
    assert_rejet("P7", validate_final(&p));
}

#[test]
fn cas_limite_coordinateur_indisponible_rejet_p7() {
    let mut p = preuve();
    p.coordinator_available = false;
    assert_rejet("P7", validate_final(&p));
}

#[test]
fn cas_limite_absence_acte_consignée_passe_p4() {
    let mut p = preuve();
    p.acts = &[];
    p.absence_consigned = true;
    assert!(validate_final(&p).is_ok());
}

#[test]
fn cas_limite_merge_squash_rejet_p1() {
    let mut p = preuve();
    let mut m = merges();
    m[0].parent2 = m[0].parent1;
    p.merges = Box::leak(m.into_boxed_slice());
    assert_rejet("P1", validate_final(&p));
}

#[test]
fn cas_limite_etat_vision_rejete_rejet_p3() {
    let mut p = preuve();
    let s = vec![
        VisionReplay { journal_lines: 47, accepted: true, contradictions: 0 },
        VisionReplay { journal_lines: 90, accepted: false, contradictions: 0 },
    ];
    p.vision_states = Box::leak(s.into_boxed_slice());
    assert_rejet("P3", validate_final(&p));
}

#[test]
fn cas_limite_journaux_meme_taille_rejet_p3() {
    let mut p = preuve();
    let s = vec![
        VisionReplay { journal_lines: 90, accepted: true, contradictions: 0 },
        VisionReplay { journal_lines: 90, accepted: true, contradictions: 0 },
    ];
    p.vision_states = Box::leak(s.into_boxed_slice());
    assert_rejet("P3", validate_final(&p));
}
