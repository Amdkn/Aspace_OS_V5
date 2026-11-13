//! Vision — fonction Vision (D-N055 F1-8, Fondation 13 → 1).
//!
//! La fonction Vision tient les registres et les calendriers sans
//! contradiction locale, sans L00/N2/pulses comme sessions séparées. Elle
//! EST l'état de vision (D-F1-8-5) : il n'y a pas de contrôle de
//! recevabilité séparé avant un acte tiers — l'état rendu EST l'acte.
//! Un état = en-tête + lectures datées + comparaisons rejouables +
//! divergences portées avec statut + absences consignées + limites
//! nommées (Discover F1-8 §5.1).
//!
//! Règles (Discover F1-8 §6), appliquées dans l'ordre
//! V1 → V6 → V2 → V3 → V4 → V7 → V5 → V8 (du moins cher au plus cher) :
//! * V1 — Lecture datée. Chaque affirmation de vision porte sa source
//!   exacte (chemin + ligne/seq/SHA) ET son horodatage de lecture (ISO
//!   8601 avec offset, pas dans le futur). Une affirmation sans
//!   horodatage de lecture = rejet (elle est déjà périmée, Discover §0.2).
//! * V6 — La vision ne tranche pas. Elle porte les divergences, elle ne
//!   les résout pas ; elle ne modifie aucune source, ne consigne aucun
//!   reçu, n'écrit ni au registre ni au journal. Une vision qui tranche,
//!   corrige silencieusement ou écrit hors de son propre dossier = rejet
//!   (et révocation).
//! * V2 — Comparaison rejouable. Chaque comparaison cite les deux valeurs
//!   lues avec leurs horodatages. Une comparaison sans les deux valeurs,
//!   ou qui cite un seq inexistant, = rejet.
//! * V3 — Ancre W1 correcte. Un seuil de silence est calculé sur le
//!   dernier événement NOMMANT le dispatch (registre ou journal-router),
//!   jamais sur la dernière entrée globale ; le seuil est l'ancre + 12 h,
//!   et le franchissement porté doit être cohérent avec l'instant de la
//!   vision. Une ancre fausse (ex. journal 938 pour D-N053) = rejet —
//!   c'est le fautif F-V1.
//! * V4 — Divergence portée avec statut. Toute divergence connue est
//!   portée avec ses deux versions et son statut (`ouverte` / `classée` /
//!   `résolue` / `absente`) + sa source. Une divergence connue et tue,
//!   portée sans statut, ou lissée (« Sheet = miroir ») = rejet.
//! * V7 — Absence consignée. Une absence (reçu PR #38/#39, runs L00
//!   manquants, `correction` jamais émis) est consignée comme telle. Une
//!   absence tue = rejet.
//! * V5 — Fautif planté rejeté. La vision doit rejeter le fait fautif
//!   planté par le design (§5.3, F-V1) avec la règle nommée. Un fautif
//!   non rejeté = échec de la fonction — retour aux mécanismes d'origine
//!   (filet (a), plan §D5). V5 est le filet : il attrape un fautif qui
//!   aurait passé V1–V4 et V7 (par exemple une ancre fausse affirmée
//!   vraie par l'appelant).
//! * V8 — Limites nommées. La vision nomme ce qu'elle ne couvre pas (les
//!   13 mémoires, le bundle, FKB02 — Discover §2.8 hors périmètre) et ses
//!   réserves (fenêtre trouée, lectures datées). Une vision qui se
//!   présente comme complète sans limites nommées = rejet.
//!
//! V2/V3 sont les seuls qui touchent aux sources au moment de la vision ;
//! V5 est le contrôle qui prouve que la vision distingue le vrai du
//! fautif.
//!
//! Normalisation des fuseaux (D-F1-8-11) : tout horodatage comparé est
//! converti en ISO 8601 avec offset avant comparaison
//! (`normalize_timestamp`) ; un horodatage non normalisable est porté
//! `périmé` (étiquette), pas rejeté comme instant. Une étiquette « EDT »
//! en heure d'hiver (après le 2026-11-01) est périmée : l'instant vrai
//! est une heure plus tôt, en EST.
//!
//! Un état mal formé est rejeté avec sa règle nommée — jamais corrigé
//! silencieusement, jamais rendu quand même (D-F1-8-4 : une divergence
//! non portée, ou portée sans statut, ou portée avec un statut faux,
//! est une contradiction locale).
//!
//! Zéro dépendance externe, zéro appel sortant : les lectures datées,
//! les comparaisons, les divergences avec statut et le fautif planté
//! sont injectés par l'appelant ; la fonction ne contacte ni le fichier
//! local ni l'API elle-même.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Vision).

