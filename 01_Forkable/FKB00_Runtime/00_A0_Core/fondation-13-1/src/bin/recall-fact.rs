//! `recall-fact` — interface en ligne de commande de la fonction
//! Mémoriser (D-N055 F1-7). Sous-commande :
//!
//! * `check --citation <dossier.md> --source <chemin> --line <n>`
//!   `[--corroboration <chemin:ligne:date> ...]`
//!   `[--fautif <dossier-fautif.md>]`
//!   — citation d'un fait (M1–M8, ordre M1 → M7 → M2 → M3 → M4 → M5 →
//!   M6 → M8) ; sort 0 si la citation est acceptée, 2 si rejetée
//!   (règle nommée). La citation rendue EST l'acte (D-F1-7-7).
//!
//! La CLI est la lectrice (A-F1-7-5) : elle re-compile l'index (elle
//! lit le dossier de citation), re-lit la source au fichier à la ligne
//! nommée, re-lit chaque corroboration à sa ligne, et lit le dossier
//! fautif quand il est donné. Lectures au fichier local nommées,
//! comptées et tracées (1 source + N corroborations + 1 fautif) ; 0
//! appel réseau, 0 recherche sémantique — la recherche sémantique n'est
//! pas le mécanisme, elle reste un outil d'exploration du producteur.
//!
//! Preuves injectées par l'opérateur (patron F1-5/F1-6 : le code ne
//! contacte ni git ni l'API, l'opérateur vérifie aux outils
//! déterministes et injecte) :
//! * `--source` / `--line` : le chemin exact et la ligne relue au
//!   fichier au moment de la citation (la date de la source est la date
//!   citée quand la ligne la porte, sinon les dates que la ligne porte
//!   sont nommées sans en choisir une, ou la date du fichier pour une
//!   note quotidienne).
//! * `--corroboration <chemin:ligne:date>` : une source corroborante
//!   relue à sa ligne ; `date` est la date du fait dans cette source,
//!   vérifiée par l'opérateur au fichier (la CLI vérifie que la date
//!   apparaît dans la ligne relue).
//! * `--fautif` : le dossier du fait fautif planté (F-X1) — la CLI en
//!   extrait (énoncé, source, date) et l'injecte comme référence M6.
//!
//! La CLI consigne la commande exacte, ses paramètres, son horodatage
//! (UTC, horloge système — comme `recorded_at` du validateur R10) et sa
//! sortie (les 4 champs cités) sur stdout — l'opérateur les verse dans
//! le dossier de citation du pas.
//!
//! Zéro appel sortant : la CLI ne lit que des fichiers locaux et n'écrit
//! que sur stdout/stderr.

use r10_validator::memory::{validate_citation, CitationEvidence, STATUSES};
use r10_validator::{format_iso_utc, now_unix};
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: recall-fact check --citation <dossier.md> --source <chemin> --line <n> [--corroboration <chemin:ligne:date> ...] [--fautif <dossier-fautif.md>]".to_string()
}

fn arg_value(args: &[String], name: &str) -> Result<String, String> {
    let mut i = 0;
    while i < args.len() {
        if args[i] == name && i + 1 < args.len() {
            return Ok(args[i + 1].clone());
        }
        i += 1;
    }
    Err(format!("argument manquant : {}", name))
}

fn arg_values(args: &[String], name: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut i = 0;
    while i < args.len() {
        if args[i] == name && i + 1 < args.len() {
            out.push(args[i + 1].clone());
            i += 2;
        } else {
            i += 1;
        }
    }
    out
}

fn read_file(path: &str, what: &str) -> Result<String, String> {
    fs::read_to_string(path).map_err(|e| format!("lecture de {} {} : {}", what, path, e))
}

/// La section `## ...` dont le titre contient `keyword`.
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

/// Le champ `**Nom :** valeur` dans une section.
fn field_in<'a>(section: &'a str, marker: &str) -> Option<&'a str> {
    for line in section.lines() {
        if let Some(rest) = line.strip_prefix(marker) {
            return Some(rest.trim());
        }
    }
    None
}

/// Les 4 champs de la section Citation d'un dossier (fautif inclus).
fn citation_fields(text: &str) -> Result<(String, String, String, String), String> {
    let section = section_named(text, "Citation");
    if section.is_empty() {
        return Err("section « Citation » absente du dossier".to_string());
    }
    let get = |m: &str| {
        field_in(section, m)
            .map(|s| s.to_string())
            .ok_or_else(|| format!("champ {m} manquant dans la section Citation"))
    };
    Ok((
        get("**Énoncé :**")?,
        get("**Source :**")?,
        get("**Date :**")?,
        get("**Statut :**")?,
    ))
}

