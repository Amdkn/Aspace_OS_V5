//! Fonction Juger — D-N055 F1-5, Fondation 13 → 1.
//!
//! La fonction Juger juge une PR par un mécanisme codé, sans le 13e comme
//! session séparée. Elle EST le jugement (D-F1-5-5) : elle applique les
//! règles J1–J8 du Discover F1-5 §4, dans l'ordre J1 → J7 → J2 → J5 → J3 →
//! J4 → J6 → J8 (du moins cher au plus cher — les contrôles J3/J4/J6 sont
//! les seuls qui touchent aux lectures à l'API et au rejeu ; tous les
//! autres sont locaux au dossier de jugement).
//!
//! Règles (Discover F1-5 §4) :
//! * J1 — En-tête complet : fonction (le 1 — fonction Juger, pas une
//!   session), date et heure réelle, PR jugée (n°, titre, tête), design
//!   jugé contre (chemin + journal de signature), méthode (rejeu
//!   indépendant), verdict. Un élément manquant = rejet du jugement (le
//!   jugement est renvoyé, la PR n'est pas jugée).
//! * J2 — Tête autorisée = tête vérifiée. Le verdict n'autorise le merge
//!   que sur la tête vérifiée à l'API au moment du jugement (SHA complet,
//!   40 hex, injecté par l'appelant). Une tête autorisée qui n'est pas la
//!   tête vérifiée, ou un SHA court, = rejet. Un jugement qui autorise
//!   une tête qu'il n'a pas vérifiée est une signature en blanc.
//! * J3 — CI re-vérifiée à l'API sur la tête. Chaque check-run sur la
//!   tête jugée est re-vérifié à l'API au moment du jugement (nom +
//!   conclusion, injectés par l'appelant), avec 0 conclusion d'échec non
//!   exclue. Une CI reprise du reçu de livraison, ou lue sur l'API legacy
//!   des statuts combinés, = rejet.
//! * J4 — Suite / harnais rejoué indépendamment. La suite est re-courue
//!   par le juge dans un clone frais, sur la tête vérifiée ; les chiffres
//!   sont re-comptés aux logs. Un PASS local repris du rapport de
//!   l'exécutant, sans rejeu, = rejet. Un rouge bloque, sauf exclusion
//!   décidée par le coordinateur avec liste exacte ET confirmée par le
//!   juge après re-vérification indépendante (P-F1-5-4).
//! * J5 — Chaque fait vérifié. Chaque fait affirmé porte son ancre
//!   vérifiable. Un fait sans ancre, ou affirmé depuis le récit du
//!   producteur (y compris le récit de l'exécutant du pas), = rejet. Un
//!   SHA cité est complet (40 hex) et résout — un SHA court = rejet là où
//!   le fait est affirmé comme preuve (un SHA court isolé est une
//!   référence, pas une citation — fiche, Divergence).
//! * J6 — Fautif planté rejeté. Le jugement doit rejeter l'artefact
//!   fautif planté par le design (§6) avec la règle nommée. Un fautif
//!   planté non rejeté (ou accepté) = échec de la fonction — la fonction
//!   revient à sa session d'origine, le 13e (filet (a), plan §D5).
//! * J7 — Le juge n'exécute pas. Le jugement ne merge rien, ne modifie
//!   pas la PR, ne consigne aucun reçu, n'écrit pas au registre ni sur
//!   les forks. Un jugement qui merge, consigne ou écrit hors de son
//!   propre fichier = rejet (et révocation du verdict).
//! * J8 — Limites nommées. Le jugement nomme ce qu'il ne prouve pas et
//!   ses réserves (R1, R2, …) avec leurs suivis hors PR. Un jugement qui
//!   se présente comme complet sans limites ni réserves nommées = rejet.
//!
//! Types du journal acceptés par la fonction (A-F1-5-3) : les 7 types du
//! design F1-3 + `closure_pulse` (8e type, légalisé porté en avant —
//! seq 14, événement vérifié). Le routeur (F1-3) n'est pas re-développé
//! par ce pas : sa liste `EVENT_TYPES` (7) reste celle du design F1-3 ;
//! c'est la fonction Juger qui accepte `closure_pulse` comme type légal
//! quand elle lit le journal.
//!
//! Frontière (voir fiche, Divergence) : la résolution des SHA, la
//! lecture CI et les résultats de suite sont injectés par l'appelant
//! (vérifiés par l'opérateur à l'API et par `cargo test` — la fonction
//! ne contacte ni git ni l'API). Zéro dépendance externe, zéro appel
//! sortant.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Juger).

