//! Suite de la fonction Mémoriser (D-N055 F1-7, H-M3).
//!
//! Cas passants : les 3 faits d'essai cités (T1 FreeLLMAPI, T2
//! aspaceos.tech, T3 ID 11e — doivent passer M1–M8) + le fait de merge
//! (base de F-X2). Cas rejetés : les 4 fautifs du Discover §5.3, dérivés
//! chacun par UNE SEULE différence (un seul remplacement, vérifié
//! `count == 1`) — ils doivent être rejetés avec la règle nommée (M3,
//! M2, M2, M4), dont le fait fautif planté F-X1 (date 2027-10-08 au lieu
//! de 2027-10-09, D-F1-7-6, amendement A-F1-7-1). Cas limites (§5.4) :
//! (a) contradiction des trois heures portée, (b) absence des 6 mémoires
//! consignée, (c) source bougée signalée, (d) fait dupliqué dédupliqué,
//! (e) fait à date future, (f) fait sans date.
//!
//! Les lignes sources sont injectées depuis des fichiers séparés
//! (`source-*.txt`, lignes relues au fichier par le générateur) —
//! jamais recopiées depuis le dossier de citation : M2 compare le
//! dossier à la ligne, pas le dossier à lui-même.

use r10_validator::memory::{
    validate_citation, CitationEvidence, Corroboration, JOURNAL_EVENT_TYPES,
};
use r10_validator::router::EVENT_TYPES;

const T2: &str = include_str!("fixtures/citation-valide.md");
const T1: &str = include_str!("fixtures/citation-t1.md");
const T3: &str = include_str!("fixtures/citation-t3.md");
const MERGE: &str = include_str!("fixtures/citation-merge.md");
const FAUTIF_1: &str = include_str!("fixtures/citation-fautif-1.md");
const LIMITE_ABSENT: &str = include_str!("fixtures/citation-limite-absent.md");
const LIMITE_BOUGEE: &str = include_str!("fixtures/citation-limite-bougee.md");
const LIMITE_DUPLIQUE: &str = include_str!("fixtures/citation-limite-duplique.md");
const LIMITE_FUTUR: &str = include_str!("fixtures/citation-limite-futur.md");
const LIMITE_SANS_DATE: &str = include_str!("fixtures/citation-limite-sans-date.md");

const LINE_T2: &str = include_str!("fixtures/source-t2.txt");
const LINE_T1: &str = include_str!("fixtures/source-t1.txt");
const LINE_T1_C1046: &str = include_str!("fixtures/source-t1-corr-1046.txt");
const LINE_T1_C1055: &str = include_str!("fixtures/source-t1-corr-1055.txt");
const LINE_T3: &str = include_str!("fixtures/source-t3.txt");
const LINE_MERGE: &str = include_str!("fixtures/source-merge.txt");
const LINE_FUTUR: &str = include_str!("fixtures/source-futur.txt");
const LINE_SANS_DATE: &str = include_str!("fixtures/source-sans-date.txt");
const LINE_DUPLIQUE: &str = include_str!("fixtures/source-duplique.txt");

fn ev<'a>(
    source_exists: bool,
    source_line_text: &'a str,
    source_date: &'a str,
    corroborations: &'a [Corroboration<'a>],
    planted_fautif: Option<(&'a str, &'a str, &'a str)>,
) -> CitationEvidence<'a> {
    CitationEvidence {
        source_exists,
        source_line_text,
        source_date,
        corroborations,
        planted_fautif,
    }
}

fn no_ev<'a>(line: &'a str, date: &'a str) -> CitationEvidence<'a> {
    ev(true, line, date, &[], None)
}

/// UNE SEULE différence par rapport à une citation valide — le
/// remplacement est vérifié (le motif apparaît exactement une fois).
fn fautif(base: &str, needle: &str, replacement: &str) -> String {
    let count = base.matches(needle).count();
    assert_eq!(
        count, 1,
        "fautif : « {} » apparaît {} fois, pas 1",
        needle, count
    );
    base.replacen(needle, replacement, 1)
}

fn assert_rejet(
    rule: &str,
    result: Result<r10_validator::memory::ValidCitation, r10_validator::Rejection>,
) {
    let err = result.expect_err("la citation aurait dû être rejetée");
    assert_eq!(err.rule, rule, "règle attendue {}, rejet : {}", rule, err);
}

// --- Cas passants : les 3 faits d'essai ---

