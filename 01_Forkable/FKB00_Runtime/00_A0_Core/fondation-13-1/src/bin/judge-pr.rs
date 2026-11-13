//! `judge-pr` — interface en ligne de commande de la fonction Juger
//! (D-N055 F1-5). Sous-commande :
//!
//! * `check --judgment <fichier.md> --shas <shas.txt> --head <sha40>`
//!   `--ci <ci.txt> --suite <suite.txt> [--planted-rule J2]`
//!   — jugement d'une PR (J1–J8, ordre J1 → J7 → J2 → J5 → J3 → J4 →
//!   J6 → J8) ; sort 0 si le jugement est accepté, 2 si rejeté (raison
//!   nommée).
//!
//! Preuves injectées (patron F1-4 : le code ne contacte ni git ni l'API,
//! l'opérateur les vérifie aux outils déterministes et les injecte) :
//! * `shas.txt` : un SHA complet (40 hex) par ligne — les SHA qui
//!   résolvent, vérifiés par l'opérateur à l'API.
//! * `--head` : la tête vérifiée à l'API au moment du jugement (40 hex).
//! * `ci.txt` : un check-run par ligne, `nom: conclusion` — les
//!   check-runs re-vérifiés à l'API sur la tête (ex. `CodeQL: success`).
//! * `suite.txt` : la suite re-courue par le juge — lignes `passed: N`,
//!   `failed: N`, `failed_names: a, b` (noms des tests en échec) et
//!   `excluded: a, b` (liste exacte d'exclusion du coordinateur, si rouge
//!   exclu — P-F1-5-4).
//!
//! Zéro appel sortant : la CLI ne lit que des fichiers locaux et n'écrit
//! que sur stdout/stderr.

use r10_validator::judge::{validate_judgment, JudgmentEvidence};
use r10_validator::StaticShaResolver;
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: judge-pr check --judgment <fichier.md> --shas <shas.txt> --head <sha40> --ci <ci.txt> --suite <suite.txt> [--planted-rule J2]".to_string()
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

fn read_file(path: &str, what: &str) -> Result<String, String> {
    fs::read_to_string(path).map_err(|e| format!("lecture de {} {} : {}", what, path, e))
}

/// Lignes `nom: conclusion` — un check-run par ligne.
fn parse_ci(text: &str) -> Vec<(String, String)> {
    let mut out = Vec::new();
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        if let Some((name, conclusion)) = line.split_once(':') {
            out.push((name.trim().to_string(), conclusion.trim().to_string()));
        }
    }
    out
}

/// Lignes `passed: N`, `failed: N`, `failed_names: a, b`, `excluded: a, b`.
fn parse_suite(text: &str) -> (usize, usize, Vec<String>, Vec<String>) {
    let mut passed = 0usize;
    let mut failed = 0usize;
    let mut failed_names: Vec<String> = Vec::new();
    let mut excluded: Vec<String> = Vec::new();
    for line in text.lines() {
        let line = line.trim();
        if let Some(v) = line.strip_prefix("passed:") {
            passed = v.trim().parse().unwrap_or(0);
        } else if let Some(v) = line.strip_prefix("failed:") {
            failed = v.trim().parse().unwrap_or(0);
        } else if let Some(v) = line.strip_prefix("failed_names:") {
            failed_names = v
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect();
        } else if let Some(v) = line.strip_prefix("excluded:") {
            excluded = v
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect();
        }
    }
    (passed, failed, failed_names, excluded)
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() || args[0] != "check" {
        eprintln!("{}", usage());
        return ExitCode::from(2);
    }
    let rest = &args[1..];
    let judgment_path = match arg_value(rest, "--judgment") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let shas_path = match arg_value(rest, "--shas") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let head = match arg_value(rest, "--head") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let ci_path = match arg_value(rest, "--ci") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let suite_path = match arg_value(rest, "--suite") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let planted_rule = arg_value(rest, "--planted-rule").unwrap_or_else(|_| "J2".to_string());

    let text = match read_file(&judgment_path, "du jugement") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let shas_text = match read_file(&shas_path, "des SHA") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let ci_text = match read_file(&ci_path, "de la CI") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let suite_text = match read_file(&suite_path, "de la suite") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };

    let resolver = StaticShaResolver::new(
        shas_text
            .lines()
            .map(|l| l.trim().to_string())
            .filter(|l| !l.is_empty()),
    );
    let ci = parse_ci(&ci_text);
    let ci_refs: Vec<(&str, &str)> = ci
        .iter()
        .map(|(n, c)| (n.as_str(), c.as_str()))
        .collect();
    let (suite_passed, suite_failed, failed_names, excluded) = parse_suite(&suite_text);
    let failed_refs: Vec<&str> = failed_names.iter().map(|s| s.as_str()).collect();
    let excluded_refs: Vec<&str> = excluded.iter().map(|s| s.as_str()).collect();

    let evidence = JudgmentEvidence {
        head: &head,
        resolver: &resolver,
        ci: &ci_refs,
        suite_passed,
        suite_failed,
        suite_failed_names: &failed_refs,
        excluded: &excluded_refs,
        planted_fault_rule: &planted_rule,
    };

    match validate_judgment(&text, &evidence) {
        Ok(valid) => {
            println!(
                "ACCEPTÉ — Jugement PR #{} : {} — J1–J8 passés ({} SHA complets vérifiés, tête {})",
                valid.pr, valid.verdict, valid.shas_checked, valid.head
            );
            ExitCode::SUCCESS
        }
        Err(rejection) => {
            eprintln!("{}", rejection);
            ExitCode::from(2)
        }
    }
}
