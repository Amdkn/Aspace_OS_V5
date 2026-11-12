//! Fonction Découvrir — D-N055 F1-4, Fondation 13 → 1.
//!
//! La fonction Découvrir valide un Discover comme contrôle de recevabilité
//! du dossier, sans Bill comme session séparée. Elle ne juge pas une PR
//! (fonction Juger, F1-5) : elle applique les règles D1–D8 du Discover
//! F1-4 §4, dans l'ordre D1 → D4 → D5 → D7 → D2 → D3 → D6 → D8 (du moins
//! cher au plus cher — les contrôles D2/D3 sont les seuls qui touchent aux
//! SHA et aux ancres ; tous les autres sont locaux au document).
//!
//! Règles (Discover F1-4 §4) :
//! * D1 — En-tête complet : mission, auteur = fonction Découvrir (pas une
//!   session), date, statut (pas un design, pas une signature, pas une
//!   exécution), sources lues en entier nommées, règle de vérification.
//! * D2 — Chaque fait vérifié : chaque SHA complet (40 hex) cité résout
//!   (injecté par l'appelant, comme le résolveur de SHA du validateur) ;
//!   les faits de substrat du §2 (F1-2 CLOSE, F1-3 CLOSE) portent leur
//!   SHA complet et leur vérification à l'API ; aucun fait affirmé depuis
//!   un récit dans les §0/§2.
//! * D3 — Mesure zéro nommée et datée : le §0 porte des comptes et leur
//!   date ; le Master HEAD complet est cité et résout.
//! * D4 — Aucune décision tranchée : aucune décision « ADOPTÉE » ni
//!   signature hors des §4 (la règle elle-même) et §6 (le rejet motivé,
//!   qui décrit les fautifs) — ces deux sections décrivent la règle, elles
//!   ne tranchent pas.
//! * D5 — Aucune exécution : aucun reçu consigné ni PR ouverte par ce
//!   Discover — une mention niée (« Aucun reçu consigné par ce Discover »)
//!   n'est pas une exécution.
//! * D6 — Corrections portées en avant : la correction déclarée au §2
//!   (compte BYB F1-2 v2 : 14 214 o → 14 360 o, écart de 146 o) est
//!   présente avec sa valeur d'origine et son écart — une réécriture
//!   silencieuse l'efface, et D6 la détecte.
//! * D7 — Sources lues en entier : chaque source nommée dans l'en-tête
//!   est attestée « lu en entier » sur sa ligne du §10.
//! * D8 — Limites nommées : le Discover nomme ce qu'il ne prouve pas et
//!   les questions qu'il laisse au design.
//!
//! Frontière (voir fiche, Divergence) : un SHA court (7 car.) est une
//! référence, pas une citation comme preuve — la citation (merge, HEAD)
//! doit porter la forme complète ; le contrôle D2 ne rejette donc pas un
//! SHA court isolé, il exige la forme complète là où le fait est affirmé.
//! Zéro dépendance externe, zéro appel sortant : la résolution des SHA est
//! injectée par l'appelant (`ShaResolver`) ; la seule lecture est le
//! fichier Discover lui-même.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Découvrir).

use super::{Rejection, ShaResolver};

/// Un Discover validé (prêt à être lu par la fonction de design — la
/// lecture et l'acceptation restent l'acte de la destinataire, §5).
#[derive(Debug, Clone)]
pub struct ValidDiscover {
    /// Mission portée par l'en-tête (ex. `D-N055 F1-4`).
    pub mission: String,
    /// Nombre de SHA complets vérifiés (D2/D3).
    pub shas_checked: usize,
}

/// Valide un Discover (texte Markdown) contre D1–D8, dans l'ordre
/// D1 → D4 → D5 → D7 → D2 → D3 → D6 → D8. Le premier rejet rencontré est
/// retourné, avec sa raison nommée — jamais corrigé silencieusement.
pub fn validate_discover(
    text: &str,
    resolver: &dyn ShaResolver,
) -> Result<ValidDiscover, Rejection> {
    check_d1(text)?;
    check_d4(text)?;
    check_d5(text)?;
    check_d7(text)?;
    let shas_checked = check_d2(text, resolver)?;
    check_d3(text, resolver)?;
    check_d6(text)?;
    check_d8(text)?;
    Ok(ValidDiscover {
        mission: "D-N055 F1-4".to_string(),
        shas_checked,
    })
}