use super::{parse_iso8601_offset, Rejection};

/// Les quatre statuts qu'une divergence portée peut porter (Discover §5.1,
/// design D-F1-8-4).
pub const VISION_STATUSES: [&str; 4] = ["ouverte", "classée", "résolue", "absente"];

/// Une lecture datée (V1) : source exacte + valeur lue + horodatage de
/// lecture (ISO 8601 avec offset).
#[derive(Debug, Clone)]
pub struct DatedReading<'a> {
    /// La source exacte : chemin + ligne / seq / SHA.
    pub source: &'a str,
    /// La valeur lue (texte exact, tronqué par l'appelant si long).
    pub value: &'a str,
    /// L'horodatage de la lecture (ISO 8601 avec offset) — jamais vide.
    pub read_at: &'a str,
}

/// L'issue d'une comparaison rejouable (V2) : cohérente, divergente, ou
/// dérive datée — deux lectures du même registre à deux instants
/// distincts qui diffèrent (Discover §5.4a : une dérive n'est pas une
/// contradiction).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    Coherent,
    Divergent,
    Drift,
}

/// Une comparaison rejouable (V2) : les deux lectures citées avec leurs
/// valeurs exactes et leurs horodatages.
#[derive(Debug, Clone)]
pub struct Comparison<'a> {
    /// Le nom de la comparaison (ex. « registre ligne 938 = journal seq 37 »).
    pub name: &'a str,
    /// La première lecture.
    pub left: DatedReading<'a>,
    /// La seconde lecture.
    pub right: DatedReading<'a>,
    /// L'issue de la comparaison.
    pub outcome: Outcome,
    /// Le seq cité par la comparaison, quand elle cite le journal
    /// (F-V2 : un seq cité au-delà du dernier seq n'existe pas).
    pub cited_seq: Option<usize>,
}

/// Une divergence portée (V4) : ses deux versions, son statut, sa source
/// et sa date.
#[derive(Debug, Clone)]
pub struct Divergence<'a> {
    /// Le nom de la divergence (identique au nom porté dans
    /// `known_divergences`).
    pub name: &'a str,
    /// La première version.
    pub version_a: &'a str,
    /// La seconde version.
    pub version_b: &'a str,
    /// Le statut, l'un des quatre (`VISION_STATUSES`).
    pub status: &'a str,
    /// La source du classement (ordre, run, lecture datée).
    pub source: &'a str,
    /// La date du fait porté.
    pub date: &'a str,
}

/// Un seuil calendaire (V3) : l'ancre W1 est le dernier événement NOMMANT
/// le dispatch, jamais la dernière entrée globale.
#[derive(Debug, Clone)]
pub struct Threshold<'a> {
    /// Le dispatch surveillé (ex. « D-N053 »).
    pub dispatch_id: &'a str,
    /// Le journal cité comme ancre (ex. 938).
    pub anchor_journal: u32,
    /// L'ancre nomme-t-elle le dispatch ? Faux pour F-V1 : le journal 938
    /// nomme D-N055, pas D-N053.
    pub anchor_names_dispatch: bool,
    /// Le dispatch que l'ancre nomme réellement.
    pub anchor_dispatch_named: &'a str,
    /// L'horodatage de l'ancre (ISO 8601 avec offset).
    pub anchor_at: &'a str,
    /// Le seuil = l'ancre + 12 h (ISO 8601 avec offset).
    pub threshold_at: &'a str,
    /// Le seuil est-il porté franchi ?
    pub crossed: bool,
    /// Le dernier événement nommant réellement le dispatch (raison V3) —
    /// ex. « journal 930, ~21:00, seuil ~09:00, non franchi ».
    pub correct_anchor: &'a str,
}