use super::{Rejection, ShaResolver};

/// Les 8 types d'événements du journal acceptés par la fonction Juger
/// (A-F1-5-3 : les 7 du design F1-3 + `closure_pulse`).
pub const JOURNAL_EVENT_TYPES: [&str; 8] = [
    "closure_pulse",
    "correction",
    "dispatch_ack",
    "dispatch_relayed",
    "dispatch_typed",
    "judgment_rendered",
    "judgment_requested",
    "pulse",
];

/// Un type d'événement du journal est-il légal pour la fonction Juger ?
pub fn is_legal_event_type(typ: &str) -> bool {
    JOURNAL_EVENT_TYPES.contains(&typ)
}

/// Preuves injectées par l'appelant (vérifiées par l'opérateur à l'API et
/// par `cargo test` — la fonction ne contacte ni git ni l'API).
pub struct JudgmentEvidence<'a> {
    /// Tête vérifiée à l'API au moment du jugement (SHA complet, 40 hex).
    pub head: &'a str,
    /// Résolveur des SHA complets cités (vérifiés par l'opérateur).
    pub resolver: &'a dyn ShaResolver,
    /// Check-runs re-vérifiés à l'API sur la tête (nom, conclusion).
    pub ci: &'a [(&'a str, &'a str)],
    /// Suite re-courue par le juge : tests passés.
    pub suite_passed: usize,
    /// Suite re-courue par le juge : tests en échec.
    pub suite_failed: usize,
    /// Noms des tests en échec (preuves).
    pub suite_failed_names: &'a [&'a str],
    /// Noms des tests en échec exclus par décision du coordinateur
    /// (liste exacte, P-F1-5-4).
    pub excluded: &'a [&'a str],
    /// Règle attendue du rejet du fautif planté (ex. "J2").
    pub planted_fault_rule: &'a str,
}

/// Un jugement validé (prêt à être lu par le coordinateur — le merge reste
/// l'acte de l'exécutant, jamais du juge, J7).
#[derive(Debug, Clone)]
pub struct ValidJudgment {
    /// Numéro de la PR jugée (ex. `44`).
    pub pr: String,
    /// Tête autorisée (SHA complet, = tête vérifiée).
    pub head: String,
    /// Verdict (`VALIDÉE`, `VALIDÉE AVEC RÉSERVES` ou `REJETÉE`).
    pub verdict: String,
    /// Nombre de SHA complets vérifiés (J2/J5).
    pub shas_checked: usize,
}

/// Valide un jugement (texte Markdown) contre J1–J8, dans l'ordre
/// J1 → J7 → J2 → J5 → J3 → J4 → J6 → J8. Le premier rejet rencontré est
/// retourné, avec sa raison nommée — jamais corrigé silencieusement.
pub fn validate_judgment(
    text: &str,
    evidence: &JudgmentEvidence,
) -> Result<ValidJudgment, Rejection> {
    check_j1(text)?;
    check_j7(text)?;
    let shas_checked = check_j2(text, evidence)?;
    check_j5(text, evidence)?;
    check_j3(text, evidence)?;
    check_j4(text, evidence)?;
    check_j6(text, evidence)?;
    check_j8(text)?;
    let pr = extract_pr_number(text).unwrap_or_default();
    let verdict = extract_verdict(text);
    Ok(ValidJudgment {
        pr,
        head: evidence.head.to_string(),
        verdict,
        shas_checked,
    })
}

// ---------------------------------------------------------------------------
// Découpage du document en sections (« ## ... »)
// ---------------------------------------------------------------------------

/// Texte de la section dont l'en-tête contient `keyword` (de sa ligne
/// `## ` à la section suivante, ou à la fin du document). Chaîne vide si
/// absente.
fn section_named<'a>(text: &'a str, keyword: &str) -> &'a str {
    let mut start: Option<usize> = None;
    let mut end = text.len();
    let mut pos = 0usize;
    for line in text.split_inclusive('\n') {
        if line.starts_with("## ") {
            if start.is_some() {
                end = pos;
                break;
            }
            if line[3..].contains(keyword) {
                start = Some(pos);
            }
        }
        pos += line.len();
    }
    match start {
        Some(s) => &text[s..end],
        None => "",
    }
}

