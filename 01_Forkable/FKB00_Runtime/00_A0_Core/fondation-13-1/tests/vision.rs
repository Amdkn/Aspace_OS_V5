//! Suite de la fonction Vision (D-N055 F1-8, H-M3).
//!
//! Cas passants : les 3 cas d'essai du Discover §5.2 (T1 cohérence F1-7
//! registre ↔ journal ↔ master ↔ reçu ; T2 seuils D-N055/D-N053 non
//! franchis sur leurs ancres ; T3 divergence classée N2 portée — doivent
//! passer V1–V8). Cas rejetés : les 4 fautifs du Discover §5.3, dérivés
//! chacun par UNE SEULE différence (raisons nommées : V3 ancre fausse,
//! V2 seq inexistant, V1 lecture non datée, V4 divergence lissée), dont
//! le fait fautif planté F-V1 (ancre journal 938 pour D-N053, D-F1-8-6,
//! amendement A-F1-8-1). Cas limites (§5.4) : (a) master qui bouge
//! (dérive datée, pas contradiction), (b) N2 ombre classée, (c) fenêtre
//! L00 trouée (absence consignée), (d) fuseaux normalisés (EDT périmé),
//! (e) `pulse_2110` portée non re-vérifiée, (f) fiche/manifeste périmés
//! portés.
//!
//! Les états sont construits en Rust (données injectées) — la CLI
//! `hold-vision` les rend depuis les fichiers ; le dossier fautif
//! (`fixtures/vision-fautif-1.md`) est lu par `parse_fautif`, comme la
//! CLI le lit au fichier.

use r10_validator::vision::{
    normalize_timestamp, parse_fautif, threshold_after, validate_vision, Comparison,
    DatedReading, Divergence, Outcome, PlantedFautif, Threshold, VisionState,
};
use r10_validator::parse_iso8601_offset;

const FAUTIF_1: &str = include_str!("fixtures/vision-fautif-1.md");

/// Instant de référence des cas : 2026-11-13T02:45:00-05:00 — avant les
/// seuils D-N053 (~09:00) et D-N055 (~13:52).
fn now() -> i64 {
    parse_iso8601_offset("2026-11-13T02:45:00-05:00").unwrap()
}

const ANCHOR_D_N055: &str = "2026-11-13T01:52:00-05:00";
const THRESHOLD_D_N055: &str = "2026-11-13T13:52:00-05:00";
const ANCHOR_D_N053: &str = "2026-11-12T21:00:00-05:00";
const THRESHOLD_D_N053: &str = "2026-11-13T09:00:00-05:00";
const READ_AT: &str = "2026-11-13T02:40:00-05:00";

fn readings() -> Vec<DatedReading<'static>> {
    vec![
        DatedReading {
            source: "registre (ligne 938)",
            value: "939 lignes ; journal 938 : merge PR #50, 055745b, 01:47:15 EST",
            read_at: READ_AT,
        },
        DatedReading {
            source: "journal-router (seq 37)",
            value: "37 lignes, seq 1–37 contigus ; seq 37 : merge_executed D-N055-F1-7-MERGE à 2026-11-13T01:47:15-05:00",
            read_at: READ_AT,
        },
        DatedReading {
            source: "master (injecté par l'opérateur)",
            value: "master 7feb8b0fc916750ee00eadc5c5801200dc8462cb ; 0 PR ouverte",
            read_at: READ_AT,
        },
    ]
}