/// Le fait fautif planté (V5) : le triplet qui l'identifie
/// (dispatch, ancre, franchissement affirmé).
#[derive(Debug, Clone)]
pub struct PlantedFautif<'a> {
    pub dispatch_id: &'a str,
    pub anchor_journal: u32,
    pub crossed: bool,
}

/// L'état de vision soumis à la fonction — toutes les entrées sont
/// injectées par l'appelant, qui les a relues au fichier.
pub struct VisionState<'a> {
    /// Les lectures datées (V1).
    pub readings: &'a [DatedReading<'a>],
    /// Les comparaisons rejouables (V2).
    pub comparisons: &'a [Comparison<'a>],
    /// Les divergences portées (V4).
    pub divergences: &'a [Divergence<'a>],
    /// Les seuils calendaires (V3).
    pub thresholds: &'a [Threshold<'a>],
    /// Les noms des divergences connues — chacune doit être portée (V4).
    pub known_divergences: &'a [&'a str],
    /// Les absences consignées (V7).
    pub absences: &'a [&'a str],
    /// Les noms des absences connues — chacune doit être consignée (V7).
    pub known_absences: &'a [&'a str],
    /// Les limites nommées (V8).
    pub limits: &'a [&'a str],
    /// La vision se présente-t-elle comme complète ? (V8 : doit être faux.)
    pub claims_complete: bool,
    /// La vision tranche-t-elle une divergence ? (V6 : doit être faux.)
    pub claims_resolution: bool,
    /// La vision modifie-t-elle une source ? (V6 : doit être faux.)
    pub modifies_source: bool,
    /// La vision consigne-t-elle un reçu ? (V6 : doit être faux.)
    pub consigns_receipt: bool,
    /// Le fait fautif planté (V5) — `None` = aucun fautif injecté.
    pub planted_fautif: Option<PlantedFautif<'a>>,
    /// Le dernier seq du journal au moment de la vision (V2 : un seq cité
    /// au-delà n'existe pas).
    pub max_seq: usize,
}

