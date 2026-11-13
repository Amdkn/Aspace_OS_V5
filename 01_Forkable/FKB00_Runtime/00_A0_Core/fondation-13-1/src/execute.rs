//! Fonction Exécuter — D-N055 F1-6, Fondation 13 → 1.
//!
//! La fonction Exécuter exécute un merge par un mécanisme codé, sans Ryan
//! comme session séparée. Elle EST l'exécution (D-F1-6-5) : elle applique
//! les règles E1–E8 du Discover F1-6 §4, dans l'ordre E1 → E8 → E2 → E4 →
//! E3 → E5 → E6 → E7 (du moins cher au plus cher — les contrôles E2/E3/E4
//! sont les seuls qui touchent aux lectures à l'API avant l'appel ; E6 est
//! l'appel lui-même ; E7 est la vérification post-merge, par un tiers).
//!
//! Règles (Discover F1-6 §4) :
//! * E1 — Instruction complète. L'exécution porte : le jugement rendu
//!   (fichier + journal de signature du design), son verdict (VALIDÉE ou
//!   VALIDÉE AVEC RÉSERVES — jamais REJETÉE), la tête autorisée (SHA
//!   complet, 40 hex), les réserves et exclusions applicables. Un élément
//!   manquant, un verdict REJETÉE, ou l'absence de jugement = pas de merge.
//! * E2 — Tête au moment du merge = tête autorisée. La tête vérifiée à
//!   l'API immédiatement avant l'appel est la tête autorisée par le
//!   jugement (SHA complet). Une tête qui a bougé après le jugement, ou
//!   une tête autorisée qui n'est pas la tête vérifiée, = pas de merge —
//!   un nouveau jugement est exigé sur la nouvelle tête. Un merge qui
//!   merge une tête qu'il n'a pas vérifiée au moment de l'acte n'est pas
//!   une exécution, c'est un clic.
//! * E3 — CI re-vérifiée à l'API sur la tête, au moment du merge. Chaque
//!   check-run sur la tête est re-vérifié à l'API immédiatement avant
//!   l'appel (nom + conclusion, injectés par l'appelant), avec 0
//!   conclusion d'échec non exclue. Une CI reprise du jugement, ou lue
//!   sur l'API legacy des statuts combinés, = pas de merge. Un rouge
//!   bloque, sauf exclusion décidée par le coordinateur avec liste exacte
//!   ET confirmée par le juge après re-vérification indépendante (règle 11,
//!   Discover F1-6 §1).
//! * E4 — Mergeable au moment du merge. La PR est `mergeable: true` et
//!   `mergeable_state: clean` à l'API immédiatement avant l'appel. Un
//!   `mergeable_state` autre que `clean` = pas de merge — l'exécution
//!   attend ou renvoie, elle ne force pas. Un état transitoire
//!   (`unstable`, CI en cours) est attendu par re-lecture, jamais refusé
//!   définitivement comme un état transitoire ; un `blocked` ou `dirty`
//!   (conflit) = refus/renvoi.
//! * E5 — Méthode true merge, nommée dans l'appel. L'appel porte la
//!   méthode `merge` (jamais `squash`, jamais `rebase`) ; le merge commit
//!   doit porter 2 parents (DVG-01). Une méthode autre que `merge`, ou un
//!   merge commit à 1 parent, = merge invalide.
//! * E6 — Appel nommé et rejouable. La commande exacte (ou l'appel API
//!   exact), ses paramètres, son horodatage et sa sortie (merge commit
//!   SHA, `merged: true`) sont consignés dans le dossier d'exécution. Un
//!   merge dont l'appel n'est pas consigné = merge non vérifiable.
//! * E7 — Vérification post-merge par un tiers. Après l'appel, un autre
//!   que l'exécutant re-vérifie à l'API : merge commit 2 parents
//!   (DVG-01), parent 2 = tête autorisée, parent 1 = master au moment du
//!   merge, `merged: true`, `merged_at`, master HEAD = merge commit,
//!   0 PR ouverte. Un écart = le merge est invalide.
//! * E8 — Limites nommées ; l'exécutant ne juge pas. L'exécution nomme
//!   ce qu'elle ne prouve pas (« ce que ce merge ne prouve pas ») et ne
//!   juge rien, ne modifie pas la PR, ne consigne aucun reçu, n'écrit pas
//!   au registre. Une exécution qui juge, consigne ou écrit hors de son
//!   propre dossier = rejet (et révocation de l'exécution).
//!
//! Types du journal acceptés par la fonction (A-F1-6-4) : les 9 types —
//! les 8 du design F1-5 (les 7 du design F1-3 + `closure_pulse`) +
//! `merge_executed` (émis par le routeur au rendu du merge). La F1-6
//! changeset porte la liste des types du routeur à 9 ; le design F1-3
//! n'est pas réécrit.
//!
//! Frontière (voir fiche, Divergence) : la résolution des SHA, la lecture
//! CI, le mergeable et les preuves post-merge sont injectés par l'appelant
//! (vérifiés par l'opérateur à l'API et par `cargo test` — la fonction ne
//! contacte ni git ni l'API). L'appel de merge lui-même (`gh pr merge
//! --merge`, ou `POST /pulls/{n}/merge`, méthode `merge`) est effectué par
//! l'opérateur sur instruction du dossier validé par la CLI, et consigné
//! dans le dossier (E6) — la CLI, std seul sans dépendance, ne peut pas
//! faire d'HTTPS. Zéro dépendance externe, zéro appel sortant dans le code.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Exécuter).