#[test]
fn citation_valide_t2() {
    let valid = validate_citation(T2, &no_ev(LINE_T2, "2027-10-09")).expect("T2 doit passer M1–M8");
    assert_eq!(valid.date, "2027-10-09");
    assert_eq!(valid.status, "vérifié");
    assert!(valid.source.contains("MEMORY.md:98"));
    assert!(valid.statement.contains("aspaceos.tech"));
}

#[test]
fn citation_t1_contradiction_portee() {
    // Les dates des corroborations sont celles que portent les lignes relues.
    assert!(LINE_T1_C1046.contains("2026-10-17 ~10:46 EDT"));
    assert!(LINE_T1_C1055.contains("2026-10-17 ~10:55 EDT"));
    let corr: [Corroboration; 2] = [
        (
            "~/memory/2026-10-17.md:657",
            "2026-10-17 ~10:46 EDT",
            "vérifié",
        ),
        (
            "~/side-chats/2428b187-722b-427a-8ad3-460bdce2a208/MEMORY.md:67",
            "2026-10-17 ~10:55 EDT",
            "vérifié",
        ),
    ];
    let valid = validate_citation(T1, &ev(true, LINE_T1, "2026-10-17", &corr, None))
        .expect("T1 doit passer M1–M8 avec le statut contredit");
    assert_eq!(valid.status, "contredit");
    assert_eq!(valid.date, "2026-10-17 ~10:50 EDT");
    assert!(valid.statement.contains("FreeLLMAPI"));
}

#[test]
fn citation_t3_date_de_fichier() {
    let valid = validate_citation(T3, &no_ev(LINE_T3, "2026-10-09")).expect("T3 doit passer M1–M8");
    assert_eq!(valid.status, "consigné");
    assert_eq!(valid.date, "2026-10-09");
    assert!(valid
        .statement
        .contains("6f410ddd-4ef8-4834-805a-0b38ede9ba76"));
}

#[test]
fn citation_merge_valide() {
    let valid = validate_citation(MERGE, &no_ev(LINE_MERGE, "2026-11-13"))
        .expect("le merge doit passer M1–M8");
    assert_eq!(valid.status, "vérifié");
    assert!(valid.statement.contains("e2e9c14"));
}

// --- Cas rejetés : les 4 fautifs du Discover §5.3 ---

#[test]
fn fautif_fx1_date_fausse_rejetee_m3() {
    // F-X1 : date 2027-10-08 au lieu de 2027-10-09 — rejet M3, la règle
    // nommée par le design (D-F1-7-6, A-F1-7-1).
    let result = validate_citation(FAUTIF_1, &no_ev(LINE_T2, "2027-10-09"));
    assert_rejet("M3", result);
}

#[test]
fn fautif_fx1_avec_fautif_injecte_rejete_m3_avant_m6() {
    // Même avec le fautif injecté comme référence M6, c'est M3 qui
    // rejette F-X1 en premier (ordre M1 → M7 → M2 → M3 → M4 → M5 → M6 → M8).
    let valid = validate_citation(T2, &no_ev(LINE_T2, "2027-10-09")).expect("T2 valide");
    let planted = (
        valid.statement.as_str(),
        valid.source.as_str(),
        "2027-10-08",
    );
    let result = validate_citation(
        FAUTIF_1,
        &ev(true, LINE_T2, "2027-10-09", &[], Some(planted)),
    );
    assert_rejet("M3", result);
}

#[test]
fn fautif_fx2_sha_altere_rejete_m2() {
    // F-X2 : SHA `e2e9c15…` au lieu de `e2e9c14…` — l'énoncé n'est plus
    // celui que porte la ligne source relue.
    let f = fautif(MERGE, "Merge commit e2e9c14", "Merge commit e2e9c15");
    let result = validate_citation(&f, &no_ev(LINE_MERGE, "2026-11-13"));
    assert_rejet("M2", result);
}

#[test]
fn fautif_fx3_source_absente_rejetee_m2() {
    // F-X3 : T1 attribué à la mémoire absente de Nardole — M2 en premier
    // (la source citée n'existe pas), puis M4 (A-F1-7-2).
    let f = fautif(
        T1,
        "**Source :** `~/side-chats/500abaec-457d-4224-97d9-ca13271d5f40/MEMORY.md:38`",
        "**Source :** `side-chats/Nardole/MEMORY.md — absent (0 octet, seq F1-0 1055)`",
    );
    let result = validate_citation(&f, &ev(false, "", "inconnue", &[], None));
    assert_rejet("M2", result);
}