/// Plus grand indice ≤ `i` qui est une frontière de caractère UTF-8.
fn floor_boundary(s: &str, mut i: usize) -> usize {
    while i > 0 && !s.is_char_boundary(i) {
        i -= 1;
    }
    i
}

/// Toutes les suites maximales de caractères hexadécimaux minuscules du
/// texte, avec leur longueur.
fn hex_runs(text: &str) -> Vec<(String, usize)> {
    let mut runs = Vec::new();
    let mut cur = String::new();
    for c in text.chars() {
        if c.is_ascii_hexdigit() && (c.is_ascii_digit() || ('a'..='f').contains(&c)) {
            cur.push(c);
        } else {
            if !cur.is_empty() {
                let len = cur.len();
                runs.push((cur.clone(), len));
                cur.clear();
            }
        }
    }
    if !cur.is_empty() {
        let len = cur.len();
        runs.push((cur, len));
    }
    runs
}

fn is_hex40(s: &str) -> bool {
    s.len() == 40 && s.chars().all(|c| c.is_ascii_hexdigit())
}

fn truncate_line(s: &str, max: usize) -> String {
    let t: String = s.chars().take(max).collect();
    if s.chars().count() > max {
        format!("{}…", t)
    } else {
        t
    }
}

/// La ligne contenant `marker` (première occurrence), ou "".
fn line_containing<'a>(text: &'a str, marker: &str) -> &'a str {
    text.lines().find(|l| l.contains(marker)).unwrap_or("")
}

/// Numéro de PR extrait de la première ligne « PR #<n> ».
fn extract_pr_number(text: &str) -> Option<String> {
    let line = line_containing(text, "PR #");
    let after = line.split("PR #").nth(1)?;
    let num: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
    if num.is_empty() {
        None
    } else {
        Some(num)
    }
}

/// Verdict porté par le dossier (ordre : le plus précis d'abord).
fn extract_verdict(text: &str) -> String {
    if text.contains("VALIDÉE AVEC RÉSERVES") {
        "VALIDÉE AVEC RÉSERVES".to_string()
    } else if text.contains("VALIDÉE") {
        "VALIDÉE".to_string()
    } else if text.contains("REJETÉE") {
        "REJETÉE".to_string()
    } else {
        String::new()
    }
}

/// Un marqueur est-il nié sur sa propre ligne ? Une mention niée
/// (« Aucun reçu consigné par ce jugement ») n'est pas une exécution —
/// c'est sa négation (patron D5, F1-4). Seule la ligne qui porte le
/// marqueur compte : une négation d'une autre ligne (« ne prouve pas »
/// de l'en-tête de section) ne nie rien ici.
fn denied_before(text: &str, idx: usize) -> bool {
    let line_start = text[..idx].rfind('\n').map(|i| i + 1).unwrap_or(0);
    let before = &text[line_start..idx];
    before.contains("Aucun")
        || before.contains("aucun")
        || before.contains("ne ")
        || before.contains("Ni ")
        || before.contains("ni ")
        || before.contains("pas ")
        || before.contains("rien")
        || before.contains("Rien")
        || before.contains("sans ")
        || before.contains("jamais")
}

// ---------------------------------------------------------------------------
// J1 — En-tête complet
// ---------------------------------------------------------------------------

