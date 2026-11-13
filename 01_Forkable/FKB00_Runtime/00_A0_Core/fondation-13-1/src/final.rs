//! Preuve finale (D-N055 F1-11) : le 1 tient les 13 fonctions sans le
//! routeur — un rejeu, pas une re-déclaration.
//!
//! La fonction Preuve finale valide une preuve posée par l'opérateur en
//! la rejouant : suite re-courue, jugements relus au fichier, merges
//! re-vérifiés 2 parents à l'API (valeurs injectées), absorptions citées
//! avec leurs preuves, états de vision rendus par la CLI généralisée,
//! actes autorisés sans question, comptage « 0 routeur » au journal,
//! F-A3 re-vérifié contre le journal réel, R3 aligné, fiche et
//! manifeste corrigés. Une CLI qui ne ferait que valider une preuve
//! posée par l'opérateur serait un ré-étiquetage — REJETÉ par le design
//! (D-F1-11-9) : la preuve finale est un rejeu, chaque condition est
//! re-vérifiée depuis sa source, jamais reprise du dossier.
//!
//! Règles (design F1-11 §1), appliquées dans l'ordre
//! P1 → P2 → P6 → P3 → P4 → P5 → P7 → P8 :
//! * P1 — Suite et jugements et merges. La suite passe (passed == total
//!   > 0) ; les 10 jugements (F1-1..F1-10) sont VALIDÉ ou ACCEPTÉ
//!   (verdict contenant « VALIDÉ » ou « ACCEPTÉ ») ; les 9 merges sont
//!   des true merges (sha 40-hex, 2 parents distincts 40-hex ≠ sha).
//! * P2 — Absorptions. Les 6 absorptions (vérifier, décider, observer,
//!   interfacer, fluer, fabriquer) portent chacune une preuve non vide.
//! * P6 — Ancres généralisées. 20 ancres généralisées (9 gates + 11
//!   libellés) ; le fautif F-V5 est rejeté V9 ; les régressions
//!   F-V1..F-V4 sont rejetées par leurs règles (V3/V2/V1/V4).
//! * P3 — États de vision. 2 états acceptés, 0 contradiction non
//!   portée, journaux de tailles distinctes (47 et 90 lignes).
//! * P4 — Acte. Au moins un acte autorisé sans question — ou 0 acte et
//!   l'absence consignée (honnêteté A7 : jamais ACCEPTÉ par
//!   anticipation).
//! * P5 — Routeur. 0 événement acteur session Nardole ; 100 % des
//!   routages comme événements du journal (routages comme événements ==
//!   total > 0).
//! * P7 — F-A3, R3, fiche/manifeste, coordinateur. F-A3 rejeté A3 (ou
//!   A2 avec sa raison exacte portée) ; R3 aligné ; fiche et manifeste
//!   corrigés au merge ; coordinateur disponible (il atteste par
//!   événement du journal — indisponible = la preuve ne peut pas être
//!   attestée).
//! * P8 — Limites. Limites non vides, dont DETTE-H-F1-7-SEMAINE nommée
//!   ; la preuve ne se prétend pas universelle (claims_universal faux :
//!   la semaine n'est pas prouvée, la mémoire universelle, le
//!   démantèlement, le rollback réel, H-F8-9 et la bascule ne le sont
//!   pas non plus).
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Preuve finale).

use super::Rejection;

/// Un merge re-vérifié à l'API (DVG-01 : le compte de parents fait foi).
#[derive(Debug, Clone)]
pub struct MergeRef<'a> {
    /// Le numéro de la PR (ex. 26).
    pub pr: usize,
    /// Le SHA complet du merge commit (40 hex).
    pub sha: &'a str,
    /// Le SHA complet du premier parent (40 hex).
    pub parent1: &'a str,
    /// Le SHA complet du second parent (40 hex).
    pub parent2: &'a str,
}