// ---------------------------------------------------------------------------
// Découpage du document en sections (« ## N. »)
// ---------------------------------------------------------------------------

/// Renvoie le texte de la section `n` (de sa ligne `## n.` à la section
/// suivante, ou à la fin du document). Chaîne vide si absente.
fn section_of<'a>(text: &'a str, n: u32) -> &'a str {
    let prefix = format!("{}.", n);
    let mut start: Option<usize> = None;
    let mut end = text.len();
    let mut pos = 0usize;
    for line in text.split_inclusive('\n') {
        if line.starts_with("## ") {
            if start.is_some() {
                end = pos;
                break;
            }
            if line.trim_start_matches("## ").starts_with(&prefix) {
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

/// Texte du document hors des sections `excluded` (en-tête inclus).
fn text_except_sections(text: &str, excluded: &[u32]) -> String {
    let mut out = String::new();
    let mut pos = 0usize;
    let mut current: Option<u32> = None;
    for line in text.split_inclusive('\n') {
        if line.starts_with("## ") {
            let num: Option<u32> = line
                .trim_start_matches("## ")
                .split('.')
                .next()
                .and_then(|s| s.trim().parse().ok());
            current = num;
        }
        let skip = match current {
            Some(n) => excluded.contains(&n),
            None => false,
        };
        if !skip {
            out.push_str(line);
        }
        pos += line.len();
    }
    let _ = pos;
    out
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

// ---------------------------------------------------------------------------
// D1 — En-tête complet
// ---------------------------------------------------------------------------

fn check_d1(text: &str) -> Result<(), Rejection> {
    let required: [(&str, &str, &str); 6] = [
        ("mission", "Mission :", "la mission (D-N055 F1-4)"),
        (
            "auteur",
            "fonction Découvrir",
            "l'auteur = fonction Découvrir, pas une session",
        ),
        ("date", "Date :", "la date du Discover"),
        (
            "statut",
            "pas un design, pas une signature, pas une exécution",
            "le statut (pas un design, pas une signature, pas une exécution)",
        ),
        (
            "sources",
            "Sources lues en entier",
            "les sources lues en entier, nommées",
        ),
        (
            "règle de vérification",
            "Règle de ce document",
            "la règle de vérification du document",
        ),
    ];
    for (field, marker, detail) in required {
        if !text.contains(marker) {
            return Err(Rejection::new(
                "D1",
                field,
                "absent",
                &format!("en-tête incomplet : {} manquant", detail),
            ));
        }
    }
    if !text.contains("pas de session Bill séparée") {
        return Err(Rejection::new(
            "D1",
            "auteur",
            "fonction Découvrir",
            "en-tête incomplet : l'auteur doit dire « pas de session Bill séparée »",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// D4 — Aucune décision tranchée
// ---------------------------------------------------------------------------

fn check_d4(text: &str) -> Result<(), Rejection> {
    // Les §4 (la règle) et §6 (le rejet motivé) décrivent la règle et les
    // fautifs — ils ne tranchent pas. Toute décision hors d'eux est un rejet.
    let body = text_except_sections(text, &[4, 6]);
    for line in body.lines() {
        if line.contains("ADOPTÉ") {
            return Err(Rejection::new(
                "D4",
                "décision",
                &truncate_line(line.trim(), 120),
                "le Discover propose, il ne tranche pas — une décision « ADOPTÉE » ne peut pas figurer dans un Discover",
            ));
        }
        if line.contains("SIGNÉ") {
            return Err(Rejection::new(
                "D4",
                "signature",
                &truncate_line(line.trim(), 120),
                "le Discover ne signe rien — la signature est l'acte de la fonction de design, pas du Discover",
            ));
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// D5 — Aucune exécution
// ---------------------------------------------------------------------------

fn check_d5(text: &str) -> Result<(), Rejection> {
    let markers = [
        "consigné par ce Discover",
        "ouverte par ce Discover",
        "mergée par ce Discover",
        "ouvre la PR",
    ];
    for marker in markers {
        let mut search_from = 0usize;
        while let Some(rel) = text[search_from..].find(marker) {
            let idx = search_from + rel;
            // Fenêtre de négation : « Aucun reçu consigné par ce Discover »
            // n'est pas une exécution, c'est sa négation.
            let start = floor_boundary(text, idx.saturating_sub(48));
            let before = &text[start..idx];
            if !before.contains("Aucun") && !before.contains("aucun") {
                return Err(Rejection::new(
                    "D5",
                    "exécution",
                    marker,
                    "le Discover n'exécute rien — aucun reçu consigné, aucune PR ouverte par ce Discover",
                ));
            }
            search_from = idx + marker.len();
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// D7 — Sources lues en entier
// ---------------------------------------------------------------------------

/// Chemins entre backticks dans la liste des sources de l'en-tête.
fn header_sources(text: &str) -> Vec<String> {
    let start = match text.find("Sources lues en entier") {
        Some(i) => i,
        None => return Vec::new(),
    };
    let end = text[start..]
        .find("Règle de ce document")
        .map(|r| start + r)
        .unwrap_or(text.len());
    let header = &text[start..end];
    let mut sources = Vec::new();
    let mut rest = header;
    while let Some(open) = rest.find('`') {
        let after = &rest[open + 1..];
        match after.find('`') {
            Some(close) => {
                let path = &after[..close];
                if path.contains('/') && (path.ends_with(".md") || path.ends_with(".json")) {
                    sources.push(path.to_string());
                }
                rest = &after[close + 1..];
            }
            None => break,
        }
    }
    sources
}

fn check_d7(text: &str) -> Result<(), Rejection> {
    let sources = header_sources(text);
    if sources.is_empty() {
        return Err(Rejection::new(
            "D7",
            "sources",
            "absent",
            "aucune source nommée dans l'en-tête — D1 aurait dû rejeter avant",
        ));
    }
    let s10 = section_of(text, 10);
    for path in &sources {
        let mut attested = false;
        for line in s10.lines() {
            // « non lu en entier » n'est pas une attestation — c'est
            // l'aveu de son absence (leçon §0.4.5.1).
            if line.contains(path.as_str())
                && line.contains("lu en entier")
                && !line.contains("non lu en entier")
            {
                attested = true;
                break;
            }
        }
        if !attested {
            return Err(Rejection::new(
                "D7",
                "source",
                path,
                "source citée dans l'en-tête sans attestation « lu en entier » au §10 — une source citée non lue (ou lue partiellement) n'est pas un Discover",
            ));
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// D2 — Chaque fait vérifié
// ---------------------------------------------------------------------------

fn check_d2(text: &str, resolver: &dyn ShaResolver) -> Result<usize, Rejection> {
    // (a) Tout SHA complet cité résout.
    let mut checked = 0usize;
    let mut seen: Vec<String> = Vec::new();
    for (run, len) in hex_runs(text) {
        if len == 40 && is_hex40(&run) && !seen.contains(&run) {
            seen.push(run.clone());
            checked += 1;
            if !resolver.resolves(&run) {
                return Err(Rejection::new(
                    "D2",
                    "sha",
                    &run,
                    "SHA complet cité mais ne résout pas — un SHA cité est complet (40 hex) et résout",
                ));
            }
        }
    }
    // (b) Les faits de substrat du §2 portent leur ancre : la ligne
    // F1-3 CLOSE porte le SHA complet du merge et la vérification à
    // l'API ; la ligne F1-2 CLOSE porte son SHA complet.
    let s2 = section_of(text, 2);
    for line in s2.lines() {
        if line.contains("F1-3 CLOSE") {
            let has_sha = line.chars().collect::<Vec<_>>().windows(40).any(|w| {
                let s: String = w.iter().collect();
                is_hex40(&s)
            }) || hex_runs(line).iter().any(|(_, l)| *l == 40);
            if !has_sha || !line.contains("vérifié à l'API") {
                return Err(Rejection::new(
                    "D2",
                    "ancre",
                    &truncate_line(line.trim(), 120),
                    "le merge de la PR #30 est affirmé sans ancre — ni SHA complet du merge, ni vérification à l'API : un fait sans ancre, affirmé depuis un récit, n'est pas un Discover",
                ));
            }
        }
        if line.contains("F1-2 CLOSE") {
            let has_sha = hex_runs(line).iter().any(|(_, l)| *l == 40);
            if !has_sha {
                return Err(Rejection::new(
                    "D2",
                    "ancre",
                    &truncate_line(line.trim(), 120),
                    "le merge de la PR #26 est affirmé sans SHA complet — un fait sans ancre n'est pas un Discover",
                ));
            }
        }
    }
    // (c) Aucun fait affirmé depuis un récit dans les §0/§2 (les §1, §3,
    // §6 parlent du récit pour l'interdire ou le décrire — ils ne
    // l'affirment pas comme source).
    for n in [0u32, 2u32] {
        let sec = section_of(text, n);
        let marker = "récit de l'exécutant";
        let mut from = 0usize;
        while let Some(rel) = sec[from..].find(marker) {
            let idx = from + rel;
            let start = floor_boundary(sec, idx.saturating_sub(60));
            let before = &sec[start..idx];
            if !before.contains("non ") && !before.contains("jamais") {
                let line = sec.lines().find(|l| l.contains(marker)).unwrap_or("");
                return Err(Rejection::new(
                    "D2",
                    "ancre",
                    &truncate_line(line.trim(), 120),
                    "fait affirmé depuis le récit de l'exécutant — un Discover qui affirme sans vérifier n'est pas un Discover, c'est un récit",
                ));
            }
            from = idx + marker.len();
        }
    }
    Ok(checked)
}

// ---------------------------------------------------------------------------
// D3 — Mesure zéro nommée et datée
// ---------------------------------------------------------------------------

fn check_d3(text: &str, resolver: &dyn ShaResolver) -> Result<(), Rejection> {
    let s0 = section_of(text, 0);
    if !s0.contains("2026-11-12") || !s0.contains("lignes") {
        return Err(Rejection::new(
            "D3",
            "mesure zéro",
            "§0 sans date ni compte",
            "le §0 doit porter des comptes re-mesurés à l'instantané du Discover, avec leur date",
        ));
    }
    let head = match text.find("Master HEAD") {
        Some(i) => i,
        None => {
            return Err(Rejection::new(
                "D3",
                "mesure zéro",
                "Master HEAD absent",
                "le §0 doit porter le Master HEAD à l'instantané du Discover",
            ))
        }
    };
    let window_end = floor_boundary(text, (head + 400).min(text.len()));
    let window = &text[head..window_end];
    let sha = hex_runs(window)
        .into_iter()
        .find(|(_, l)| *l == 40)
        .map(|(s, _)| s);
    match sha {
        Some(s) if resolver.resolves(&s) => Ok(()),
        Some(s) => Err(Rejection::new(
            "D3",
            "sha",
            &s,
            "le Master HEAD cité ne résout pas",
        )),
        None => Err(Rejection::new(
            "D3",
            "mesure zéro",
            "Master HEAD sans SHA complet",
            "le Master HEAD doit être cité à sa forme complète (40 hex)",
        )),
    }
}

// ---------------------------------------------------------------------------
// D6 — Corrections portées en avant
// ---------------------------------------------------------------------------

fn check_d6(text: &str) -> Result<(), Rejection> {
    // La correction déclarée au §2 (compte BYB F1-2 v2 : le registre porte
    // 14 214 o, écart de 146 o porté en avant) doit y figurer avec sa
    // valeur d'origine et son écart — une réécriture silencieuse l'efface.
    let s2 = section_of(text, 2);
    if !s2.contains("14 214 o") || !s2.contains("146 o") {
        return Err(Rejection::new(
            "D6",
            "correction",
            "compte BYB F1-2 v2 sans note datée",
            "la correction du compte BYB F1-2 v2 (14 214 o, écart de 146 o) doit être portée en avant au §2 — une réécriture silencieuse n'est pas un Discover",
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// D8 — Limites nommées
// ---------------------------------------------------------------------------

fn check_d8(text: &str) -> Result<(), Rejection> {
    if !text.contains("Ce que ce Discover ne prouve pas") {
        return Err(Rejection::new(
            "D8",
            "limites",
            "absent",
            "le Discover doit nommer ce qu'il ne prouve pas",
        ));
    }
    if !text.contains("À trancher au design") {
        return Err(Rejection::new(
            "D8",
            "questions",
            "absent",
            "le Discover doit nommer les questions qu'il laisse au design",
        ));
    }
    Ok(())
}