/// Un état de vision accepté : ses comptes, 0 contradiction non portée.
#[derive(Debug)]
pub struct ValidVision {
    pub readings: usize,
    pub comparisons: usize,
    pub divergences: usize,
    pub thresholds: usize,
    pub absences: usize,
    pub limits: usize,
    /// Toujours 0 — c'est la définition de « 0 contradiction »
    /// (D-F1-8-4 : 0 contradiction non portée).
    pub unported_contradictions: usize,
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

/// Les mots d'un nom (minuscules, découpés sur tout ce qui n'est pas
/// alphanumérique) — pour le contrôle de lissage V4.
fn name_tokens(name: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    for c in name.chars() {
        if c.is_alphanumeric() {
            current.extend(c.to_lowercase());
        } else if !current.is_empty() {
            tokens.push(std::mem::take(&mut current));
        }
    }
    if !current.is_empty() {
        tokens.push(current);
    }
    tokens
}

/// Le nom de la comparaison couvre-t-il le nom de la divergence (tous
/// ses mots sont dans le nom de la divergence) ? Une comparaison
/// « Workgraph : Sheet = miroir » couvre la divergence « Workgraph Sheet
/// ↔ miroir (Bill/Coordinateur) » ; une comparaison « N2 Run #484 vs L00
/// Run #702 » ne couvre pas « N2 ombre vs L00 » (run, 484, 702 absents).
fn name_covers(comparison_name: &str, divergence_name: &str) -> bool {
    let c_tokens = name_tokens(comparison_name);
    let d_tokens = name_tokens(divergence_name);
    !c_tokens.is_empty()
        && c_tokens
            .iter()
            .all(|t| d_tokens.iter().any(|d| d == t))
}

/// Un horodatage est-il une lecture datée valide (V1) : ISO 8601 avec
/// offset, date valide, pas dans le futur ?
fn dated(read_at: &str, now_unix: i64) -> Result<i64, Rejection> {
    match parse_iso8601_offset(read_at) {
        Some(epoch) if epoch <= now_unix => Ok(epoch),
        Some(_) => Err(rejection(
            "V1",
            "read_at",
            read_at,
            "l'horodatage de lecture est dans le futur par rapport à l'instant de la vision",
        )),
        None => Err(rejection(
            "V1",
            "read_at",
            read_at,
            "la lecture n'est pas datée — une affirmation sans horodatage de lecture (ISO 8601 avec offset) est déjà périmée",
        )),
    }
}

/// Valide un état de vision, dans l'ordre
/// V1 → V6 → V2 → V3 → V4 → V7 → V5 → V8.
///
/// `now_unix` est l'instant de la vision (V1 : aucune lecture dans le
/// futur ; V3 : le franchissement porté doit être cohérent avec lui).
pub fn validate_vision(
    state: &VisionState,
    now_unix: i64,
) -> Result<ValidVision, Rejection> {
    // V1 — Lecture datée : chaque lecture porte sa source exacte et son
    // horodatage de lecture ; chaque comparaison est datée des deux côtés ;
    // chaque seuil est daté (ancre et seuil).
    for reading in state.readings {
        if reading.source.trim().is_empty() {
            return Err(rejection(
                "V1",
                "source",
                reading.value,
                "une lecture sans source exacte n'est pas une lecture datée",
            ));
        }
        dated(reading.read_at, now_unix)?;
    }
    for comparison in state.comparisons {
        dated(comparison.left.read_at, now_unix)?;
        dated(comparison.right.read_at, now_unix)?;
    }
    for threshold in state.thresholds {
        if parse_iso8601_offset(threshold.anchor_at).is_none() {
            return Err(rejection(
                "V1",
                "anchor_at",
                threshold.anchor_at,
                "l'ancre du seuil n'est pas datée (ISO 8601 avec offset) — un seuil sans ancre datée n'est pas calculable",
            ));
        }
        if parse_iso8601_offset(threshold.threshold_at).is_none() {
            return Err(rejection(
                "V1",
                "threshold_at",
                threshold.threshold_at,
                "le seuil n'est pas daté (ISO 8601 avec offset)",
            ));
        }
    }

    // V6 — La vision ne tranche pas.
    if state.claims_resolution {
        return Err(rejection(
            "V6",
            "(état)",
            "la vision tranche une divergence",
            "la vision porte les divergences, elle ne les résout pas — la résolution appartient à la fonction de jugement ou à un événement de correction explicite",
        ));
    }
    if state.modifies_source {
        return Err(rejection(
            "V6",
            "(état)",
            "la vision modifie une source",
            "la vision lit, compare, porte — elle ne modifie aucune source",
        ));
    }
    if state.consigns_receipt {
        return Err(rejection(
            "V6",
            "(état)",
            "la vision consigne un reçu",
            "la vision ne consigne aucun reçu — le reçu H-F1-7 est consigné après le merge par un exécutant dédié",
        ));
    }

    // V2 — Comparaison rejouable : les deux valeurs sont citées ; un seq
    // cité existe (dernier seq connu : max_seq).
    for comparison in state.comparisons {
        if comparison.left.value.trim().is_empty() || comparison.right.value.trim().is_empty() {
            return Err(rejection(
                "V2",
                "comparaison",
                comparison.name,
                "une comparaison sans les deux valeurs n'est pas rejouable — les deux lectures doivent être citées avec leurs valeurs exactes",
            ));
        }
        if let Some(seq) = comparison.cited_seq {
            if seq > state.max_seq || seq == 0 {
                return Err(rejection(
                    "V2",
                    "cited_seq",
                    &format!("seq {} (dernier seq {})", seq, state.max_seq),
                    "la valeur citée n'existe pas — une comparaison qui cite un seq inexistant n'est pas rejouable",
                ));
            }
        }
    }

    // V3 — Ancre W1 correcte : l'ancre nomme le dispatch ; le seuil est
    // l'ancre + 12 h ; le franchissement porté est cohérent avec l'instant
    // de la vision.
    for threshold in state.thresholds {
        if !threshold.anchor_names_dispatch {
            return Err(rejection(
                "V3",
                "anchor_journal",
                &format!(
                    "journal {} pour {}",
                    threshold.anchor_journal, threshold.dispatch_id
                ),
                &format!(
                    "le journal {} nomme {}, pas {} — l'ancre est fausse ; le dernier événement nommant {} est {}",
                    threshold.anchor_journal,
                    threshold.anchor_dispatch_named,
                    threshold.dispatch_id,
                    threshold.dispatch_id,
                    threshold.correct_anchor
                ),
            ));
        }
        let anchor_epoch = parse_iso8601_offset(threshold.anchor_at)
            .expect("V1 garantit anchor_at parseable");
        let threshold_epoch = parse_iso8601_offset(threshold.threshold_at)
            .expect("V1 garantit threshold_at parseable");
        if threshold_epoch != anchor_epoch + 12 * 3600 {
            return Err(rejection(
                "V3",
                "threshold_at",
                threshold.threshold_at,
                "le seuil n'est pas l'ancre + 12 h — un seuil W1 se calcule sur l'ancre, jamais sur la dernière entrée globale",
            ));
        }
        if threshold.crossed && now_unix < threshold_epoch {
            return Err(rejection(
                "V3",
                "crossed",
                "franchi",
                "franchissement affirmé avant le seuil — le seuil n'est pas encore atteint à l'instant de la vision",
            ));
        }
        if !threshold.crossed && now_unix >= threshold_epoch {
            return Err(rejection(
                "V3",
                "crossed",
                "non franchi",
                "seuil dépassé mais porté non franchi — le silence a dépassé 12 h sur cette ancre",
            ));
        }
    }

    // V4 — Divergence portée avec statut : chaque divergence connue est
    // portée (même nom, statut valide, source non vide) ; une comparaison
    // cohérente qui recouvre une divergence connue la lisse.
    for divergence in state.divergences {
        if !VISION_STATUSES.contains(&divergence.status) {
            return Err(rejection(
                "V4",
                "status",
                divergence.status,
                "une divergence portée sans statut valide (ouverte / classée / résolue / absente) est une contradiction locale",
            ));
        }
        if divergence.source.trim().is_empty() {
            return Err(rejection(
                "V4",
                "source",
                divergence.name,
                "une divergence portée sans source n'est pas portée — le classement doit être cité avec sa source",
            ));
        }
    }
    for known in state.known_divergences {
        if !state.divergences.iter().any(|d| d.name == *known) {
            return Err(rejection(
                "V4",
                "divergence",
                known,
                "divergence connue non portée — une divergence connue et tue est une contradiction locale",
            ));
        }
    }
    // Lissage : une comparaison qui affirme l'égalité (cohérente) sur
    // une paire de registres dont la divergence est portée (même nom,
    // aux mots près) lisse la divergence connue — F-V4.
    for comparison in state.comparisons {
        if comparison.outcome != Outcome::Coherent {
            continue;
        }
        for divergence in state.divergences {
            if name_covers(comparison.name, divergence.name) {
                return Err(rejection(
                    "V4",
                    "comparaison",
                    comparison.name,
                    &format!(
                        "divergence connue lissée — la comparaison affirme l'égalité alors que la divergence « {} » est portée avec le statut « {} »",
                        divergence.name, divergence.status
                    ),
                ));
            }
        }
    }

    // V7 — Absence consignée : chaque absence connue est consignée.
    for known in state.known_absences {
        if !state.absences.iter().any(|a| a.contains(known)) {
            return Err(rejection(
                "V7",
                "absence",
                known,
                "absence connue non consignée — une absence tue est une contradiction locale",
            ));
        }
    }

    // V5 — Fautif planté rejeté (le filet) : aucun seuil porté ne doit
    // être le fait fautif planté.
    if let Some(planted) = &state.planted_fautif {
        for threshold in state.thresholds {
            if threshold.dispatch_id == planted.dispatch_id
                && threshold.anchor_journal == planted.anchor_journal
                && threshold.crossed == planted.crossed
            {
                return Err(rejection(
                    "V5",
                    "threshold",
                    &format!(
                        "{} ancre journal {} franchi={}",
                        threshold.dispatch_id, threshold.anchor_journal, threshold.crossed
                    ),
                    "fait fautif planté non rejeté — l'état affirme le franchissement fautif ; la fonction Vision revient à ses mécanismes d'origine",
                ));
            }
        }
    }

    // V8 — Limites nommées.
    if state.limits.is_empty() {
        return Err(rejection(
            "V8",
            "limites",
            "(aucune)",
            "la vision ne nomme pas ses limites — une vision qui se présente sans limites nommées n'est pas une vision tenue",
        ));
    }
    if state.claims_complete {
        return Err(rejection(
            "V8",
            "(état)",
            "la vision se présente comme complète",
            "la vision ne couvre pas tout (13 mémoires, bundle, FKB02 hors périmètre) — une vision qui se présente comme complète sans limites nommées est rejetée",
        ));
    }

    Ok(ValidVision {
        readings: state.readings.len(),
        comparisons: state.comparisons.len(),
        divergences: state.divergences.len(),
        thresholds: state.thresholds.len(),
        absences: state.absences.len(),
        limits: state.limits.len(),
        unported_contradictions: 0,
    })
}

// ---------------------------------------------------------------------------
// Temps — normalisation des fuseaux (D-F1-8-11)
// ---------------------------------------------------------------------------

fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y_adj = if m <= 2 { y - 1 } else { y };
    let era = if y_adj >= 0 { y_adj } else { y_adj - 399 } / 400;
    let yoe = y_adj - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146097 + doe - 719468
}