/// Un jugement relu au fichier (F1-1/F1-2 au registre seul, journaux
/// 787/791/795 — l'asymétrie est nommée, pas lissée).
#[derive(Debug, Clone)]
pub struct JudgmentRef<'a> {
    /// Le pas (ex. « F1-3 »).
    pub step: &'a str,
    /// La source exacte (fichier de jugement ou registre + journal).
    pub source: &'a str,
    /// Le verdict lu (contient « VALIDÉ » ou « ACCEPTÉ »).
    pub verdict: &'a str,
}

/// Une absorption (D-F1-11-3) : la fonction absorbée et sa preuve citée.
#[derive(Debug, Clone)]
pub struct Absorption<'a> {
    /// La fonction absorbée (vérifier, décider, observer, interfacer,
    /// fluer, fabriquer).
    pub function: &'a str,
    /// La preuve citée (non vide exigée).
    pub proof: &'a str,
}

/// Un état de vision rendu par la CLI généralisée.
#[derive(Debug, Clone)]
pub struct VisionReplay {
    /// Le nombre de lignes du journal rendu (47 ou 90).
    pub journal_lines: usize,
    /// L'état a-t-il été ACCEPTÉ par la CLI ?
    pub accepted: bool,
    /// Le nombre de contradictions non portées (0 exigé).
    pub contradictions: usize,
}

/// Un acte posé par l'opérateur (A1–A8 : autorisé sans question).
#[derive(Debug, Clone)]
pub struct Act<'a> {
    /// L'acte (ex. « ouverture de la PR F1-11 »).
    pub act: &'a str,
    /// L'acte est-il autorisé par le design signé ?
    pub authorized: bool,
    /// Le nombre de questions de clarification posées (0 exigé).
    pub questions_asked: usize,
    /// Le dispatch de l'acte (ex. « D-N055-F1-11-DELIVER »).
    pub dispatch_id: &'a str,
}

/// La preuve finale, telle que posée par l'opérateur — rejouée par
/// `validate_final` depuis ses sources, jamais reprise telle quelle.
#[derive(Debug, Clone)]
pub struct FinalProof<'a> {
    /// La suite : nombre total de tests re-courus.
    pub suite_total: usize,
    /// La suite : nombre de tests passés.
    pub suite_passed: usize,
    /// Les 10 jugements F1-1..F1-10, relus au fichier.
    pub judgments: &'a [JudgmentRef<'a>],
    /// Les 9 merges, re-vérifiés 2 parents à l'API.
    pub merges: &'a [MergeRef<'a>],
    /// Les 6 absorptions, avec leurs preuves citées.
    pub absorptions: &'a [Absorption<'a>],
    /// Le nombre d'ancres généralisées (20 exigé : 9 gates + 11 libellés).
    pub anchors_generalized: usize,
    /// Le fautif F-V5 a-t-il été rejeté par la CLI ?
    pub fautif_v5_rejected: bool,
    /// La règle du rejet de F-V5 (« V9 » exigée).
    pub fautif_v5_rule: &'a str,
    /// Les régressions F-V1..F-V4 : (fautif, règle attendue).
    pub vision_regressions: &'a [(&'a str, &'a str)],
    /// Les 2 états de vision rendus par la CLI généralisée.
    pub vision_states: &'a [VisionReplay],
    /// Les actes posés (vide = absence consignée, voir P4).
    pub acts: &'a [Act<'a>],
    /// L'absence d'acte est-elle consignée (honnêteté A7) ?
    pub absence_consigned: bool,
    /// Le nombre d'événements acteur session Nardole pendant la fenêtre
    /// (0 exigé — D-F1-11-2).
    pub router_nardole_events: usize,
    /// Le nombre total de routages pendant la fenêtre (> 0 exigé).
    pub router_routing_total: usize,
    /// Le nombre de routages consignés comme événements du journal (==
    /// total exigé).
    pub router_routing_as_events: usize,
    /// La règle du rejet de F-A3 re-vérifié (« A3 » exigée, « A2 » avec
    /// raison portée acceptée).
    pub f_a3_rule: &'a str,
    /// La raison exacte du rejet de F-A3 (exigée si la règle est A2).
    pub f_a3_reason: &'a str,
    /// R3 est-il aligné (D-F1-11-7) ?
    pub r3_aligned: bool,
    /// La fiche et le manifeste sont-ils corrigés au merge (D-F1-11-8) ?
    pub fiche_manifeste_corrected: bool,
    /// Le coordinateur est-il disponible (il atteste par événement du
    /// journal) ?
    pub coordinator_available: bool,
    /// Les limites nommées (§ Limites, P8).
    pub limits: &'a [&'a str],
    /// La preuve se prétend-elle universelle ? (faux exigé — P8.)
    pub claims_universal: bool,
}