fn check_j1(text: &str) -> Result<(), Rejection> {
    let required: [(&str, &str, &str); 7] = [
        ("fonction", "Fonction :", "la fonction (le 1 — fonction Juger)"),
        (
            "fonction",
            "fonction Juger",
            "la fonction Juger, pas une session",
        ),
        (
            "fonction",
            "pas une session",
            "« pas une session » — le jugement est rendu par la fonction, pas par une session 13e",
        ),
        ("date", "Date", "la date et l'heure réelle du jugement"),
        ("pr", "PR jugée", "la PR jugée (n°, titre, tête)"),
        (
            "design",
            "Design jugé contre",
            "le design jugé contre (chemin + journal de signature)",
        ),
        (
            "méthode",
            "Méthode",
            "la méthode (rejeu indépendant, rien pris sur parole)",
        ),
    ];
    for (field, marker, detail) in required {
        if !text.contains(marker) {
            return Err(Rejection::new(
                "J1",
                field,
                "absent",
                &format!("en-tête incomplet : {} manquant", detail),
            ));
        }
    }
    if !text.contains("Verdict") {
        return Err(Rejection::new(
            "J1",
            "verdict",
            "absent",
            "en-tête incomplet : le verdict (VALIDÉE / VALIDÉE AVEC RÉSERVES / REJETÉE) est absent",
        ));
    }
    if extract_pr_number(text).is_none() {
        return Err(Rejection::new(
            "J1",
            "pr",
            "PR jugée sans numéro",
            "la PR jugée doit porter son numéro (PR #<n>)",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// J7 — Le juge n'exécute pas
// ---------------------------------------------------------------------------

fn check_j7(text: &str) -> Result<(), Rejection> {
    let markers = [
        "consigné par ce jugement",
        "mergé par ce jugement",
        "ouvre la PR",
        "écrit au registre",
        "consigne un reçu",
        "merge la PR",
    ];
    for marker in markers {
        let mut search_from = 0usize;
        while let Some(rel) = text[search_from..].find(marker) {
            let idx = search_from + rel;
            if !denied_before(text, idx) {
                return Err(Rejection::new(
                    "J7",
                    "exécution",
                    marker,
                    "le juge n'exécute pas — un jugement qui merge, consigne un reçu ou écrit au registre n'est pas un jugement, c'est une exécution déguisée",
                ));
            }
            search_from = idx + marker.len();
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// J2 — Tête autorisée = tête vérifiée
// ---------------------------------------------------------------------------

fn check_j2(text: &str, evidence: &JudgmentEvidence) -> Result<usize, Rejection> {
    let mut checked = 0usize;
    let mut seen: Vec<String> = Vec::new();
    // (a) La tête autorisée par le verdict est la tête vérifiée — la
    // ligne qui la porte est la première ligne « tête autorisée »
    // portant un SHA complet (une mention sans SHA ne l'autorise pas).
    let authorized = text
        .lines()
        .filter(|l| l.to_lowercase().contains("tête autorisée"))
        .find_map(|l| {
            hex_runs(l)
                .into_iter()
                .find(|(_, len)| *len == 40)
                .map(|(s, _)| s)
        });
    let line = line_containing(text, "tête autorisée");
    if line.is_empty() {
        return Err(Rejection::new(
            "J2",
            "tête autorisée",
            "absente",
            "le verdict doit nommer la tête autorisée en SHA complet — sans tête autorisée, aucun merge n'est autorisé",
        ));
    }
    match authorized {
        Some(sha) => {
            if !seen.contains(&sha) {
                seen.push(sha.clone());
                checked += 1;
            }
            if !evidence.resolver.resolves(&sha) {
                return Err(Rejection::new(
                    "J2",
                    "tête autorisée",
                    &sha,
                    "la tête autorisée ne résout pas — un SHA cité est complet (40 hex) et résout",
                ));
            }
            if sha != evidence.head {
                return Err(Rejection::new(
                    "J2",
                    "tête autorisée",
                    &truncate_line(&sha, 40),
                    "la tête autorisée n'est pas la tête vérifiée à l'API — un jugement qui autorise une tête qu'il n'a pas vérifiée est une signature en blanc",
                ));
            }
        }
        None => {
            return Err(Rejection::new(
                "J2",
                "tête autorisée",
                &truncate_line(line.trim(), 120),
                "la tête autorisée doit être citée à sa forme complète (40 hex) — un SHA court n'autorise rien",
            ));
        }
    }
    // (b) La tête de la PR jugée est la même tête vérifiée.
    let pr_line = line_containing(text, "PR jugée");
    for (run, len) in hex_runs(pr_line) {
        if len == 40 && is_hex40(&run) {
            if !seen.contains(&run) {
                seen.push(run.clone());
                checked += 1;
            }
            if !evidence.resolver.resolves(&run) {
                return Err(Rejection::new(
                    "J2",
                    "sha",
                    &run,
                    "la tête de la PR jugée ne résout pas",
                ));
            }
            if run != evidence.head {
                return Err(Rejection::new(
                    "J2",
                    "tête jugée",
                    &truncate_line(&run, 40),
                    "la tête de la PR jugée n'est pas la tête vérifiée à l'API — le jugement porte sur une autre tête que celle vérifiée",
                ));
            }
        }
    }
    Ok(checked)
}

// ---------------------------------------------------------------------------
// J5 — Chaque fait vérifié
// ---------------------------------------------------------------------------

fn check_j5(text: &str, evidence: &JudgmentEvidence) -> Result<(), Rejection> {
    // (a) Tout SHA complet cité résout.
    let mut seen: Vec<String> = Vec::new();
    for (run, len) in hex_runs(text) {
        if len == 40 && is_hex40(&run) && !seen.contains(&run) {
            seen.push(run.clone());
            if !evidence.resolver.resolves(&run) {
                return Err(Rejection::new(
                    "J5",
                    "sha",
                    &run,
                    "SHA complet cité mais ne résout pas — un SHA cité est complet (40 hex) et résout",
                ));
            }
        }
    }
    // (b) Aucun fait affirmé depuis le récit du producteur.
    for marker in ["récit de l'exécutant", "rapport de l'exécutant"] {
        let mut search_from = 0usize;
        while let Some(rel) = text[search_from..].find(marker) {
            let idx = search_from + rel;
            if !denied_before(text, idx) {
                let line = text.lines().find(|l| l.contains(marker)).unwrap_or("");
                return Err(Rejection::new(
                    "J5",
                    "ancre",
                    &truncate_line(line.trim(), 120),
                    "fait affirmé depuis le récit de l'exécutant — un jugement qui reprend le récit du producteur sans re-vérifier n'est pas un jugement, c'est un tampon",
                ));
            }
            search_from = idx + marker.len();
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// J3 — CI re-vérifiée à l'API sur la tête
// ---------------------------------------------------------------------------

fn check_j3(text: &str, evidence: &JudgmentEvidence) -> Result<(), Rejection> {
    if evidence.ci.is_empty() {
        return Err(Rejection::new(
            "J3",
            "ci",
            "aucun check-run injecté",
            "la CI doit être re-vérifiée à l'API sur la tête jugée — aucun check-run fourni par l'opérateur",
        ));
    }
    // (a) Aucune conclusion d'échec dans les preuves injectées.
    for (name, conclusion) in evidence.ci {
        if *conclusion != "success" && *conclusion != "neutral" {
            return Err(Rejection::new(
                "J3",
                "ci",
                &format!("{}: {}", name, conclusion),
                "la CI re-vérifiée à l'API porte une conclusion d'échec sur la tête jugée — le jugement ne peut pas valider une CI non verte",
            ));
        }
    }
    // (b) La section CI du dossier liste chaque check-run re-vérifié et
    // ne porte aucune conclusion d'échec.
    let ci_section = section_named(text, "CI");
    if ci_section.is_empty() {
        return Err(Rejection::new(
            "J3",
            "ci",
            "section CI absente",
            "le jugement doit porter une section CI re-vérifiée à l'API sur la tête jugée",
        ));
    }
    for bad in ["failure", "cancelled", "timed_out", "action_required"] {
        if ci_section.contains(bad) {
            return Err(Rejection::new(
                "J3",
                "ci",
                bad,
                "la section CI du dossier porte une conclusion d'échec — une CI non verte ne peut pas être validée",
            ));
        }
    }
    for (name, _) in evidence.ci {
        if !ci_section.contains(name) {
            return Err(Rejection::new(
                "J3",
                "ci",
                name,
                "check-run re-vérifié à l'API absent de la section CI du dossier — la CI du dossier n'est pas la CI re-vérifiée",
            ));
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// J4 — Suite / harnais rejoué indépendamment
// ---------------------------------------------------------------------------

/// Premier compte « N/M » après `cargo test` dans la section Rejeu.
fn replay_counts(text: &str) -> Option<(usize, usize)> {
    let sec = section_named(text, "Rejeu");
    let pos = sec.find("cargo test")?;
    let after = &sec[pos..];
    let mut digits = String::new();
    let mut first: Option<usize> = None;
    for c in after.chars() {
        if c.is_ascii_digit() {
            digits.push(c);
        } else if c == '/' && first.is_none() && !digits.is_empty() {
            first = digits.parse().ok();
            digits.clear();
        } else if !digits.is_empty() {
            if let Some(p) = first {
                if let Ok(t) = digits.parse::<usize>() {
                    return Some((p, t));
                }
            }
            return None;
        } else if first.is_some() {
            return None;
        }
    }
    if let Some(p) = first {
        if let Ok(t) = digits.parse::<usize>() {
            return Some((p, t));
        }
    }
    None
}

fn check_j4(text: &str, evidence: &JudgmentEvidence) -> Result<(), Rejection> {
    let (passed, total) = match replay_counts(text) {
        Some(c) => c,
        None => {
            return Err(Rejection::new(
                "J4",
                "rejeu",
                "aucun compte cargo test",
                "la suite doit être re-courue par le juge dans un clone frais — aucun compte « cargo test N/M » dans la section Rejeu",
            ));
        }
    };
    if total == 0 || passed > total {
        return Err(Rejection::new(
            "J4",
            "rejeu",
            &format!("{}/{}", passed, total),
            "compte de suite incohérent — passés > total, ou total nul",
        ));
    }
    let failed = total - passed;
    if failed == 0 {
        if evidence.suite_failed > 0 {
            return Err(Rejection::new(
                "J4",
                "rejeu",
                &format!("dossier {}/{} vert, preuves {} échec(s)", passed, total, evidence.suite_failed),
                "le dossier affirme une suite verte alors que les preuves injectées portent un rouge — le vert est repris du récit, pas rejoué",
            ));
        }
        return Ok(());
    }
    // Un rouge : il ne passe que par exclusion décidée par le
    // coordinateur, liste exacte, confirmée par le juge (P-F1-5-4).
    let names_exclusion = text.contains("Exclusion") && text.contains("coordinateur");
    if !names_exclusion {
        return Err(Rejection::new(
            "J4",
            "suite",
            &format!("{}/{} ({} rouge(s), sans exclusion)", passed, total, failed),
            "la suite re-courue porte un rouge sans décision d'exclusion du coordinateur — sans décision, un rouge bloque",
        ));
    }
    if evidence.suite_failed != failed {
        return Err(Rejection::new(
            "J4",
            "suite",
            &format!("dossier {} rouge(s), preuves {} rouge(s)", failed, evidence.suite_failed),
            "le nombre de rouges du dossier ne correspond pas aux preuves injectées — l'exclusion ne couvre pas ce rouge",
        ));
    }
    for name in evidence.suite_failed_names {
        if !evidence.excluded.contains(name) {
            return Err(Rejection::new(
                "J4",
                "suite",
                name,
                "rouge non couvert par la liste exacte d'exclusion du coordinateur — l'exclusion ne vaut que pour sa liste exacte",
            ));
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// J6 — Fautif planté rejeté
// ---------------------------------------------------------------------------

fn check_j6(text: &str, evidence: &JudgmentEvidence) -> Result<(), Rejection> {
    let start = match text.find("Fautif planté") {
        Some(i) => i,
        None => {
            return Err(Rejection::new(
                "J6",
                "fautif planté",
                "absent",
                "le jugement doit rejeter l'artefact fautif planté par le design avec sa règle nommée — sans rejet, la fonction n'a pas prouvé qu'elle juge",
            ));
        }
    };
    let end = floor_boundary(text, (start + 300).min(text.len()));
    let window = &text[start..end];
    let expected = format!("REJET {}", evidence.planted_fault_rule);
    if !window.contains(&expected) {
        return Err(Rejection::new(
            "J6",
            "fautif planté",
            &truncate_line(window.trim(), 120),
            &format!(
                "le fautif planté n'est pas rejeté avec la règle attendue ({}) — un fautif planté non rejeté est un échec de la fonction",
                evidence.planted_fault_rule
            ),
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// J8 — Limites nommées
// ---------------------------------------------------------------------------

fn check_j8(text: &str) -> Result<(), Rejection> {
    if !text.contains("Ce que ce jugement ne prouve pas") {
        return Err(Rejection::new(
            "J8",
            "limites",
            "absent",
            "le jugement doit nommer ce qu'il ne prouve pas",
        ));
    }
    if !text.contains("Réserves") {
        return Err(Rejection::new(
            "J8",
            "réserves",
            "absent",
            "le jugement doit nommer ses réserves (R1, R2, …) avec leurs suivis hors PR",
        ));
    }
    Ok(())
}