/// Les dates `AAAA-MM-JJ` d'une ligne, dans l'ordre (fenêtres de 10
/// caractères — jamais de découpage au milieu d'un caractère UTF-8).
fn all_dates(line: &str) -> Vec<String> {
    let chars: Vec<char> = line.chars().collect();
    let mut out = Vec::new();
    for w in chars.windows(10) {
        let s: String = w.iter().collect();
        let b = s.as_bytes();
        if b[4] == b'-'
            && b[7] == b'-'
            && b[..4].iter().all(|c| c.is_ascii_digit())
            && b[5..7].iter().all(|c| c.is_ascii_digit())
            && b[8..10].iter().all(|c| c.is_ascii_digit())
        {
            out.push(s);
        }
    }
    out
}

/// La première date `AAAA-MM-JJ` d'une ligne, quand elle en porte une.
fn first_date(line: &str) -> Option<String> {
    all_dates(line).into_iter().next()
}

/// La date d'un fichier de note quotidienne (`AAAA-MM-JJ.md`), sinon
/// « inconnue ».
fn file_date(path: &str) -> String {
    let name = path.rsplit('/').next().unwrap_or(path);
    if name.len() >= 13 && name.ends_with(".md") {
        let stem = &name[..name.len() - 3];
        if first_date(stem).as_deref() == Some(stem) {
            return stem.to_string();
        }
    }
    "inconnue".to_string()
}

/// La ligne `n` (1-based) d'un texte, ou une erreur nommée.
fn line_at(text: &str, n: usize, path: &str) -> Result<String, String> {
    text.lines()
        .nth(n - 1)
        .map(|s| s.to_string())
        .ok_or_else(|| format!("ligne {} absente de {}", n, path))
}