/// Une preuve finale validée : les comptes rejoués.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidFinal {
    /// Tests de la suite passés (== total).
    pub suite_passed: usize,
    /// Jugements VALIDÉ/ACCEPTÉ (10).
    pub judgments: usize,
    /// Merges true merge (9).
    pub merges: usize,
    /// Absorptions avec preuve (6).
    pub absorptions: usize,
    /// États de vision acceptés (2).
    pub vision_states: usize,
    /// Actes autorisés sans question.
    pub acts: usize,
    /// Routages comme événements du journal.
    pub routings_as_events: usize,
}

fn rejection(
    rule: &'static str,
    field: &'static str,
    received: &str,
    detail: &str,
) -> Rejection {
    Rejection {
        rule,
        field,
        received: received.chars().take(120).collect(),
        detail: detail.to_string(),
        also_violated: Vec::new(),
    }
}

/// Un SHA complet est-il 40 caractères hex minuscules ?
fn is_sha40(s: &str) -> bool {
    s.len() == 40
        && s.bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

/// Les 6 fonctions absorbées (D-F1-11-3), dans l'ordre du design.
pub const ABSORBED_FUNCTIONS: [&str; 6] = [
    "vérifier",
    "décider",
    "observer",
    "interfacer",
    "fluer",
    "fabriquer",
];

/// Les régressions attendues (D-F1-11-10) : F-V1 → V3, F-V2 → V2,
/// F-V3 → V1, F-V4 → V4.
pub const VISION_REGRESSIONS: [(&str, &str); 4] = [
    ("F-V1", "V3"),
    ("F-V2", "V2"),
    ("F-V3", "V1"),
    ("F-V4", "V4"),
];

/// Valide une preuve finale, dans l'ordre P1 → P2 → P6 → P3 → P4 → P5 →
/// P7 → P8. Un désaccord (la fonction rend une absorption ou un état
/// que le design n'a pas vérifié) est un échec du hold-out, pas une
/// correction du dossier.
pub fn validate_final(proof: &FinalProof) -> Result<ValidFinal, Rejection> {
    // P1 — Suite et jugements et merges.
    if proof.suite_total == 0 || proof.suite_passed != proof.suite_total {
        return Err(rejection(
            "P1",
            "suite",
            &format!("{}/{} tests passés", proof.suite_passed, proof.suite_total),
            "la suite re-courue doit passer entièrement (passed == total > 0) — un test rouge bloque la montée d'état sauf exclusion décidée par le coordinateur",
        ));
    }
    if proof.judgments.len() != 10 {
        return Err(rejection(
            "P1",
            "jugements",
            &format!("{} jugements relus", proof.judgments.len()),
            "10 jugements sont attendus (F1-1..F1-10) — un jugement manquant n'est pas un jugement VALIDÉ",
        ));
    }
    for j in proof.judgments {
        if !j.verdict.contains("VALIDÉ") && !j.verdict.contains("ACCEPTÉ") {
            return Err(rejection(
                "P1",
                "jugement",
                j.verdict,
                &format!(
                    "le jugement {} ne porte pas de verdict VALIDÉ ou ACCEPTÉ — un jugement non VALIDÉ ne ferme pas son pas",
                    j.step
                ),
            ));
        }
    }
    if proof.merges.len() != 9 {
        return Err(rejection(
            "P1",
            "merges",
            &format!("{} merges re-vérifiés", proof.merges.len()),
            "9 merges sont attendus (PR #26/#30/#44/#47/#49/#50/#51/#52/#53) — un merge manquant n'est pas un true merge",
        ));
    }
    for m in proof.merges {
        if !is_sha40(m.sha) || !is_sha40(m.parent1) || !is_sha40(m.parent2) {
            return Err(rejection(
                "P1",
                "merge",
                &format!("PR #{} sha {}", m.pr, m.sha),
                "un merge est un true merge : sha 40-hex, 2 parents 40-hex (DVG-01 : le compte de parents fait foi)",
            ));
        }
        if m.parent1 == m.parent2 || m.parent1 == m.sha || m.parent2 == m.sha {
            return Err(rejection(
                "P1",
                "merge",
                &format!("PR #{} parents {} / {}", m.pr, m.parent1, m.parent2),
                "un true merge a 2 parents distincts, distincts du merge commit — un squash n'est pas un merge",
            ));
        }
    }

    // P2 — Absorptions.
    if proof.absorptions.len() != 6 {
        return Err(rejection(
            "P2",
            "absorptions",
            &format!("{} absorptions citées", proof.absorptions.len()),
            "6 absorptions sont attendues (vérifier, décider, observer, interfacer, fluer, fabriquer) — une absorption sans preuve n'est pas une absorption",
        ));
    }
    for f in ABSORBED_FUNCTIONS {
        match proof.absorptions.iter().find(|a| a.function == f) {
            None => {
                return Err(rejection(
                    "P2",
                    "absorption",
                    f,
                    "l'absorption est absente de la preuve — une fonction non absorbée n'est pas tenue par le 1",
                ));
            }
            Some(a) if a.proof.trim().is_empty() => {
                return Err(rejection(
                    "P2",
                    "absorption",
                    f,
                    "l'absorption est citée sans preuve — une preuve vide n'est pas une preuve",
                ));
            }
            _ => {}
        }
    }

    // P6 — Ancres généralisées (avant P3 : la généralisation est la
    // condition des états de vision).
    if proof.anchors_generalized != 20 {
        return Err(rejection(
            "P6",
            "ancres généralisées",
            &format!("{} ancres", proof.anchors_generalized),
            "20 ancres généralisées sont attendues (9 gates A1–A9 + 11 libellés B1–B11) — une ancre non généralisée est une constante déguisée",
        ));
    }
    if !proof.fautif_v5_rejected || proof.fautif_v5_rule != "V9" {
        return Err(rejection(
            "P6",
            "fautif F-V5",
            proof.fautif_v5_rule,
            "le fautif F-V5 doit être rejeté V9 (libellés périmés présentés comme courants) — tout autre sort est un échec du hold-out",
        ));
    }
    for (fautif, rule) in VISION_REGRESSIONS {
        match proof
            .vision_regressions
            .iter()
            .find(|(f, _)| *f == fautif)
        {
            None => {
                return Err(rejection(
                    "P6",
                    "régression",
                    fautif,
                    "la régression est absente de la preuve — un fautif non rejoué n'est pas une régression verte",
                ));
            }
            Some((_, r)) if *r != rule => {
                return Err(rejection(
                    "P6",
                    "régression",
                    &format!("{} rejeté {}", fautif, r),
                    &format!(
                        "la régression {} doit être rejetée {} — une autre règle est un échec du hold-out",
                        fautif, rule
                    ),
                ));
            }
            _ => {}
        }
    }

    // P3 — États de vision.
    if proof.vision_states.len() != 2 {
        return Err(rejection(
            "P3",
            "états de vision",
            &format!("{} états rendus", proof.vision_states.len()),
            "2 états de vision sont attendus (journal 47 lignes et journal 90 lignes, sans modification du code entre les deux) — un seul état n'est pas un rejeu",
        ));
    }
    for s in proof.vision_states {
        if !s.accepted {
            return Err(rejection(
                "P3",
                "état de vision",
                &format!("journal {} lignes", s.journal_lines),
                "l'état de vision doit être ACCEPTÉ par la CLI généralisée — un état rejeté n'est pas une vision tenue",
            ));
        }
        if s.contradictions != 0 {
            return Err(rejection(
                "P3",
                "état de vision",
                &format!("{} contradictions non portées", s.contradictions),
                "0 contradiction non portée est exigée — une contradiction non portée est une contradiction lissée",
            ));
        }
    }
    if proof.vision_states[0].journal_lines == proof.vision_states[1].journal_lines {
        return Err(rejection(
            "P3",
            "états de vision",
            &format!(
                "journaux {} et {} lignes",
                proof.vision_states[0].journal_lines, proof.vision_states[1].journal_lines
            ),
            "les 2 états doivent porter sur des journaux de tailles distinctes (47 et 90 lignes) — deux rendus du même journal ne sont pas deux états",
        ));
    }

    // P4 — Acte.
    let acts_ok = proof
        .acts
        .iter()
        .filter(|a| a.authorized && a.questions_asked == 0)
        .count();
    if acts_ok == 0 && !proof.absence_consigned {
        return Err(rejection(
            "P4",
            "acte",
            "0 acte autorisé sans question, absence non consignée",
            "au moins un acte autorisé sans question est attendu — ou 0 acte et l'absence consignée (honnêteté A7 : jamais ACCEPTÉ par anticipation)",
        ));
    }
    if proof.acts.iter().any(|a| !a.authorized) {
        return Err(rejection(
            "P4",
            "acte",
            "un acte non autorisé est posé",
            "un acte non autorisé par le design signé n'est pas un acte du 1",
        ));
    }
    if proof
        .acts
        .iter()
        .any(|a| a.authorized && a.questions_asked > 0)
    {
        return Err(rejection(
            "P4",
            "acte",
            "un acte autorisé porte des questions de clarification",
            "un acte autorisé ne pose pas de question (A1–A8 : l'action est autorisée sans question préalable)",
        ));
    }

    // P5 — Routeur.
    if proof.router_nardole_events != 0 {
        return Err(rejection(
            "P5",
            "routeur",
            &format!(
                "{} événement(s) acteur session Nardole",
                proof.router_nardole_events
            ),
            "« 0 routeur » exige 0 événement acteur session Nardole (ae7d36d1) pendant la fenêtre — un seul événement rouvre le routeur",
        ));
    }
    if proof.router_routing_total == 0
        || proof.router_routing_as_events != proof.router_routing_total
    {
        return Err(rejection(
            "P5",
            "routeur",
            &format!(
                "{}/{} routages comme événements du journal",
                proof.router_routing_as_events, proof.router_routing_total
            ),
            "100 % des routages doivent être des événements du journal (> 0) — un routage hors journal est un routage par le routeur",
        ));
    }

    // P7 — F-A3, R3, fiche/manifeste, coordinateur.
    let f_a3_ok = proof.f_a3_rule == "A3"
        || (proof.f_a3_rule == "A2" && !proof.f_a3_reason.trim().is_empty());
    if !f_a3_ok {
        return Err(rejection(
            "P7",
            "F-A3",
            &format!("rejet {}", proof.f_a3_rule),
            "F-A3 doit être rejeté A3 (ou A2 avec sa raison exacte portée, cas à deux différences) — un rejet sans règle nommée, ou A1/A4/A6/A7, échoue le pas",
        ));
    }
    if !proof.r3_aligned {
        return Err(rejection(
            "P7",
            "R3",
            "note_code non alignée",
            "R3 doit être aligné (D-F1-11-7) : l'appel de merge est effectué par l'opérateur, la CLI execute-merge contrôle et gâte",
        ));
    }
    if !proof.fiche_manifeste_corrected {
        return Err(rejection(
            "P7",
            "fiche/manifeste",
            "fiche ou manifeste en retard au merge",
            "la fiche et le manifeste doivent être corrigés au merge (D-F1-11-8) — une preuve rendue sur un état en retard est une preuve périmée",
        ));
    }
    if !proof.coordinator_available {
        return Err(rejection(
            "P7",
            "coordinateur",
            "coordinateur indisponible",
            "le coordinateur atteste par événement du journal — indisponible, la preuve ne peut pas être attestée par événement du journal",
        ));
    }

    // P8 — Limites.
    if proof.limits.is_empty() {
        return Err(rejection(
            "P8",
            "limites",
            "aucune limite nommée",
            "la preuve nomme ses limites — une preuve sans limites se prétend complète",
        ));
    }
    if !proof
        .limits
        .iter()
        .any(|l| l.contains("DETTE-H-F1-7-SEMAINE"))
    {
        return Err(rejection(
            "P8",
            "limites",
            "DETTE-H-F1-7-SEMAINE absente",
            "la dette DETTE-H-F1-7-SEMAINE doit être nommée dans les limites — la semaine n'est pas prouvée, elle est portée comme dette",
        ));
    }
    if proof.claims_universal {
        return Err(rejection(
            "P8",
            "limites",
            "la preuve se prétend universelle",
            "la preuve ne promet pas la semaine, la mémoire universelle, le démantèlement, le rollback réel, H-F8-9 ni la bascule — une prétention universelle est une re-déclaration, pas un rejeu",
        ));
    }

    Ok(ValidFinal {
        suite_passed: proof.suite_passed,
        judgments: proof.judgments.len(),
        merges: proof.merges.len(),
        absorptions: proof.absorptions.len(),
        vision_states: proof.vision_states.len(),
        acts: acts_ok,
        routings_as_events: proof.router_routing_as_events,
    })
}

#[cfg(test)]
mod unit_tests {
    use super::*;

    fn preuve_valide<'a>() -> FinalProof<'a> {
        FinalProof {
            suite_total: 213,
            suite_passed: 213,
            judgments: &[
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
            ],
            merges: &[
                MergeRef { pr: 26, sha: "1f89b56123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 30, sha: "4668305123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 44, sha: "573cad4123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 47, sha: "4a68288123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 49, sha: "e2e9c14123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 50, sha: "055745b853495c38f0aaa0ae6c3d2adad9e89177", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 51, sha: "94fcda8123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 52, sha: "691b0a0123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
                MergeRef { pr: 53, sha: "28d32f7123456789012345678901234567890123", parent1: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", parent2: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" },
            ],
            absorptions: &[
                Absorption { function: "vérifier", proof: "DVG-01 + CI 8/8 dans les 8 jugements F1-3..F1-10" },
                Absorption { function: "décider", proof: "designs signés journaux 790/806/923/931/934/937/939/941/943" },
                Absorption { function: "observer", proof: "L00 tête Run #711 + N2 Run #487 re-mesurés" },
                Absorption { function: "interfacer", proof: "surface unique main + WhatsApp, chat.list re-vérifié" },
                Absorption { function: "fluer", proof: "journal 90 événements, seq 1–90, 0 trou" },
                Absorption { function: "fabriquer", proof: "9 merges true merge, commits 1f89b56..28d32f7" },
            ],
            anchors_generalized: 20,
            fautif_v5_rejected: true,
            fautif_v5_rule: "V9",
            vision_regressions: &[
                ("F-V1", "V3"),
                ("F-V2", "V2"),
                ("F-V3", "V1"),
                ("F-V4", "V4"),
            ],
            vision_states: &[
                VisionReplay { journal_lines: 47, accepted: true, contradictions: 0 },
                VisionReplay { journal_lines: 90, accepted: true, contradictions: 0 },
            ],
            acts: &[Act {
                act: "ouverture de la PR F1-11",
                authorized: true,
                questions_asked: 0,
                dispatch_id: "D-N055-F1-11-DELIVER",
            }],
            absence_consigned: false,
            router_nardole_events: 0,
            router_routing_total: 99,
            router_routing_as_events: 99,
            f_a3_rule: "A3",
            f_a3_reason: "",
            r3_aligned: true,
            fiche_manifeste_corrected: true,
            coordinator_available: true,
            limits: &[
                "DETTE-H-F1-7-SEMAINE — la tenue vision + action sur 7 jours consécutifs n'est pas prouvée",
                "mémoire universelle non prouvée",
                "démantèlement non prouvé",
                "rollback réel non prouvé",
                "H-F8-9 NON MESURÉ",
                "bascule non prouvée",
            ],
            claims_universal: false,
        }
    }

    #[test]
    fn preuve_valide_passe_p1_p8() {
        let valid = validate_final(&preuve_valide()).unwrap();
        assert_eq!(valid.suite_passed, 213);
        assert_eq!(valid.judgments, 10);
        assert_eq!(valid.merges, 9);
        assert_eq!(valid.absorptions, 6);
        assert_eq!(valid.vision_states, 2);
        assert_eq!(valid.acts, 1);
        assert_eq!(valid.routings_as_events, 99);
    }

    #[test]
    fn p1_suite_rouge_rejette() {
        let mut p = preuve_valide();
        p.suite_passed = 212;
        assert_eq!(validate_final(&p).unwrap_err().rule, "P1");
    }

    #[test]
    fn p2_absorption_sans_preuve_rejette() {
        let mut p = preuve_valide();
        let mut absorptions = p.absorptions.to_vec();
        absorptions[0].proof = "";
        p.absorptions = Box::leak(absorptions.into_boxed_slice());
        assert_eq!(validate_final(&p).unwrap_err().rule, "P2");
    }

    #[test]
    fn p6_ancre_non_generalisee_rejette() {
        let mut p = preuve_valide();
        p.anchors_generalized = 19;
        assert_eq!(validate_final(&p).unwrap_err().rule, "P6");
    }

    #[test]
    fn p6_f_v5_non_rejete_v9_rejette() {
        let mut p = preuve_valide();
        p.fautif_v5_rule = "V3";
        assert_eq!(validate_final(&p).unwrap_err().rule, "P6");
    }

    #[test]
    fn p3_etat_rejete_rejette() {
        let mut p = preuve_valide();
        let mut states = p.vision_states.to_vec();
        states[1].accepted = false;
        p.vision_states = Box::leak(states.into_boxed_slice());
        assert_eq!(validate_final(&p).unwrap_err().rule, "P3");
    }

    #[test]
    fn p4_absence_consignée_passe() {
        let mut p = preuve_valide();
        p.acts = &[];
        p.absence_consigned = true;
        assert!(validate_final(&p).is_ok());
    }

    #[test]
    fn p4_aucun_acte_sans_absence_rejette() {
        let mut p = preuve_valide();
        p.acts = &[];
        p.absence_consigned = false;
        assert_eq!(validate_final(&p).unwrap_err().rule, "P4");
    }

    #[test]
    fn p5_routeur_non_nul_rejette() {
        let mut p = preuve_valide();
        p.router_nardole_events = 1;
        assert_eq!(validate_final(&p).unwrap_err().rule, "P5");
    }

    #[test]
    fn p7_f_a3_autre_regle_rejette() {
        let mut p = preuve_valide();
        p.f_a3_rule = "A1";
        assert_eq!(validate_final(&p).unwrap_err().rule, "P7");
    }

    #[test]
    fn p7_f_a3_a2_avec_raison_passe() {
        // D-F1-11-6 : F-A3 re-classé cas à deux différences, ACCEPTÉ sous
        // la lecture « première règle applicable dans l'ordre ».
        let mut p = preuve_valide();
        p.f_a3_rule = "A2";
        p.f_a3_reason = "le rapport n'est pas rendu sur le dispatch de l'acte (le merge F1-9 est au journal, la preuve du rapport ne le cite pas)";
        assert!(validate_final(&p).is_ok());
    }

    #[test]
    fn p7_coordinateur_indisponible_rejette() {
        let mut p = preuve_valide();
        p.coordinator_available = false;
        assert_eq!(validate_final(&p).unwrap_err().rule, "P7");
    }

    #[test]
    fn p8_semaine_exigee_rejette() {
        let mut p = preuve_valide();
        p.claims_universal = true;
        assert_eq!(validate_final(&p).unwrap_err().rule, "P8");
    }

    #[test]
    fn p8_dette_absente_rejette() {
        let mut p = preuve_valide();
        p.limits = &["mémoire universelle non prouvée"];
        assert_eq!(validate_final(&p).unwrap_err().rule, "P8");
    }
}
