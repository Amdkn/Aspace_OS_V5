//! Suite de la fonction Exécuter (D-N055 F1-6, H-M3).
//!
//! Cas passant : une exécution valide du merge de la PR #44
//! (`execution-valide.md` — dossier d'exécution réel, faits vérifiés à
//! l'API par le Discover F1-6 : tête `2d38798`, merge `573cad4`, 2 parents,
//! CI 8/8) doit passer E1–E8. Cas rejetés : les 5 fautifs du Discover §6,
//! dérivés chacun par UNE SEULE différence (un seul remplacement, vérifié
//! `count == 1`) — ils doivent être rejetés avec la raison nommée (E2, E3,
//! E1, E5, E8), dont le merge fautif planté n° 1 (tête non autorisée,
//! D-F1-6-4, amendement A-F1-6-1). Cas limites : document vide (E1),
//! dossier sans limites nommées (E8), PR non mergeable (E4), appel non
//! consigné (E6), parent 2 non autorisé (E7), stade pré-merge (E1–E5),
//! type `merge_executed` légal comme 9e type (A-F1-6-4).
//!
//! Les SHA complets du dossier sont résolus par le résolveur statique
//! (vérifiés à l'API par l'opérateur : tête PR #44 `2d38798…`, base
//! `96d64ce…`, merge PR #44 `573cad4…`, parent 1 `a0a6cb3…`).

use r10_validator::execute::{
    is_legal_event_type, validate_execution, ExecutionEvidence, Stage,
    JOURNAL_EVENT_TYPES,
};
use r10_validator::StaticShaResolver;

const BASE: &str = include_str!("fixtures/execution-valide.md");

const HEAD: &str = "2d3879808cd165a449016372a8a8ed4e4af03ec3";
const BASE_SHA: &str = "96d64ce8c5fb7626a9a80ef1c5602bfb38b7f273";
const MERGE: &str = "573cad466fbc4c76da522ddaec893d54e6650907";
const PARENT1: &str = "a0a6cb39d1d7e0c921325e33ce8742d22d4f46d8";

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
    StaticShaResolver::new(
        [HEAD, BASE_SHA, MERGE, PARENT1]
            .iter()
            .map(|s| s.to_string()),
    )
}