use super::{Rejection, ShaResolver};

/// Les 9 types d'événements du journal acceptés par la fonction Exécuter
/// (A-F1-6-4 : les 8 du design F1-5 + `merge_executed`).
pub const JOURNAL_EVENT_TYPES: [&str; 9] = [
    "closure_pulse",
    "correction",
    "dispatch_ack",
    "dispatch_relayed",
    "dispatch_typed",
    "judgment_rendered",
    "judgment_requested",
    "merge_executed",
    "pulse",
];

/// Un type d'événement du journal est-il légal pour la fonction Exécuter ?
pub fn is_legal_event_type(typ: &str) -> bool {
    JOURNAL_EVENT_TYPES.contains(&typ)
}

/// Stade de l'exécution au moment du contrôle : avant l'appel (E1–E5 +
/// E8 seuls — E6/E7 ne sont pas encore applicables) ou après l'appel
/// (E1–E8 complets).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Stage {
    PreMerge,
    PostMerge,
}

/// Preuves injectées par l'appelant (vérifiées par l'opérateur à l'API —
/// la fonction ne contacte ni git ni l'API).
pub struct ExecutionEvidence<'a> {
    /// Tête vérifiée à l'API immédiatement avant l'appel (SHA complet).
    pub head: &'a str,
    /// Résolveur des SHA complets cités (vérifiés par l'opérateur).
    pub resolver: &'a dyn ShaResolver,
    /// Check-runs re-vérifiés à l'API sur la tête (nom, conclusion).
    pub ci: &'a [(&'a str, &'a str)],
    /// La PR est-elle `mergeable` à l'API au moment du merge ?
    pub mergeable: bool,
    /// `mergeable_state` à l'API au moment du merge (`clean`, …).
    pub mergeable_state: &'a str,
    /// Méthode de l'appel (`merge` — jamais `squash` ni `rebase`).
    pub method: &'a str,
    /// Noms des check-runs en échec exclus par décision du coordinateur
    /// (liste exacte, P-F1-6-4).
    pub excluded: &'a [&'a str],
    /// Stade du contrôle (avant ou après l'appel).
    pub stage: Stage,
    /// Merge commit (post-merge seulement) : SHA complet, 40 hex.
    pub merge_commit: Option<&'a str>,
    /// Le merge a-t-il réussi (`merged: true`) ?
    pub merged: bool,
    /// `merged_at` (post-merge seulement, ISO 8601).
    pub merged_at: &'a str,
    /// Parent 1 du merge commit (post-merge seulement).
    pub parent1: Option<&'a str>,
    /// Parent 2 du merge commit (post-merge seulement).
    pub parent2: Option<&'a str>,
    /// Master HEAD après le merge (post-merge seulement).
    pub master_head: Option<&'a str>,
    /// PR ouvertes après le merge (post-merge seulement).
    pub open_prs: Option<usize>,
}