fn divergences() -> Vec<Divergence<'static>> {
    vec![
        Divergence {
            name: "D-N021/24/26/32 — silence 12 j",
            version_a: "L00 #702 : classés (chemin 12e retiré, ordre S0 00:32 EST 11-11)",
            version_b: "N2 Run #484 : W1 ANOMALIE portée (12 j 7 h)",
            status: "classée",
            source: "ordre S0 00:32 EST 11-11 ; L00 Runs #642/#643 ; N2 #484",
            date: "2026-11-11",
        },
        Divergence {
            name: "N2 ombre vs L00 (W1 ANOMALIE D-N021)",
            version_a: "L00 #702 : D-N021 classé",
            version_b: "N2 #484 : W1 ANOMALIE D-N021 (12 j 7 h)",
            status: "classée",
            source: "L00 #702",
            date: "2026-11-13",
        },
        Divergence {
            name: "Écart #601 (ligne absente L00-ETAT)",
            version_a: "L00-ETAT : ligne #601 absente",
            version_b: "consignation attendue : ligne #601 présente",
            status: "ouverte",
            source: "L00 #702",
            date: "2026-11-13",
        },
        Divergence {
            name: "Fiche/manifeste — instance F1-7",
            version_a: "fiche : F1-7 PR ouverte, non mergée ; manifeste : F1-7 jugement à venir",
            version_b: "PR #50 mergée 055745b, jugement VALIDÉE, journal 938",
            status: "résolue",
            source: "fiche + manifeste relus au fichier",
            date: "2026-11-13",
        },
        Divergence {
            name: "Fiche/manifeste — dérive structurelle",
            version_a: "aucun chemin d'atterrissage ne met à jour la fiche",
            version_b: "fiche et manifeste à jour à chaque atterrissage",
            status: "ouverte",
            source: "Discover F1-8 §2.7",
            date: "2026-11-13",
        },
        Divergence {
            name: "L00 cadence déclarée 1 h vs observée ~40 min",
            version_a: "cron l00-veille-w1-w7 : interval@1h déclaré",
            version_b: "runs #699 00:17 → #702 01:57 observés ~40 min",
            status: "ouverte",
            source: "cron.list + L00-ETAT",
            date: "2026-11-13",
        },
        Divergence {
            name: "Workgraph Sheet ↔ miroir (Bill/Coordinateur)",
            version_a: "miroir : Bill PRÉSENT, Coordinateur ABSENT",
            version_b: "Sheet (02:13:32 EST) : Bill ABSENT, Coordinateur ×2 PRÉSENT",
            status: "ouverte",
            source: "DISCOVER-F1-8.md §2.5",
            date: "2026-11-13",
        },
        Divergence {
            name: "Jugement F1-5 absent comme judgment_rendered au journal",
            version_a: "journal-router : aucun judgment_rendered F1-5",
            version_b: "closure_pulse seq 20 le porte comme preuve",
            status: "classée",
            source: "Discover F1-7 §3.4",
            date: "2026-11-12",
        },
        Divergence {
            name: "Supabase injoignable (point rouge 08:44 EST 11-11)",
            version_a: "L00 Run #604 : injoignable 5/5",
            version_b: "service attendu joignable",
            status: "ouverte",
            source: "L00 #702",
            date: "2026-11-11",
        },
        Divergence {
            name: "Design D-N046 non livré",
            version_a: "L00 #702 : À surveiller",
            version_b: "design livré",
            status: "ouverte",
            source: "L00 #702",
            date: "2026-11-13",
        },
        Divergence {
            name: "Désarchivage V4 (#107) en attente",
            version_a: "issue #107 ouverte, décision S0 en attente",
            version_b: "décision rendue",
            status: "ouverte",
            source: "L00 #702 + issue #107",
            date: "2026-11-06",
        },
    ]
}

fn known_divergences() -> Vec<&'static str> {
    divergences().iter().map(|d| d.name).collect()
}

fn absences() -> Vec<&'static str> {
    vec![
        "Reçus PR #38/#39 absents (grep SHAs 1606405/bfeae74 = 0, L00 #702)",
        "21 runs L00 absents (#657–#666, #673, #675–#684)",
        "correction jamais émis au journal (0/37 événements)",
        "pulse_2110 : entrée d'hier, non re-vérifiée, non re-routée (L00 #702)",
    ]
}

fn known_absences() -> Vec<&'static str> {
    absences()
}