fn evidence<'a>(resolver: &'a StaticShaResolver) -> ExecutionEvidence<'a> {
    ExecutionEvidence {
        head: HEAD,
        resolver,
        ci: &CI,
        mergeable: true,
        mergeable_state: "clean",
        method: "merge",
        excluded: &[],
        stage: Stage::PostMerge,
        merge_commit: Some(MERGE),
        merged: true,
        merged_at: "2026-11-12T19:59:15Z",
        parent1: Some(PARENT1),
        parent2: Some(HEAD),
        master_head: Some(MERGE),
        open_prs: Some(0),
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
fn execution_valide_passe_e1_e8() {
    let r = resolver();
    let ev = evidence(&r);
    let valid = validate_execution(BASE, &ev).unwrap();
    assert_eq!(valid.pr, "44");
    assert_eq!(valid.head, HEAD);
    assert_eq!(valid.method, "merge");
    assert_eq!(valid.merge_commit.as_deref(), Some(MERGE));
}

#[test]
fn fautif_1_tete_non_autorisee_rejetee_e2() {
    // A-F1-6-1 : le verdict autorise l'ancienne tête (la base) alors que
    // la tête vérifiée a bougé — un merge qui merge une tête qu'il n'a pas
    // vérifiée au moment de l'acte n'est pas une exécution, c'est un clic.
    let f = fautif(
        BASE,
        "**Tête autorisée : `2d3879808cd165a449016372a8a8ed4e4af03ec3`**",
        "**Tête autorisée : `96d64ce8c5fb7626a9a80ef1c5602bfb38b7f273`**",
    );
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E2");
    assert!(err.detail.contains("c'est un clic"));
}

#[test]
fn fautif_2_ci_non_verte_rejetee_e3() {
    // Un check-run en échec dans le dossier, alors que le jugement
    // affirmait le vert — l'exécutant re-vérifie, le désaccord tranche
    // en rejet.
    let f = fautif(
        BASE,
        "- Verify 01 Kernel Gates : success",
        "- Verify 01 Kernel Gates : failure",
    );
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E3");
}

#[test]
fn fautif_3_sans_jugement_rejete_e1() {
    // Jugement REJETÉE — l'exécutant ne merge jamais sans instruction.
    let f = fautif(
        BASE,
        "**Verdict du jugement : VALIDÉE**",
        "**Verdict du jugement : REJETÉE**",
    );
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E1");
}

#[test]
fn fautif_4_methode_squash_rejetee_e5() {
    // Demande d'exécution portant la méthode `squash` — un squash n'est
    // pas un merge du 1, même sur la bonne tête.
    let f = fautif(BASE, "méthode `merge`", "méthode `squash`");
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E5");
}

#[test]
fn fautif_5_executant_qui_juge_rejete_e8() {
    // Un reçu consigné par cette exécution — l'exécutant ne juge pas.
    let f = fautif(
        BASE,
        "## Ce que l'exécutant n'a pas fait",
        "## Ce que l'exécutant n'a pas fait\n\n**Reçu consigné par cette exécution : G-20261112-901 (mission TEST-F1-6-FAUTIF-5).**",
    );
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E8");
}

#[test]
fn document_vide_rejete_e1() {
    let err = validate_execution("", &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E1");
}

#[test]
fn dossier_sans_limites_rejete_e8() {
    let f = fautif(
        BASE,
        "## Ce que cette exécution ne prouve pas",
        "## Limites",
    );
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E8");
}

#[test]
fn mergeable_bloque_rejete_e4() {
    // PR non mergeable (conflit) — l'exécution attend ou renvoie, elle
    // ne force pas.
    let r = resolver();
    let ev = ExecutionEvidence {
        mergeable_state: "blocked",
        ..evidence(&r)
    };
    let err = validate_execution(BASE, &ev).unwrap_err();
    assert_eq!(err.rule, "E4");
}

#[test]
fn appel_non_consigné_rejete_e6() {
    // Sortie de l'appel sans `merged: true` — un merge dont l'appel n'est
    // pas consigné n'est pas vérifiable.
    let f = fautif(
        BASE,
        "**Sortie :** merge commit `573cad466fbc4c76da522ddaec893d54e6650907`, `merged: true`.",
        "**Sortie :** merge commit `573cad466fbc4c76da522ddaec893d54e6650907`, `merged: false`.",
    );
    let err = validate_execution(&f, &evidence(&resolver())).unwrap_err();
    assert_eq!(err.rule, "E6");
}

#[test]
fn parent2_non_autorise_rejete_e7() {
    // Merge commit dont le parent 2 n'est pas la tête autorisée — le
    // filet post-merge attrape le merge sur une autre tête.
    let r = resolver();
    let ev = ExecutionEvidence {
        parent2: Some(BASE_SHA),
        ..evidence(&r)
    };
    let err = validate_execution(BASE, &ev).unwrap_err();
    assert_eq!(err.rule, "E7");
}

#[test]
fn merge_executed_neuvieme_type_legal() {
    // A-F1-6-4 : `merge_executed` est le 9e type du journal, légalisé
    // porté en avant — la fonction Exécuter l'accepte comme type légal.
    assert_eq!(JOURNAL_EVENT_TYPES.len(), 9);
    assert!(is_legal_event_type("merge_executed"));
    assert!(is_legal_event_type("closure_pulse"));
    assert!(is_legal_event_type("judgment_rendered"));
    assert!(!is_legal_event_type("type_inconnu"));
}

#[test]
fn pre_merge_passe_e1_e5() {
    // Stade pré-merge : E1, E8, E2, E4, E3, E5 contrôlés ; E6/E7 ne sont
    // pas encore applicables (vérifiées après l'appel).
    let r = resolver();
    let ev = ExecutionEvidence {
        stage: Stage::PreMerge,
        merge_commit: None,
        merged: false,
        merged_at: "",
        parent1: None,
        parent2: None,
        master_head: None,
        open_prs: None,
        ..evidence(&r)
    };
    let valid = validate_execution(BASE, &ev).unwrap();
    assert_eq!(valid.pr, "44");
    assert_eq!(valid.merge_commit, None);
}