/// Une exécution validée (prête à être lue par le coordinateur — le reçu
/// du merge vient après, par un exécutant dédié, jamais par l'exécutant,
/// E8).
#[derive(Debug, Clone)]
pub struct ValidExecution {
    /// Numéro de la PR mergée (ex. `44`).
    pub pr: String,
    /// Tête autorisée (SHA complet, = tête vérifiée).
    pub head: String,
    /// Méthode de l'appel (`merge`).
    pub method: String,
    /// Merge commit (post-merge seulement).
    pub merge_commit: Option<String>,
}

/// Valide un dossier d'exécution (texte Markdown) contre E1–E8, dans
/// l'ordre E1 → E8 → E2 → E4 → E3 → E5 → E6 → E7. En stade pré-merge,
/// E6/E7 ne sont pas encore applicables et ne sont pas contrôlés. Le
/// premier rejet rencontré est retourné, avec sa raison nommée — jamais
/// corrigé silencieusement.
pub fn validate_execution(
    text: &str,
    evidence: &ExecutionEvidence,
) -> Result<ValidExecution, Rejection> {
    check_e1(text, evidence)?;
    check_e8(text)?;
    let authorized = check_e2(text, evidence)?;
    check_e4(text, evidence)?;
    check_e3(text, evidence)?;
    check_e5(text, evidence)?;
    if evidence.stage == Stage::PostMerge {
        check_e6(text, evidence)?;
        check_e7(text, evidence, &authorized)?;
    }
    let pr = extract_pr_number(text).unwrap_or_default();
    Ok(ValidExecution {
        pr,
        head: evidence.head.to_string(),
        method: evidence.method.to_string(),
        merge_commit: evidence.merge_commit.map(|s| s.to_string()),
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

/// Un marqueur est-il nié sur sa propre ligne ? Une mention niée
/// (« Aucun reçu consigné par cette exécution ») n'est pas une exécution —
/// c'est sa négation (patron J7, F1-5). Seule la ligne qui porte le
/// marqueur compte.
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

/// La ligne « tête autorisée » portant un SHA complet (première ligne
/// « tête autorisée » avec un SHA 40 hex) — l'autorité est la section
/// Instruction : l'en-tête peut citer la tête autorisée en référence,
/// seule la ligne de la section Instruction l'autorise (patron J2, F1-5).
fn authorized_head(text: &str) -> Option<String> {
    let instruction = section_named(text, "Instruction");
    let scope = if instruction.is_empty() {
        text
    } else {
        instruction
    };
    scope
        .lines()
        .filter(|l| l.to_lowercase().contains("tête autorisée"))
        .find_map(|l| {
            hex_runs(l)
                .into_iter()
                .find(|(_, len)| *len == 40)
                .map(|(s, _)| s)
        })
}

// ---------------------------------------------------------------------------
// E1 — Instruction complète
// ---------------------------------------------------------------------------

fn check_e1(text: &str, evidence: &ExecutionEvidence) -> Result<(), Rejection> {
    let required: [(&str, &str, &str); 6] = [
        ("fonction", "Fonction :", "la fonction (le 1 — fonction Exécuter)"),
        (
            "fonction",
            "fonction Exécuter",
            "la fonction Exécuter, pas une session",
        ),
        (
            "fonction",
            "pas une session",
            "« pas une session » — l'exécution est rendue par la fonction, pas par une session Ryan",
        ),
        ("date", "Date", "la date et l'heure réelle de l'exécution"),
        ("pr", "PR mergée", "la PR mergée (n°, titre, tête)"),
        (
            "instruction",
            "Instruction lue",
            "l'instruction lue (jugement + tête autorisée)",
        ),
    ];
    for (field, marker, detail) in required {
        if !text.contains(marker) {
            return Err(Rejection::new(
                "E1",
                field,
                "absent",
                &format!("en-tête incomplet : {} manquant", detail),
            ));
        }
    }
    if section_named(text, "Instruction").is_empty() {
        return Err(Rejection::new(
            "E1",
            "instruction",
            "section Instruction absente",
            "l'exécution doit porter une section Instruction (jugement rendu, verdict, tête autorisée, réserves)",
        ));
    }
    // Le verdict porté par la ligne « Verdict du jugement : » — jamais
    // REJETÉE, jamais absent.
    let verdict_line = line_containing(text, "Verdict du jugement");
    if verdict_line.is_empty() {
        return Err(Rejection::new(
            "E1",
            "verdict",
            "absent",
            "l'instruction doit porter le verdict du jugement (VALIDÉE ou VALIDÉE AVEC RÉSERVES) — sans verdict, aucun merge n'est autorisé",
        ));
    }
    if verdict_line.contains("REJETÉE") {
        return Err(Rejection::new(
            "E1",
            "verdict",
            "REJETÉE",
            "le jugement est REJETÉE — un jugement rejeté n'autorise aucun merge, l'exécution est refusée",
        ));
    }
    if !verdict_line.contains("VALIDÉE") {
        return Err(Rejection::new(
            "E1",
            "verdict",
            &truncate_line(verdict_line.trim(), 120),
            "le verdict du jugement doit être VALIDÉE ou VALIDÉE AVEC RÉSERVES — un verdict illisible n'autorise rien",
        ));
    }
    // La tête autorisée est citée à sa forme complète et résout.
    let line = line_containing(text, "tête autorisée");
    if line.is_empty() {
        return Err(Rejection::new(
            "E1",
            "tête autorisée",
            "absente",
            "l'instruction doit nommer la tête autorisée en SHA complet — sans tête autorisée, aucun merge n'est autorisé",
        ));
    }
    match authorized_head(text) {
        Some(sha) => {
            if !evidence.resolver.resolves(&sha) {
                return Err(Rejection::new(
                    "E1",
                    "tête autorisée",
                    &sha,
                    "la tête autorisée ne résout pas — un SHA cité est complet (40 hex) et résout",
                ));
            }
        }
        None => {
            return Err(Rejection::new(
                "E1",
                "tête autorisée",
                &truncate_line(line.trim(), 120),
                "la tête autorisée doit être citée à sa forme complète (40 hex) — un SHA court n'autorise rien",
            ));
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// E8 — Limites nommées ; l'exécutant ne juge pas
// ---------------------------------------------------------------------------

fn check_e8(text: &str) -> Result<(), Rejection> {
    if !text.contains("Ce que cette exécution ne prouve pas") {
        return Err(Rejection::new(
            "E8",
            "limites",
            "absent",
            "l'exécution doit nommer ce qu'elle ne prouve pas",
        ));
    }
    if !text.contains("Réserves") {
        return Err(Rejection::new(
            "E8",
            "réserves",
            "absent",
            "l'exécution doit nommer ses réserves (R1, R2, …) avec leurs suivis hors PR",
        ));
    }
    // L'exécutant ne juge pas, ne consigne pas, n'écrit pas au registre,
    // ne modifie pas la PR — un marqueur non nié sur sa propre ligne est
    // une exécution déguisée en jugement (patron J7, F1-5).
    let markers = [
        "consigné par cette exécution",
        "mergée par cette exécution",
        "écrit au registre",
        "consigne un reçu",
        "rend un verdict",
        "modification de la PR",
    ];
    for marker in markers {
        let mut search_from = 0usize;
        while let Some(rel) = text[search_from..].find(marker) {
            let idx = search_from + rel;
            if !denied_before(text, idx) {
                return Err(Rejection::new(
                    "E8",
                    "exécution",
                    marker,
                    "l'exécutant ne juge pas — une exécution qui rend un verdict, consigne un reçu ou écrit au registre n'est pas une exécution, c'est un jugement déguisé",
                ));
            }
            search_from = idx + marker.len();
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// E2 — Tête au moment du merge = tête autorisée
// ---------------------------------------------------------------------------

fn check_e2(text: &str, evidence: &ExecutionEvidence) -> Result<String, Rejection> {
    if !is_hex40(evidence.head) {
        return Err(Rejection::new(
            "E2",
            "tête vérifiée",
            &truncate_line(evidence.head, 40),
            "la tête vérifiée à l'API doit être un SHA complet (40 hex) — une tête illisible n'autorise rien",
        ));
    }
    let authorized = match authorized_head(text) {
        Some(sha) => sha,
        None => {
            return Err(Rejection::new(
                "E2",
                "tête autorisée",
                "absente",
                "la tête autorisée doit être citée à sa forme complète (40 hex)",
            ));
        }
    };
    if authorized != evidence.head {
        return Err(Rejection::new(
            "E2",
            "tête autorisée",
            &truncate_line(&authorized, 40),
            "la tête autorisée n'est pas la tête vérifiée à l'API au moment du merge — un merge qui merge une tête qu'il n'a pas vérifiée au moment de l'acte n'est pas une exécution, c'est un clic",
        ));
    }
    Ok(authorized)
}

// ---------------------------------------------------------------------------
// E4 — Mergeable au moment du merge
// ---------------------------------------------------------------------------

fn check_e4(text: &str, evidence: &ExecutionEvidence) -> Result<(), Rejection> {
    if !evidence.mergeable {
        return Err(Rejection::new(
            "E4",
            "mergeable",
            "false",
            "la PR n'est pas mergeable à l'API au moment du merge — l'exécution attend ou renvoie, elle ne force pas",
        ));
    }
    if evidence.mergeable_state != "clean" {
        if evidence.mergeable_state == "unstable" {
            return Err(Rejection::new(
                "E4",
                "mergeable_state",
                "unstable",
                "état transitoire (CI en cours) — attendre et re-lire, jamais forcer, jamais refuser définitivement un état transitoire sans re-lecture",
            ));
        }
        return Err(Rejection::new(
            "E4",
            "mergeable_state",
            evidence.mergeable_state,
            "la PR n'est pas dans un état mergeable clean à l'API au moment du merge (conflit ou bloqué) — l'exécution attend ou renvoie, elle ne force pas",
        ));
    }
    let pre = section_named(text, "Pré-vérifications");
    if pre.is_empty() {
        return Err(Rejection::new(
            "E4",
            "pré-vérifications",
            "section absente",
            "l'exécution doit porter une section Pré-vérifications re-courues au moment du merge",
        ));
    }
    if !pre.contains("mergeable: true") {
        return Err(Rejection::new(
            "E4",
            "mergeable",
            "non consigné",
            "la section Pré-vérifications doit consigner `mergeable: true` re-vérifié à l'API au moment du merge",
        ));
    }
    if !pre.contains("mergeable_state: clean") {
        return Err(Rejection::new(
            "E4",
            "mergeable_state",
            "non consigné",
            "la section Pré-vérifications doit consigner `mergeable_state: clean` re-vérifié à l'API au moment du merge",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// E3 — CI re-vérifiée à l'API sur la tête
// ---------------------------------------------------------------------------

fn check_e3(text: &str, evidence: &ExecutionEvidence) -> Result<(), Rejection> {
    if evidence.ci.is_empty() {
        return Err(Rejection::new(
            "E3",
            "ci",
            "aucun check-run injecté",
            "la CI doit être re-vérifiée à l'API sur la tête au moment du merge — aucun check-run fourni par l'opérateur",
        ));
    }
    // (a) Aucune conclusion d'échec non exclue dans les preuves injectées.
    for (name, conclusion) in evidence.ci {
        if *conclusion != "success" && *conclusion != "neutral" {
            if !evidence.excluded.contains(name) {
                return Err(Rejection::new(
                    "E3",
                    "ci",
                    &format!("{}: {}", name, conclusion),
                    "la CI re-vérifiée à l'API porte une conclusion d'échec sur la tête au moment du merge — un rouge bloque, sauf exclusion décidée par le coordinateur avec liste exacte ET confirmée par le juge",
                ));
            }
            if !text.contains("Exclusion") || !text.contains("coordinateur") {
                return Err(Rejection::new(
                    "E3",
                    "ci",
                    &format!("{}: {} (exclu ?)", name, conclusion),
                    "le rouge exclu doit être nommé par une décision d'exclusion du coordinateur, liste exacte, dans le dossier — sans décision, un rouge bloque",
                ));
            }
        }
    }
    // (b) La section Pré-vérifications du dossier liste chaque check-run
    // re-vérifié et ne porte aucune conclusion d'échec.
    let pre = section_named(text, "Pré-vérifications");
    if pre.is_empty() {
        return Err(Rejection::new(
            "E3",
            "ci",
            "section Pré-vérifications absente",
            "l'exécution doit porter une section Pré-vérifications avec la CI re-vérifiée à l'API sur la tête",
        ));
    }
    for bad in ["failure", "cancelled", "timed_out", "action_required"] {
        if pre.contains(bad) {
            return Err(Rejection::new(
                "E3",
                "ci",
                bad,
                "la section Pré-vérifications du dossier porte une conclusion d'échec — une CI non verte ne peut pas être mergée",
            ));
        }
    }
    for (name, _) in evidence.ci {
        if !pre.contains(name) {
            return Err(Rejection::new(
                "E3",
                "ci",
                name,
                "check-run re-vérifié à l'API absent de la section Pré-vérifications du dossier — la CI du dossier n'est pas la CI re-vérifiée",
            ));
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// E5 — Méthode true merge, nommée dans l'appel
// ---------------------------------------------------------------------------

fn check_e5(text: &str, evidence: &ExecutionEvidence) -> Result<(), Rejection> {
    if evidence.method != "merge" {
        return Err(Rejection::new(
            "E5",
            "méthode",
            evidence.method,
            "l'appel doit porter la méthode `merge` (jamais `squash`, jamais `rebase`) — une autre méthode n'est pas un merge du 1",
        ));
    }
    let appel = section_named(text, "Appel");
    if appel.is_empty() {
        return Err(Rejection::new(
            "E5",
            "appel",
            "section Appel absente",
            "l'exécution doit porter une section Appel (commande exacte, méthode, horodatage, sortie)",
        ));
    }
    if !appel.contains("méthode `merge`") {
        return Err(Rejection::new(
            "E5",
            "méthode",
            &truncate_line(appel.trim(), 120),
            "la section Appel doit nommer la méthode `merge` — une méthode autre que `merge` n'est pas un true merge (2 parents, DVG-01)",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// E6 — Appel nommé et rejouable (post-merge seulement)
// ---------------------------------------------------------------------------

fn check_e6(text: &str, evidence: &ExecutionEvidence) -> Result<(), Rejection> {
    let merge_commit = match evidence.merge_commit {
        Some(sha) if is_hex40(sha) => sha,
        _ => {
            return Err(Rejection::new(
                "E6",
                "appel",
                "merge commit absent ou illisible",
                "l'appel doit être consigné avec sa sortie (merge commit SHA complet, `merged: true`) — un merge dont l'appel n'est pas consigné n'est pas vérifiable",
            ));
        }
    };
    if !evidence.merged {
        return Err(Rejection::new(
            "E6",
            "merged",
            "false",
            "l'appel n'a pas mergé la PR (`merged: false`) — l'exécution n'a pas eu lieu",
        ));
    }
    if !evidence.resolver.resolves(merge_commit) {
        return Err(Rejection::new(
            "E6",
            "merge commit",
            merge_commit,
            "le merge commit consigné ne résout pas — un SHA cité est complet (40 hex) et résout",
        ));
    }
    let appel = section_named(text, "Appel");
    if appel.is_empty() {
        return Err(Rejection::new(
            "E6",
            "appel",
            "section Appel absente",
            "l'exécution doit porter une section Appel (commande exacte, méthode, horodatage, sortie)",
        ));
    }
    for marker in ["Commande", "Horodatage", "Sortie"] {
        if !appel.contains(marker) {
            return Err(Rejection::new(
                "E6",
                "appel",
                marker,
                &format!(
                    "la section Appel doit consigner {} (commande exacte, paramètres, horodatage, sortie) — sans elle, l'appel n'est pas rejouable",
                    marker
                ),
            ));
        }
    }
    if !appel.contains(merge_commit) {
        return Err(Rejection::new(
            "E6",
            "merge commit",
            merge_commit,
            "la section Appel doit consigner le merge commit de sortie — sans lui, l'appel n'est pas rejouable",
        ));
    }
    if !appel.contains("merged: true") {
        return Err(Rejection::new(
            "E6",
            "merged",
            "non consigné",
            "la section Appel doit consigner `merged: true` en sortie — sans lui, l'appel n'est pas vérifiable",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// E7 — Vérification post-merge par un tiers (post-merge seulement)
// ---------------------------------------------------------------------------

fn check_e7(
    text: &str,
    evidence: &ExecutionEvidence,
    authorized: &str,
) -> Result<(), Rejection> {
    let (parent1, parent2, master_head, open_prs) = match (
        evidence.parent1,
        evidence.parent2,
        evidence.master_head,
        evidence.open_prs,
    ) {
        (Some(p1), Some(p2), Some(mh), Some(op)) => (p1, p2, mh, op),
        _ => {
            return Err(Rejection::new(
                "E7",
                "vérification post-merge",
                "preuves post-merge absentes",
                "la vérification post-merge exige les preuves injectées (parents du merge commit, master HEAD, PR ouvertes) — sans elles, le merge n'est pas vérifié",
            ));
        }
    };
    if !is_hex40(parent1) || !is_hex40(parent2) {
        return Err(Rejection::new(
            "E7",
            "parents",
            &format!("{} / {}", parent1, parent2),
            "le merge commit doit porter 2 parents en SHA complets (DVG-01) — un merge à 1 parent n'est pas un true merge",
        ));
    }
    if parent1 == parent2 {
        return Err(Rejection::new(
            "E7",
            "parents",
            "parent 1 = parent 2",
            "le merge commit doit porter 2 parents distincts (DVG-01)",
        ));
    }
    if parent2 != authorized {
        return Err(Rejection::new(
            "E7",
            "parent 2",
            &truncate_line(parent2, 40),
            "le parent 2 du merge commit n'est pas la tête autorisée — le merge a porté une autre tête que celle autorisée par le jugement",
        ));
    }
    let merge_commit = match evidence.merge_commit {
        Some(sha) => sha,
        None => {
            return Err(Rejection::new(
                "E7",
                "merge commit",
                "absent",
                "la vérification post-merge exige le merge commit",
            ));
        }
    };
    if !evidence.merged {
        return Err(Rejection::new(
            "E7",
            "merged",
            "false",
            "la PR n'est pas mergée (`merged: false`) — la vérification post-merge échoue",
        ));
    }
    if evidence.merged_at.trim().is_empty() {
        return Err(Rejection::new(
            "E7",
            "merged_at",
            "absent",
            "la vérification post-merge exige `merged_at`",
        ));
    }
    if master_head != merge_commit {
        return Err(Rejection::new(
            "E7",
            "master",
            &truncate_line(master_head, 40),
            "master HEAD n'est pas le merge commit après le merge — le merge n'a pas atterri sur master",
        ));
    }
    if open_prs != 0 {
        return Err(Rejection::new(
            "E7",
            "pr ouvertes",
            &format!("{}", open_prs),
            "des PR restent ouvertes après le merge — la vérification post-merge exige 0 PR ouverte",
        ));
    }
    let post = section_named(text, "Vérification post-merge");
    if post.is_empty() {
        return Err(Rejection::new(
            "E7",
            "vérification post-merge",
            "section absente",
            "l'exécution doit porter une section Vérification post-merge (merge commit re-vérifié à l'API par un tiers)",
        ));
    }
    if !post.contains(merge_commit) || !post.contains(parent1) || !post.contains(parent2) {
        return Err(Rejection::new(
            "E7",
            "vérification post-merge",
            "merge commit ou parents absents",
            "la section Vérification post-merge doit consigner le merge commit et ses 2 parents re-vérifiés à l'API",
        ));
    }
    if !post.contains("2 parents") {
        return Err(Rejection::new(
            "E7",
            "vérification post-merge",
            "2 parents non consignés",
            "la section Vérification post-merge doit consigner les 2 parents (DVG-01)",
        ));
    }
    Ok(())
}