fn limits() -> Vec<&'static str> {
    vec![
        "Les 13 mémoires — la vision ne les re-vérifie pas",
        "Le bundle / shared brain — hors périmètre",
        "FKB02 — hors périmètre",
        "La Google Sheet Workgraph — non relue en direct (0 appel réseau) ; lecture citée du Discover (02:13:32 EST)",
        "La cause des 21 runs L00 absents — non établie par ce pas",
    ]
}

fn thresholds_valid() -> Vec<Threshold<'static>> {
    vec![
        Threshold {
            dispatch_id: "D-N055",
            anchor_journal: 938,
            anchor_names_dispatch: true,
            anchor_dispatch_named: "D-N055",
            anchor_at: ANCHOR_D_N055,
            threshold_at: THRESHOLD_D_N055,
            crossed: false,
            correct_anchor: "journal 938, ~01:52, seuil ~13:52, non franchi",
        },
        Threshold {
            dispatch_id: "D-N053",
            anchor_journal: 930,
            anchor_names_dispatch: true,
            anchor_dispatch_named: "D-N053",
            anchor_at: ANCHOR_D_N053,
            threshold_at: THRESHOLD_D_N053,
            crossed: false,
            correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
        },
    ]
}

fn base_state<'a>(
    readings: &'a [DatedReading<'a>],
    comparisons: &'a [Comparison<'a>],
    divergences: &'a [Divergence<'a>],
    thresholds: &'a [Threshold<'a>],
    known_divergences: &'a [&'a str],
    absences: &'a [&'a str],
    known_absences: &'a [&'a str],
    limits: &'a [&'a str],
) -> VisionState<'a> {
    VisionState {
        readings,
        comparisons,
        divergences,
        thresholds,
        known_divergences,
        absences,
        known_absences,
        limits,
        claims_complete: false,
        claims_resolution: false,
        modifies_source: false,
        consigns_receipt: false,
        planted_fautif: None,
        max_seq: 37,
    }
}

#[test]
fn t1_coherence_f1_7_passe() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let comparisons = vec![
        Comparison {
            name: "registre ligne 938 = journal seq 37",
            left: DatedReading {
                source: "registre, ligne 938",
                value: "merge PR #50, 055745b, 01:47:15 EST",
                read_at: READ_AT,
            },
            right: DatedReading {
                source: "journal-router, seq 37",
                value: "merge_executed PR #50, 055745b, 2026-11-13T01:47:15-05:00",
                read_at: READ_AT,
            },
            outcome: Outcome::Coherent,
            cited_seq: Some(37),
        },
        Comparison {
            name: "journal seq 37 = reçu G-20261112-035",
            left: DatedReading {
                source: "journal-router, seq 37",
                value: "merge_executed PR #50, 055745b, 2026-11-13T01:47:15-05:00",
                read_at: READ_AT,
            },
            right: DatedReading {
                source: "ledger local, G-20261112-035.json",
                value: "sha 055745b853495c38f0aaa0ae6c3d2adad9e89177, merge PR #50",
                read_at: READ_AT,
            },
            outcome: Outcome::Coherent,
            cited_seq: Some(37),
        },
        Comparison {
            name: "master au merge vs master lu",
            left: DatedReading {
                source: "master au merge",
                value: "055745b au merge, 01:47:15 EST",
                read_at: "2026-11-13T01:47:15-05:00",
            },
            right: DatedReading {
                source: "master lu",
                value: "7feb8b0fc916750ee00eadc5c5801200dc8462cb lu à 2026-11-13T02:40:00-05:00",
                read_at: READ_AT,
            },
            outcome: Outcome::Drift,
            cited_seq: None,
        },
    ];
    let state = base_state(
        &readings, &comparisons, &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let valid = validate_vision(&state, now()).unwrap();
    assert_eq!(valid.unported_contradictions, 0);
    assert_eq!(valid.comparisons, 3);
}