#[test]
fn fautif_fx4_statut_faux_rejete_m4() {
    // F-X4 : T3 avec le statut « vérifié par Clara » — le statut n'est
    // pas porté par la source.
    let f = fautif(
        T3,
        "**Statut :** consigné",
        "**Statut :** vérifié par Clara",
    );
    let result = validate_citation(&f, &no_ev(LINE_T3, "2026-10-09"));
    assert_rejet("M4", result);
}

#[test]
fn fautif_m6_citation_egale_au_fautif() {
    // M6, le filet : une citation qui passe M1–M5 mais EST le fait fautif
    // planté est rejetée M6.
    let valid = validate_citation(T2, &no_ev(LINE_T2, "2027-10-09")).expect("T2 valide");
    let planted = (
        valid.statement.as_str(),
        valid.source.as_str(),
        valid.date.as_str(),
    );
    let result = validate_citation(T2, &ev(true, LINE_T2, "2027-10-09", &[], Some(planted)));
    assert_rejet("M6", result);
}

// --- Cas limites §5.4 ---

#[test]
fn limite_a_contradiction_portee() {
    // (a) — la contradiction 10:46/10:50/10:55 est portée avec le statut
    // `contredit`, jamais une version choisie silencieusement.
    assert!(LINE_T1_C1046.contains("2026-10-17 ~10:46 EDT"));
    assert!(LINE_T1_C1055.contains("2026-10-17 ~10:55 EDT"));
    let corr: [Corroboration; 2] = [
        (
            "~/memory/2026-10-17.md:657",
            "2026-10-17 ~10:46 EDT",
            "vérifié",
        ),
        (
            "~/side-chats/2428b187-722b-427a-8ad3-460bdce2a208/MEMORY.md:67",
            "2026-10-17 ~10:55 EDT",
            "vérifié",
        ),
    ];
    validate_citation(T1, &ev(true, LINE_T1, "2026-10-17", &corr, None))
        .expect("(a) contradiction portée : T1 passe avec contredit");
}

#[test]
fn limite_a_contradiction_lissee_rejetee_m5() {
    // (a) négatif — la même citation avec le statut `vérifié` lisse la
    // contradiction : rejet M5.
    let corr: [Corroboration; 2] = [
        (
            "~/memory/2026-10-17.md:657",
            "2026-10-17 ~10:46 EDT",
            "vérifié",
        ),
        (
            "~/side-chats/2428b187-722b-427a-8ad3-460bdce2a208/MEMORY.md:67",
            "2026-10-17 ~10:55 EDT",
            "vérifié",
        ),
    ];
    let f = fautif(T1, "**Statut :** contredit", "**Statut :** vérifié");
    let result = validate_citation(&f, &ev(true, LINE_T1, "2026-10-17", &corr, None));
    assert_rejet("M5", result);
}

#[test]
fn limite_b_absence_consignée() {
    // (b) — la mémoire de Nardole est absente (0 octet) : la citation
    // consigne l'absence, elle ne prétend pas retrouver le fait.
    let valid = validate_citation(LIMITE_ABSENT, &ev(false, "", "inconnue", &[], None))
        .expect("(b) absence consignée : la citation d'une absence passe M1–M8");
    assert_eq!(valid.status, "absent");
    assert_eq!(valid.date, "inconnue");
}

#[test]
fn limite_b_absence_fausse_rejetee_m2() {
    // (b) négatif — un statut `absent` sur une source qui existe est une
    // fausse absence : rejet M2.
    let result = validate_citation(LIMITE_ABSENT, &ev(true, LINE_T2, "2027-10-09", &[], None));
    assert_rejet("M2", result);
}

#[test]
fn limite_c_source_bougee_signalee() {
    // (c) — pointeur d'inventaire F1-0 seq 711 périmé (ID court),
    // re-résolu vers la source au fichier ; le déplacement est nommé.
    let valid = validate_citation(LIMITE_BOUGEE, &no_ev(LINE_T3, "2026-10-09"))
        .expect("(c) source bougée : la citation passe avec périmé");
    assert_eq!(valid.status, "périmé");
}

#[test]
fn limite_c_perime_sans_deplacement_rejete_m4() {
    // (c) négatif — un statut `périmé` sans déplacement nommé dans la
    // Vérification : rejet M4.
    let f = fautif(
        LIMITE_BOUGEE,
        "Pointeur d'inventaire F1-0 seq 711 périmé (ID court `6f410ddd`) — re-résolu vers cette source au fichier ; l'entrée d'inventaire est périmée, le fait est re-vérifié ici.",
        "Ligne 146 relue : le texte correspond, l'ID complet est celui que porte la ligne.",
    );
    let result = validate_citation(&f, &no_ev(LINE_T3, "2026-10-09"));
    assert_rejet("M4", result);
}