fn civil_from_days(z: i64) -> (i64, i64, i64) {
    let z = z + 719468;
    let era = if z >= 0 { z } else { z - 146096 } / 146097;
    let doe = z - era * 146097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    (if m <= 2 { y + 1 } else { y }, m, d)
}

fn days_in_month_local(y: i64, m: i64) -> i64 {
    match m {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 => {
            if (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 {
                29
            } else {
                28
            }
        }
        _ => 0,
    }
}

/// Formate des secondes Unix en ISO 8601 avec l'offset donné (en secondes,
/// ex. -18000 pour -05:00).
pub fn format_iso_offset(epoch_utc: i64, offset_seconds: i64) -> String {
    let local = epoch_utc + offset_seconds;
    let days = local.div_euclid(86400);
    let secs = local.rem_euclid(86400);
    let (y, m, d) = civil_from_days(days);
    let (hh, mm, ss) = (secs / 3600, (secs % 3600) / 60, secs % 60);
    let sign = if offset_seconds < 0 { '-' } else { '+' };
    let off = offset_seconds.abs();
    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}{}{:02}:{:02}",
        y, m, d, hh, mm, ss, sign, off / 3600, (off % 3600) / 60
    )
}

/// Le seuil W1 d'une ancre : l'ancre + 12 h, dans le même offset que
/// l'ancre. `None` si l'ancre n'est pas un ISO 8601 avec offset.
pub fn threshold_after(anchor_iso: &str) -> Option<String> {
    let epoch = parse_iso8601_offset(anchor_iso)?;
    let offset_seconds = parse_offset_seconds(anchor_iso)?;
    Some(format_iso_offset(epoch + 12 * 3600, offset_seconds))
}

