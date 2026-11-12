//! Suite de la fonction Découvrir (D-N055 F1-4, H-M3).
//!
//! Cas passant : ce Discover-ci (`discover-f1-4.md` — copie byte-identique
//! de `v4-factory/evidence/D-N055/DISCOVER-F1-4.md` à l'exécution F1-4,
//! 32 219 o, 158 lignes) doit passer D1–D8. Cas rejetés : les 5 fautifs du
//! Discover §6, dérivés chacun par UNE SEULE différence (un seul
//! remplacement, vérifié `count == 1`) — ils doivent être rejetés avec la
//! raison nommée (D2, D4, D7, D6, D5), dont le Discover fautif planté n° 1
//! (fait non vérifié, D-F1-4-4, amendement A-F1-4-1).
//!
//! Les SHA complets du Discover sont résolus par le résolveur statique
//! (vérifiés à l'API par l'opérateur : merge PR #30 `4668305…`, merge
//! PR #26 `1f89b56…`, Master HEAD `d972235…`).

use r10_validator::discover::validate_discover;
use r10_validator::StaticShaResolver;

const BASE: &str = include_str!("fixtures/discover-f1-4.md");

const SHAS: [&str; 3] = [
    "4668305c988422bff91e0a78c1327c7a7875bdd9",
    "1f89b56890ebfeb2cd06a0c963656cbd57f64a64",
    "d97223538ce905db8df9d0efab57718dcfeae770",
];

fn resolver() -> StaticShaResolver {
    StaticShaResolver::new(SHAS.iter().map(|s| s.to_string()))
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
fn discover_f1_4_passe_d1_d8() {
    let valid = validate_discover(BASE, &resolver()).unwrap();
    assert_eq!(valid.mission, "D-N055 F1-4");
    assert_eq!(valid.shas_checked, 3);
}

#[test]
fn fautif_1_fait_non_verifie_rejete_d2() {
    // A-F1-4-1 : le merge de la PR #30 affirmé sans ancre, repris du récit
    // de l'exécutant F1-3 — le SHA complet et la vérification à l'API
    // disparaissent du §2.
    let f = fautif(
        BASE,
        "PR #30 mergée, merge commit `4668305c988422bff91e0a78c1327c7a7875bdd9` (vérifié à l'API ce tour : merged true, merged_at 2026-11-11T07:02:50Z = 02:02:50 EST), 2 parents `63b5816` + `12b7928` (DVG-01, true merge)",
        "PR #30 mergée, d'après le récit de l'exécutant F1-3, sans vérification à l'API",
    );
    let err = validate_discover(&f, &resolver()).unwrap_err();
    assert_eq!(err.rule, "D2");
}

#[test]
fn fautif_2_decision_tranchee_rejetee_d4() {
    // Une décision « ADOPTÉE » ajoutée au §8 — le Discover propose, il ne
    // tranche pas.
    let f = fautif(
        BASE,
        "1. **Qu'est-ce qu'un Discover produit par le 1 ?** Proposé : la forme §3 (en-tête + §0–§10) et le contenu exigible (ancre par fait, corrections en avant, limites nommées). — À trancher au design.",
        "1. **Qu'est-ce qu'un Discover produit par le 1 ?** Proposé : la forme §3 (en-tête + §0–§10) et le contenu exigible (ancre par fait, corrections en avant, limites nommées). — À trancher au design.\n\n**Décision D-F1-4-1 : ADOPTÉE.**",
    );
    let err = validate_discover(&f, &resolver()).unwrap_err();
    assert_eq!(err.rule, "D4");
}

#[test]
fn fautif_3_source_citee_non_lue_rejetee_d7() {
    // Le Discover maître de Bill cité au §8 / §6.3 sans avoir été lu :
    // son attestation « lu en entier » disparaît de sa ligne du §10
    // (ancre : leçon §0.4.5.1 — 200 caractères lus, conclusion fausse).
    let f = fautif(
        BASE,
        "- `architecture-compagnons/discover-fondation-13-1.md` — lu en entier (Discover maître de Bill ; 67 267 o, 407 lignes au `wc` ce tour — 63 269 o, 398 lignes au design signé, croissance = §0.4.5).",
        "- `architecture-compagnons/discover-fondation-13-1.md` — cité au §8 (Discover maître de Bill ; 67 267 o, 407 lignes — §6.3, non lu en entier).",
    );
    let err = validate_discover(&f, &resolver()).unwrap_err();
    assert_eq!(err.rule, "D7");
}

#[test]
fn fautif_4_correction_silencieuse_rejetee_d6() {
    // Le compte 14 214 o réécrit en 14 360 o sans note datée : la valeur
    // d'origine et l'écart de 146 o disparaissent du §2.
    let f = fautif(
        BASE,
        " (14 360 o mesurés au `wc -c` ce tour — le registre porte 14 214 o, écart de 146 o porté ici en avant, à re-vérifier : le compte du registre est une mesure d'époque, pas une constante)",
        " (14 360 o mesurés au `wc -c` ce tour)",
    );
    let err = validate_discover(&f, &resolver()).unwrap_err();
    assert_eq!(err.rule, "D6");
}

#[test]
fn fautif_5_execution_deguisee_rejetee_d5() {
    // Un reçu consigné par ce Discover — le Discover n'exécute rien.
    let f = fautif(
        BASE,
        "**Ce que ce Discover ne prouve pas (porté honnêtement) :**",
        "**Ce que ce Discover ne prouve pas (porté honnêtement) :**\n\n**Reçu consigné par ce Discover : G-20261112-018 (mission LE1-FAB-D-N055-007).**",
    );
    let err = validate_discover(&f, &resolver()).unwrap_err();
    assert_eq!(err.rule, "D5");
}

#[test]
fn document_vide_rejete_d1() {
    let err = validate_discover("", &resolver()).unwrap_err();
    assert_eq!(err.rule, "D1");
}