#[test]
fn limite_d_fait_duplique_dedoupliqué() {
    // (d) — le même fait existe en miroir (world.md:69, mêmes valeurs,
    // même date) : une seule citation fait foi, le duplicata est nommé.
    // Le duplicata porte bien la même date du fait (2027-10-09) dans sa ligne relue.
    assert!(LINE_DUPLIQUE.contains("2027-10-09"));
    let corr: [Corroboration; 1] = [("~/memory/bank/world.md:69", "2027-10-09", "vérifié")];
    let valid = validate_citation(
        LIMITE_DUPLIQUE,
        &ev(true, LINE_T2, "2027-10-09", &corr, None),
    )
    .expect("(d) fait dupliqué : la citation passe, le duplicata est nommé");
    assert_eq!(valid.status, "vérifié");
}

#[test]
fn limite_e_fait_a_date_future() {
    // (e) — le token expire le 2027-02-07, après la citation : statut
    // `à venir`.
    let valid = validate_citation(LIMITE_FUTUR, &no_ev(LINE_FUTUR, "2026-11-09"))
        .expect("(e) date future : la citation passe avec à venir");
    assert_eq!(valid.status, "à venir");
    assert_eq!(valid.date, "2027-02-07");
}

#[test]
fn limite_e_avenir_passe_rejete_m4() {
    // (e) négatif — un statut `à venir` sur une date déjà advenue : rejet M4.
    let f = fautif(
        LIMITE_FUTUR,
        "**Date :** 2027-02-07",
        "**Date :** 2026-11-09",
    );
    let result = validate_citation(&f, &no_ev(LINE_FUTUR, "2026-11-09"));
    assert_rejet("M4", result);
}

#[test]
fn limite_f_fait_sans_date() {
    // (f) — la ligne ne porte aucune date d'établissement du fait : la
    // date est « inconnue », jamais inférée.
    let valid = validate_citation(LIMITE_SANS_DATE, &no_ev(LINE_SANS_DATE, "inconnue"))
        .expect("(f) sans date : la citation passe avec inconnue");
    assert_eq!(valid.status, "consigné");
    assert_eq!(valid.date, "inconnue");
}

// --- Cas limites de forme ---

#[test]
fn limite_document_vide_rejete_m1() {
    let result = validate_citation("", &no_ev(LINE_T2, "2027-10-09"));
    assert_rejet("M1", result);
}

#[test]
fn limite_sans_limites_rejetee_m8() {
    // Dossier sans limites nommées : la section existe mais son corps est vide.
    let f = fautif(
        T2,
        "Elle ne prouve pas que le domaine est encore valide aujourd'hui (la capture date du 2026-11-06) ; elle ne prouve pas le renouvellement automatique futur ; elle ne prouve rien sur les deux autres domaines de la ligne.",
        "",
    );
    let result = validate_citation(&f, &no_ev(LINE_T2, "2027-10-09"));
    assert_rejet("M8", result);
}

#[test]
fn limite_jugement_rejete_m7() {
    // La mémoire ne juge pas : un « Verdict » non nié, même avec une
    // capitale, est rejeté M7 (leçon F1-5).
    let f = fautif(
        T2,
        "## Ce que la fonction n'a pas fait\n\nLa fonction n'a pas jugé",
        "## Ce que la fonction n'a pas fait\n\n**Verdict : le fait est vrai.**\n\nLa fonction n'a pas jugé",
    );
    let result = validate_citation(&f, &no_ev(LINE_T2, "2027-10-09"));
    assert_rejet("M7", result);
}

// --- Journal : action_taken, 12e type ---

#[test]
fn douze_types_dont_action_taken() {
    assert_eq!(JOURNAL_EVENT_TYPES.len(), 12);
    assert!(JOURNAL_EVENT_TYPES.contains(&"action_taken"));
    assert!(JOURNAL_EVENT_TYPES.contains(&"vision_held"));
    assert!(JOURNAL_EVENT_TYPES.contains(&"fact_recalled"));
    assert!(JOURNAL_EVENT_TYPES.contains(&"closure_pulse"));
    assert!(JOURNAL_EVENT_TYPES.contains(&"merge_executed"));
    // La liste du module Mémoire est la même que celle du routeur —
    // une dérive entre les deux serait une seconde vérité.
    assert_eq!(JOURNAL_EVENT_TYPES, EVENT_TYPES);
}