/// L'offset (en secondes) d'un ISO 8601 avec offset, ou `None`.
fn parse_offset_seconds(iso: &str) -> Option<i64> {
    let b = iso.as_bytes();
    if b.len() != 25 || b[22] != b':' {
        return None;
    }
    let sign = match b[19] {
        b'+' => 1,
        b'-' => -1,
        _ => return None,
    };
    let parse = |s: &str| -> Option<i64> {
        if s.is_empty() || !s.bytes().all(|c| c.is_ascii_digit()) {
            return None;
        }
        s.parse::<i64>().ok()
    };
    let h = parse(&iso[20..22])?;
    let m = parse(&iso[23..25])?;
    Some(sign * (h * 3600 + m * 60))
}

/// Un horodatage normalisé : son ISO 8601 avec offset, et le statut de
/// son étiquette de fuseau (`ok`, ou `périmé` quand l'étiquette est
/// fausse — « EDT » en heure d'hiver).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NormalizedTimestamp {
    pub iso: String,
    pub label_status: &'static str,
}

/// Normalise un horodatage avant comparaison (D-F1-8-11).
///
/// * Un ISO 8601 avec offset est déjà normalisé (`ok`).
/// * Un horodatage mural « AAAA-MM-JJ HH:MM EST » est converti en ISO
///   avec offset -05:00 (`ok`).
/// * Un horodatage mural « AAAA-MM-JJ HH:MM EDT » est converti avec
///   offset -04:00 (`ok`) — sauf après la fin de l'heure d'été
///   (2026-11-01) : l'étiquette est alors périmée, l'instant vrai est
///   une heure plus tôt, en EST (`périmé`).
/// * Tout le reste retourne `None` : l'horodatage est porté `périmé`
///   (étiquette), pas rejeté comme instant.
pub fn normalize_timestamp(raw: &str) -> Option<NormalizedTimestamp> {
    let raw = raw.trim();
    if parse_iso8601_offset(raw).is_some() {
        return Some(NormalizedTimestamp {
            iso: raw.to_string(),
            label_status: "ok",
        });
    }
    // Horodatage mural : « AAAA-MM-JJ HH:MM EDT|EST ».
    let b = raw.as_bytes();
    if b.len() < 20 || b[10] != b' ' || b[13] != b':' || b[16] != b' ' {
        return None;
    }
    let date = &raw[0..10];
    let hour: i64 = raw[11..13].parse().ok()?;
    let minute: i64 = raw[14..16].parse().ok()?;
    let label = &raw[17..];
    if hour > 23 || minute > 59 {
        return None;
    }
    let year: i64 = date[0..4].parse().ok()?;
    let month: i64 = date[5..7].parse().ok()?;
    let day: i64 = date[8..10].parse().ok()?;
    if !(1..=12).contains(&month) || day < 1 || day > days_in_month_local(year, month) {
        return None;
    }
    let days = days_from_civil(year, month, day);
    let wall = days * 86400 + hour * 3600 + minute * 60;
    match label {
        "EST" => Some(NormalizedTimestamp {
            iso: format_iso_offset(wall + 5 * 3600, -5 * 3600),
            label_status: "ok",
        }),
        "EDT" => {
            // Fin de l'heure d'été 2026 : 2026-11-01. Après, « EDT » est
            // une étiquette périmée — l'instant vrai est une heure plus
            // tôt, en EST (N2 Run #484 : « 03:13 EDT » = 02:13 EST).
            if date >= "2026-11-01" {
                Some(NormalizedTimestamp {
                    iso: format_iso_offset(wall - 3600 + 5 * 3600, -5 * 3600),
                    label_status: "périmé",
                })
            } else {
                Some(NormalizedTimestamp {
                    iso: format_iso_offset(wall + 4 * 3600, -4 * 3600),
                    label_status: "ok",
                })
            }
        }
        _ => None,
    }
}

