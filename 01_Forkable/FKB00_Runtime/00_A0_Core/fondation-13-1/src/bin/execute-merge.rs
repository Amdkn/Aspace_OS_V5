//! `execute-merge` — interface en ligne de commande de la fonction
//! Exécuter (D-N055 F1-6). Sous-commande :
//!
//! * `check --execution <fichier.md> --shas <shas.txt> --head <sha40>`
//!   `--ci <ci.txt> --mergeable <true|false> --mergeable-state <clean|…>`
//!   `--method <merge> [--pre-merge] [--merge-commit <sha40>`
//!   `--parent1 <sha40> --parent2 <sha40> --merged <true|false>`
//!   `--merged-at <iso> --master <sha40> --open-prs <n>]`
//!   — contrôle d'un dossier d'exécution (E1–E8, ordre E1 → E8 → E2 →
//!   E4 → E3 → E5 → E6 → E7) ; sort 0 si l'exécution est acceptée, 2 si
//!   rejetée (raison nommée). Sans `--pre-merge`, le contrôle est complet
//!   (E1–E8, preuves post-merge exigées) ; avec `--pre-merge`, seuls
//!   E1, E8, E2, E4, E3, E5 sont contrôlés — E6/E7 ne sont pas encore
//!   applicables, elles sont vérifiées après l'appel.
//!
//! Preuves injectées (patron F1-4/F1-5 : le code ne contacte ni git ni
//! l'API, l'opérateur les vérifie aux outils déterministes et les injecte) :
//! * `shas.txt` : un SHA complet (40 hex) par ligne — les SHA qui
//!   résolvent, vérifiés par l'opérateur à l'API.
//! * `--head` : la tête vérifiée à l'API immédiatement avant l'appel
//!   (40 hex).
//! * `ci.txt` : un check-run par ligne, `nom: conclusion` — les
//!   check-runs re-vérifiés à l'API sur la tête (ex. `CodeQL: success`).
//! * `--mergeable` / `--mergeable-state` : `mergeable` et
//!   `mergeable_state` lus à l'API immédiatement avant l'appel.
//! * `--method` : la méthode de l'appel (`merge`).
//! * `--merge-commit`, `--parent1`, `--parent2`, `--merged`,
//!   `--merged-at`, `--master`, `--open-prs` : preuves post-merge,
//!   re-vérifiées à l'API par un tiers après l'appel (E7).
//!
//! L'appel de merge lui-même (`gh pr merge --merge`, ou
//! `POST /pulls/{n}/merge`, méthode `merge`) est effectué par l'opérateur
//! sur instruction du dossier validé en pré-merge, et consigné dans le
//! dossier (E6) — la CLI, std seul sans dépendance, ne fait pas d'HTTPS.
//!
//! Zéro appel sortant : la CLI ne lit que des fichiers locaux et n'écrit
//! que sur stdout/stderr.

use r10_validator::execute::{validate_execution, ExecutionEvidence, Stage};
use r10_validator::StaticShaResolver;
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: execute-merge check --execution <fichier.md> --shas <shas.txt> --head <sha40> --ci <ci.txt> --mergeable <true|false> --mergeable-state <clean|...> --method <merge> [--pre-merge] [--merge-commit <sha40> --parent1 <sha40> --parent2 <sha40> --merged <true|false> --merged-at <iso> --master <sha40> --open-prs <n>]".to_string()
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

fn has_flag(args: &[String], name: &str) -> bool {
    args.iter().any(|a| a == name)
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

fn parse_bool(s: &str) -> Result<bool, String> {
    match s {
        "true" => Ok(true),
        "false" => Ok(false),
        other => Err(format!(
            "booléen attendu (true|false), reçu '{}'",
            other
        )),
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() || args[0] != "check" {
        eprintln!("{}", usage());
        return ExitCode::from(2);
    }
    let rest = &args[1..];
    let execution_path = match arg_value(rest, "--execution") {
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
    let mergeable = match arg_value(rest, "--mergeable").and_then(|v| parse_bool(&v)) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let mergeable_state = match arg_value(rest, "--mergeable-state") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let method = match arg_value(rest, "--method") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let pre_merge = has_flag(rest, "--pre-merge");
    // Preuves post-merge (exigées sauf en pré-merge).
    let merge_commit = arg_value(rest, "--merge-commit").ok();
    let parent1 = arg_value(rest, "--parent1").ok();
    let parent2 = arg_value(rest, "--parent2").ok();
    let merged = arg_value(rest, "--merged")
        .and_then(|v| parse_bool(&v))
        .unwrap_or(false);
    let merged_at = arg_value(rest, "--merged-at").unwrap_or_default();
    let master = arg_value(rest, "--master").ok();
    let open_prs = arg_value(rest, "--open-prs")
        .and_then(|v| v.parse::<usize>().map_err(|_| "open-prs doit être un entier".to_string()))
        .ok();
    if !pre_merge
        && (merge_commit.is_none()
            || parent1.is_none()
            || parent2.is_none()
            || master.is_none()
            || open_prs.is_none())
    {
        eprintln!(
            "{} — contrôle complet (E1–E8) : --merge-commit, --parent1, --parent2, --master et --open-prs sont exigés (ou --pre-merge pour le contrôle E1–E5 avant l'appel)",
            usage()
        );
        return ExitCode::from(2);
    }

    let text = match read_file(&execution_path, "du dossier d'exécution") {
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

    let stage = if pre_merge {
        Stage::PreMerge
    } else {
        Stage::PostMerge
    };
    let evidence = ExecutionEvidence {
        head: &head,
        resolver: &resolver,
        ci: &ci_refs,
        mergeable,
        mergeable_state: &mergeable_state,
        method: &method,
        excluded: &[],
        stage,
        merge_commit: merge_commit.as_deref(),
        merged,
        merged_at: &merged_at,
        parent1: parent1.as_deref(),
        parent2: parent2.as_deref(),
        master_head: master.as_deref(),
        open_prs,
    };

    match validate_execution(&text, &evidence) {
        Ok(valid) => {
            if pre_merge {
                println!(
                    "ACCEPTÉ (pré-merge) — Exécution PR #{} : méthode {} — E1, E8, E2, E4, E3, E5 passés (tête {}) ; E6/E7 à vérifier après l'appel",
                    valid.pr, valid.method, valid.head
                );
            } else {
                println!(
                    "ACCEPTÉ — Exécution PR #{} : méthode {} — E1–E8 passés (tête {}, merge commit {})",
                    valid.pr,
                    valid.method,
                    valid.head,
                    valid.merge_commit.unwrap_or_default()
                );
            }
            ExitCode::SUCCESS
        }
        Err(rejection) => {
            eprintln!("{}", rejection);
            ExitCode::from(2)
        }
    }
}