#[test]
fn t2_seuils_non_franchis_passe() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = thresholds_valid();
    let comparisons = vec![
        Comparison {
            name: "ancre D-N055 = journal 938",
            left: DatedReading {
                source: "registre, ligne 938",
                value: "journal 938 nomme D-N055 (F1-7 CLOSE, merge PR #50)",
                read_at: READ_AT,
            },
            right: DatedReading {
                source: "journal-router, seq 37",
                value: "seq 37 merge_executed D-N055-F1-7-MERGE à 2026-11-13T01:47:15-05:00",
                read_at: READ_AT,
            },
            outcome: Outcome::Coherent,
            cited_seq: Some(37),
        },
        Comparison {
            name: "ancre D-N053 = journal 930",
            left: DatedReading {
                source: "registre, ligne 930",
                value: "journal 930 nomme D-N053 (F2 CLOSE, merge PR #46)",
                read_at: READ_AT,
            },
            right: DatedReading {
                source: "L00 Run #702",
                value: "D-N053 dernier événement nommant = journal 930 ~21:00, seuil ~09:00 EST 11-13",
                read_at: READ_AT,
            },
            outcome: Outcome::Coherent,
            cited_seq: None,
        },
    ];
    let state = base_state(
        &readings, &comparisons, &divergences, &thresholds, &known, &absences, &known_abs,
        &limits,
    );
    let valid = validate_vision(&state, now()).unwrap();
    assert_eq!(valid.thresholds, 2);
    assert_eq!(valid.unported_contradictions, 0);
}

#[test]
fn t3_divergence_classee_passee() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let comparisons = vec![Comparison {
        name: "N2 Run #484 vs L00 Run #702 (D-N021)",
        left: DatedReading {
            source: "L00-N2-ETAT, Run #484",
            value: "W1 ANOMALIE D-N021 (12 j 7 h), label « 2026-11-13 03:13 EDT » → 2026-11-13T02:13:00-05:00 (étiquette périmée)",
            read_at: READ_AT,
        },
        right: DatedReading {
            source: "L00-ETAT, Run #702",
            value: "D-N021 classé (chemin 12e retiré, ordre S0 00:32 EST 11-11)",
            read_at: READ_AT,
        },
        outcome: Outcome::Divergent,
        cited_seq: None,
    }];
    let state = base_state(
        &readings, &comparisons, &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let valid = validate_vision(&state, now()).unwrap();
    assert_eq!(valid.divergences, 11);
    assert_eq!(valid.unported_contradictions, 0);
}

#[test]
fn f_v1_rejet_v3_ancre_fausse() {
    // Le fautif planté (A-F1-8-1) : UNE SEULE différence — l'ancre du
    // seuil D-N053 (journal 938 au lieu de journal 930). Aucune autre
    // règle ne doit se déclencher avant V3.
    let claim = parse_fautif(FAUTIF_1).unwrap();
    assert_eq!(claim.dispatch_id, "D-N053");
    assert_eq!(claim.anchor_journal, 938);
    assert_eq!(claim.anchor_dispatch_named, "D-N055");
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = vec![Threshold {
        dispatch_id: "D-N053",
        anchor_journal: claim.anchor_journal,
        anchor_names_dispatch: false,
        anchor_dispatch_named: "D-N055",
        anchor_at: ANCHOR_D_N055,
        threshold_at: THRESHOLD_D_N055,
        crossed: true,
        correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
    }];
    let mut state = base_state(
        &readings, &[], &divergences, &thresholds, &known, &absences, &known_abs, &limits,
    );
    state.planted_fautif = Some(PlantedFautif {
        dispatch_id: "D-N053",
        anchor_journal: 938,
        crossed: true,
    });
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V3");
    assert!(err.detail.contains("journal 938 nomme D-N055, pas D-N053"));
    assert!(err.detail.contains("journal 930"));
}

#[test]
fn f_v2_rejet_v2_seq_inexistant() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let comparisons = vec![Comparison {
        name: "journal-router seq 38 = merge PR #50",
        left: DatedReading {
            source: "journal-router, seq 38",
            value: "merge_executed PR #50",
            read_at: READ_AT,
        },
        right: DatedReading {
            source: "registre, ligne 938",
            value: "merge PR #50, 055745b",
            read_at: READ_AT,
        },
        outcome: Outcome::Coherent,
        cited_seq: Some(38),
    }];
    let state = base_state(
        &readings, &comparisons, &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V2");
    assert!(err.detail.contains("n'existe pas"));
}