// ---------------------------------------------------------------------------
// Dossier fautif planté (A-F1-8-1) — lecture seule, sans I/O
// ---------------------------------------------------------------------------

/// La faute plantée F-V1, extraite du dossier fautif : le dispatch, le
/// journal cité comme ancre, le dispatch que l'ancre nomme réellement, le
/// seuil affirmé et le dernier événement nommant réellement le dispatch.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FautifClaim {
    pub dispatch_id: String,
    pub anchor_journal: u32,
    pub anchor_dispatch_named: String,
    pub threshold_claimed: String,
    pub correct_anchor: String,
}

fn fautif_field<'a>(text: &'a str, marker: &str) -> Option<&'a str> {
    for line in text.lines() {
        if let Some(rest) = line.trim_start().strip_prefix(marker) {
            return Some(rest.trim());
        }
    }
    None
}

/// Extrait la faute plantée d'un dossier fautif (`VISION-FAUTIF-1.md`) :
/// champs `**Dispatch :**`, `**Ancre :** journal NNN`, `**Ancre nomme :**`,
/// `**Seuil affirmé :**`, `**Dernier événement nommant :**`.
pub fn parse_fautif(text: &str) -> Result<FautifClaim, String> {
    let get = |m: &str| {
        fautif_field(text, m)
            .map(|s| s.to_string())
            .ok_or_else(|| format!("champ {m} manquant dans le dossier fautif"))
    };
    let dispatch_id = get("**Dispatch :**")?;
    let anchor_line = get("**Ancre :**")?;
    let anchor_journal: u32 = anchor_line
        .split_whitespace()
        .find_map(|w| w.trim_matches(|c: char| !c.is_ascii_digit()).parse().ok())
        .ok_or_else(|| {
            format!(
                "aucun numéro de journal dans l'ancre '{}'",
                anchor_line
            )
        })?;
    // Le numéro est le premier nombre qui suit le mot « journal ».
    let anchor_journal = anchor_line
        .split("journal")
        .nth(1)
        .and_then(|rest| {
            rest.split_whitespace()
                .next()
                .and_then(|w| w.trim_matches(|c: char| !c.is_ascii_digit()).parse().ok())
        })
        .unwrap_or(anchor_journal);
    Ok(FautifClaim {
        dispatch_id,
        anchor_journal,
        anchor_dispatch_named: get("**Ancre nomme :**")?,
        threshold_claimed: get("**Seuil affirmé :**")?,
        correct_anchor: get("**Dernier événement nommant :**")?,
    })
}