/// Le statut d'une corroboration, lu dans la ligne de la section
/// Corroborations qui nomme sa source (le premier des six statuts
/// trouvés sur la ligne, sinon « vérifié » — le module ne compare que
/// les dates, M5).
fn corroboration_status(section: &str, source: &str) -> String {
    for line in section.lines() {
        if line.contains(source) {
            for status in STATUSES {
                if line.contains(status) {
                    return status.to_string();
                }
            }
        }
    }
    "vérifié".to_string()
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.first().map(|s| s.as_str()) != Some("check") {
        eprintln!("{}", usage());
        return ExitCode::from(1);
    }
    let rest = &args[1..];
    let citation_path = match arg_value(rest, "--citation") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}\n{}", usage());
            return ExitCode::from(1);
        }
    };
    let source_path = match arg_value(rest, "--source") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}\n{}", usage());
            return ExitCode::from(1);
        }
    };
    let line_n: usize = match arg_value(rest, "--line") {
        Ok(v) => match v.parse() {
            Ok(n) if n >= 1 => n,
            _ => {
                eprintln!("--line attend un entier >= 1, reçu '{}'\n{}", v, usage());
                return ExitCode::from(1);
            }
        },
        Err(e) => {
            eprintln!("{e}\n{}", usage());
            return ExitCode::from(1);
        }
    };
    let corroboration_args = arg_values(rest, "--corroboration");
    let fautif_path = arg_value(rest, "--fautif").ok();

    let citation = match read_file(&citation_path, "dossier de citation") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{e}");
            return ExitCode::from(1);
        }
    };

    // La date citée (lue dans le dossier) sert à dériver la date de la
    // source : la ligne porte la date du fait quand elle la contient ;
    // sinon la CLI nomme les dates que la ligne porte, sans en choisir
    // une — choisir la première serait inférer (M3 interdit l'inférence).
    let cited_date = citation_fields(&citation)
        .map(|(_, _, d, _)| d)
        .unwrap_or_default();

    // 1 lecture au fichier : la source, relue à sa ligne.
    let mut reads = 1usize;
    let (source_exists, source_line, source_date) = match fs::read_to_string(&source_path) {
        Ok(text) => {
            let line = match line_at(&text, line_n, &source_path) {
                Ok(l) => l,
                Err(e) => {
                    eprintln!("{e}");
                    return ExitCode::from(1);
                }
            };
            let date = if !cited_date.is_empty() && line.contains(&cited_date) {
                cited_date.clone()
            } else {
                let dates = all_dates(&line);
                if dates.is_empty() {
                    file_date(&source_path)
                } else {
                    dates.join(", ")
                }
            };
            (true, line, date)
        }
        Err(_) => (false, String::new(), "inconnue".to_string()),
    };

    // N lectures au fichier : les corroborations, relues à leur ligne.
    let mut corroborations: Vec<(String, String, String)> = Vec::new();
    let corr_section = section_named(&citation, "Corroborations et contradictions");
    for spec in &corroboration_args {
        let parts: Vec<&str> = spec.splitn(3, ':').collect();
        if parts.len() != 3 {
            eprintln!(
                "--corroboration attend <chemin:ligne:date>, reçu '{}'\n{}",
                spec,
                usage()
            );
            return ExitCode::from(1);
        }
        let (path, line_s, date) = (parts[0], parts[1], parts[2]);
        let line_n: usize = match line_s.parse() {
            Ok(n) if n >= 1 => n,
            _ => {
                eprintln!("--corroboration : ligne invalide '{}'\n{}", line_s, usage());
                return ExitCode::from(1);
            }
        };
        let text = match read_file(path, "corroboration") {
            Ok(t) => t,
            Err(e) => {
                eprintln!("{e}");
                return ExitCode::from(1);
            }
        };
        reads += 1;
        let line = match line_at(&text, line_n, path) {
            Ok(l) => l,
            Err(e) => {
                eprintln!("{e}");
                return ExitCode::from(1);
            }
        };
        if !line.contains(date) {
            eprintln!(
                "REJET M5 — corroboration {} : la date {} n'est pas celle que porte la ligne {} relue",
                path, date, line_n
            );
            return ExitCode::from(2);
        }
        let status = corroboration_status(corr_section, path);
        corroborations.push((path.to_string(), date.to_string(), status));
    }
    let corr_refs: Vec<(&str, &str, &str)> = corroborations
        .iter()
        .map(|(s, d, st)| (s.as_str(), d.as_str(), st.as_str()))
        .collect();

    // 1 lecture au fichier : le dossier fautif, quand il est donné.
    let mut fautif_owned: Option<(String, String, String)> = None;
    if let Some(path) = &fautif_path {
        let text = match read_file(path, "dossier fautif") {
            Ok(t) => t,
            Err(e) => {
                eprintln!("{e}");
                return ExitCode::from(1);
            }
        };
        reads += 1;
        match citation_fields(&text) {
            Ok((stmt, src, date, _)) => {
                fautif_owned = Some((stmt, src, date));
            }
            Err(e) => {
                eprintln!("dossier fautif {} : {}", path, e);
                return ExitCode::from(1);
            }
        }
    }
    let planted = fautif_owned
        .as_ref()
        .map(|(s, src, d)| (s.as_str(), src.as_str(), d.as_str()));

    let evidence = CitationEvidence {
        source_exists,
        source_line_text: &source_line,
        source_date: &source_date,
        corroborations: &corr_refs,
        planted_fautif: planted,
    };

    let command = format!(
        "recall-fact check --citation {} --source {} --line {}{}",
        citation_path,
        source_path,
        line_n,
        {
            let mut s = String::new();
            for c in &corroboration_args {
                s.push_str(&format!(" --corroboration {}", c));
            }
            if let Some(p) = &fautif_path {
                s.push_str(&format!(" --fautif {}", p));
            }
            s
        }
    );
    let at = format_iso_utc(now_unix());

    match validate_citation(&citation, &evidence) {
        Ok(valid) => {
            println!("ACCEPTÉ — Citation : M1–M8 passés");
            println!("  Énoncé : {}", valid.statement);
            println!("  Source : {}", valid.source);
            println!("  Date : {}", valid.date);
            println!("  Statut : {}", valid.status);
            println!(
                "  Re-lecture : {} ligne {} ({} lecture(s) au fichier, 0 appel réseau, 0 recherche sémantique)",
                source_path, line_n, reads
            );
            println!("  Commande : {}", command);
            println!("  Horodatage : {}", at);
            ExitCode::from(0)
        }
        Err(rejection) => {
            println!("{}", rejection);
            println!("  Commande : {}", command);
            println!("  Horodatage : {}", at);
            println!(
                "  Re-lecture : {} ligne {} ({} lecture(s) au fichier, 0 appel réseau, 0 recherche sémantique)",
                source_path, line_n, reads
            );
            ExitCode::from(2)
        }
    }
}