#[test]
fn f_v3_rejet_v1_lecture_non_datee() {
    // Master 765ac89, 0 PR ouverte — sans horodatage de lecture.
    let readings = vec![DatedReading {
        source: "master",
        value: "765ac89, 0 PR ouverte",
        read_at: "",
    }];
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let state = base_state(
        &readings, &[], &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V1");
}

#[test]
fn f_v4_rejet_v4_divergence_lissee() {
    // UNE SEULE différence par rapport à un état valide : la comparaison
    // Workgraph affirme « Sheet = miroir » (cohérente) alors que la
    // divergence est portée (Bill/Coordinateur divergent dans les deux sens).
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let comparisons = vec![Comparison {
        name: "Workgraph : Sheet = miroir",
        left: DatedReading {
            source: "miroir Workgraph",
            value: "Bill PRÉSENT, Coordinateur ABSENT",
            read_at: READ_AT,
        },
        right: DatedReading {
            source: "Google Sheet",
            value: "Bill ABSENT, Coordinateur ×2 PRÉSENT",
            read_at: READ_AT,
        },
        outcome: Outcome::Coherent,
        cited_seq: None,
    }];
    let state = base_state(
        &readings, &comparisons, &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V4");
    assert!(err.detail.contains("lissée"));
}

#[test]
fn v5_filet_attrape_fautif_affirme_vrai() {
    // Le filet V5 : l'appelant affirme (à tort) que l'ancre 938 nomme
    // D-N053 — V3 passe sur l'affirmation, V5 attrape le fautif planté.
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = vec![Threshold {
        dispatch_id: "D-N053",
        anchor_journal: 938,
        anchor_names_dispatch: true,
        anchor_dispatch_named: "D-N053",
        anchor_at: ANCHOR_D_N055,
        threshold_at: THRESHOLD_D_N055,
        crossed: true,
        correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
    }];
    let mut state = base_state(
        &readings, &[], &divergences, &thresholds, &known, &absences, &known_abs, &limits,
    );
    state.planted_fautif = Some(PlantedFautif {
        dispatch_id: "D-N053",
        anchor_journal: 938,
        crossed: true,
    });
    // Après le seuil (13:52) : le franchissement affirmé est cohérent
    // avec l'instant — seule V5 peut encore rejeter.
    let late = parse_iso8601_offset("2026-11-13T14:00:00-05:00").unwrap();
    let err = validate_vision(&state, late).unwrap_err();
    assert_eq!(err.rule, "V5");
}

#[test]
fn v6_tranche_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let mut state = base_state(
        &readings, &[], &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    state.claims_resolution = true;
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V6");
}

#[test]
fn v6_modifie_source_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let mut state = base_state(
        &readings, &[], &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    state.modifies_source = true;
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V6");
}

#[test]
fn v7_absence_tue_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = vec!["21 runs L00 absents (#657–#666, #673, #675–#684)"];
    let known_abs = known_absences();
    let limits = limits();
    let state = base_state(
        &readings, &[], &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V7");
}

#[test]
fn v8_sans_limites_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits: Vec<&str> = vec![];
    let state = base_state(
        &readings, &[], &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V8");
}

#[test]
fn v4_divergence_non_portee_rejet() {
    let readings = readings();
    let mut divergences = divergences();
    divergences.retain(|d| d.name != "Supabase injoignable (point rouge 08:44 EST 11-11)");
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let state = base_state(
        &readings, &[], &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V4");
    assert!(err.detail.contains("non portée"));
}

#[test]
fn v1_avant_v3_ordre() {
    // L'ordre V1 → V6 → V2 → V3 est respecté : un état qui viole V1 et
    // V3 est rejeté V1, pas V3.
    let readings = vec![DatedReading {
        source: "registre",
        value: "939 lignes",
        read_at: "",
    }];
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = vec![Threshold {
        dispatch_id: "D-N053",
        anchor_journal: 938,
        anchor_names_dispatch: false,
        anchor_dispatch_named: "D-N055",
        anchor_at: ANCHOR_D_N055,
        threshold_at: THRESHOLD_D_N055,
        crossed: true,
        correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
    }];
    let state = base_state(
        &readings, &[], &divergences, &thresholds, &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V1");
}

#[test]
fn v3_seuil_incoherent_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = vec![Threshold {
        dispatch_id: "D-N053",
        anchor_journal: 930,
        anchor_names_dispatch: true,
        anchor_dispatch_named: "D-N053",
        anchor_at: ANCHOR_D_N053,
        threshold_at: "2026-11-13T02:15:00-05:00",
        crossed: false,
        correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
    }];
    let state = base_state(
        &readings, &[], &divergences, &thresholds, &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V3");
}

#[test]
fn v3_franchissement_avant_seuil_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = vec![Threshold {
        dispatch_id: "D-N053",
        anchor_journal: 930,
        anchor_names_dispatch: true,
        anchor_dispatch_named: "D-N053",
        anchor_at: ANCHOR_D_N053,
        threshold_at: THRESHOLD_D_N053,
        crossed: true,
        correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
    }];
    let state = base_state(
        &readings, &[], &divergences, &thresholds, &known, &absences, &known_abs, &limits,
    );
    let err = validate_vision(&state, now()).unwrap_err();
    assert_eq!(err.rule, "V3");
}

#[test]
fn v3_seuil_depasse_non_franchi_rejet() {
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let thresholds = thresholds_valid();
    let state = base_state(
        &readings, &[], &divergences, &thresholds, &known, &absences, &known_abs, &limits,
    );
    // Après le seuil D-N053 (09:00), le porter non franchi est faux.
    let late = parse_iso8601_offset("2026-11-13T10:00:00-05:00").unwrap();
    let err = validate_vision(&state, late).unwrap_err();
    assert_eq!(err.rule, "V3");
}

#[test]
fn limite_master_bouge_drift_passee() {
    // §5.4a : le master a bougé entre deux lectures — une dérive datée,
    // pas une contradiction.
    let readings = readings();
    let divergences = divergences();
    let known = known_divergences();
    let absences = absences();
    let known_abs = known_absences();
    let limits = limits();
    let comparisons = vec![Comparison {
        name: "master 02:06 vs master 02:15",
        left: DatedReading {
            source: "master lu à 02:06",
            value: "765ac89",
            read_at: "2026-11-13T02:06:00-05:00",
        },
        right: DatedReading {
            source: "master lu à 02:15",
            value: "e743a29",
            read_at: "2026-11-13T02:15:00-05:00",
        },
        outcome: Outcome::Drift,
        cited_seq: None,
    }];
    let state = base_state(
        &readings, &comparisons, &divergences, &[], &known, &absences, &known_abs, &limits,
    );
    let valid = validate_vision(&state, now()).unwrap();
    assert_eq!(valid.unported_contradictions, 0);
}

#[test]
fn limite_fuseaux_normalises() {
    // §5.4d : N2 « 03:13 EDT » en heure d'hiver = 02:13 EST, étiquette périmée.
    let n = normalize_timestamp("2026-11-13 03:13 EDT").unwrap();
    assert_eq!(n.iso, "2026-11-13T02:13:00-05:00");
    assert_eq!(n.label_status, "périmé");
    // Un horodatage non normalisable est porté périmé, pas rejeté comme instant.
    assert_eq!(normalize_timestamp("hier vers 2 h"), None);
}

#[test]
fn seuil_plus_12h_coherent() {
    assert_eq!(
        threshold_after(ANCHOR_D_N055).as_deref(),
        Some(THRESHOLD_D_N055)
    );
    assert_eq!(
        threshold_after(ANCHOR_D_N053).as_deref(),
        Some(THRESHOLD_D_N053)
    );
}