#[cfg(test)]
mod unit_tests {
    use super::*;

    #[test]
    fn normalisation_edt_perimee() {
        // N2 Run #484 : « 2026-11-13 03:13 EDT » = 02:13 EST, étiquette périmée.
        let n = normalize_timestamp("2026-11-13 03:13 EDT").unwrap();
        assert_eq!(n.iso, "2026-11-13T02:13:00-05:00");
        assert_eq!(n.label_status, "périmé");
        // Un ISO avec offset est déjà normalisé.
        let n = normalize_timestamp("2026-11-13T02:13:00-05:00").unwrap();
        assert_eq!(n.iso, "2026-11-13T02:13:00-05:00");
        assert_eq!(n.label_status, "ok");
        // EDT avant la fin de l'heure d'été : offset -04:00, étiquette ok.
        let n = normalize_timestamp("2026-10-31 03:13 EDT").unwrap();
        assert_eq!(n.iso, "2026-10-31T03:13:00-04:00");
        assert_eq!(n.label_status, "ok");
        // EST mural : offset -05:00, étiquette ok.
        let n = normalize_timestamp("2026-11-13 02:08 EST").unwrap();
        assert_eq!(n.iso, "2026-11-13T02:08:00-05:00");
        assert_eq!(n.label_status, "ok");
        // Non normalisable : porté périmé, pas rejeté comme instant.
        assert_eq!(normalize_timestamp("hier vers 2 h"), None);
        assert_eq!(normalize_timestamp("2026-13-40 25:99 EST"), None);
    }

    #[test]
    fn seuil_ancre_plus_12h() {
        assert_eq!(
            threshold_after("2026-11-13T01:52:00-05:00").as_deref(),
            Some("2026-11-13T13:52:00-05:00")
        );
        assert_eq!(
            threshold_after("2026-11-12T21:00:00-05:00").as_deref(),
            Some("2026-11-13T09:00:00-05:00")
        );
        assert_eq!(threshold_after("2026-11-13 01:52 EST"), None);
    }

    #[test]
    fn parse_fautif_champs() {
        let text = "**Dispatch :** D-N053\n**Ancre :** journal 938 (F1-7 CLOSE)\n**Ancre nomme :** D-N055\n**Seuil affirmé :** FRANCHI à 02:15 EST\n**Dernier événement nommant :** journal 930, ~21:00, seuil ~09:00, non franchi\n";
        let claim = parse_fautif(text).unwrap();
        assert_eq!(claim.dispatch_id, "D-N053");
        assert_eq!(claim.anchor_journal, 938);
        assert_eq!(claim.anchor_dispatch_named, "D-N055");
        assert_eq!(claim.threshold_claimed, "FRANCHI à 02:15 EST");
        assert_eq!(
            claim.correct_anchor,
            "journal 930, ~21:00, seuil ~09:00, non franchi"
        );
    }
}
