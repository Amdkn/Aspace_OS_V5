//! `validate-discover` — interface en ligne de commande de la fonction
//! Découvrir (D-N055 F1-4). Sous-commande :
//!
//! * `check --discover <fichier.md> --shas <shas.txt>`
//!   — contrôle de recevabilité d'un fichier Discover (D1–D8, ordre
//!   D1 → D4 → D5 → D7 → D2 → D3 → D6 → D8) ; sort 0 si accepté, 2 si
//!   rejeté (raison nommée).
//!
//! `shas.txt` : un SHA complet (40 hex) par ligne — les SHA qui résolvent,
//! vérifiés par l'opérateur à l'API (même frontière que `r10-receive` :
//! la résolution est injectée, le code ne contacte ni le git local ni
//! l'API). Zéro appel sortant : la CLI ne lit que des fichiers locaux et
//! n'écrit que sur stdout/stderr.

use r10_validator::discover::validate_discover;
use r10_validator::StaticShaResolver;
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: validate-discover check --discover <fichier.md> --shas <shas.txt>".to_string()
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

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() || args[0] != "check" {
        eprintln!("{}", usage());
        return ExitCode::from(2);
    }
    let rest = &args[1..];
    let discover_path = match arg_value(rest, "--discover") {
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

    let text = match fs::read_to_string(&discover_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("lecture du Discover {} : {}", discover_path, e);
            return ExitCode::from(2);
        }
    };
    let shas_text = match fs::read_to_string(&shas_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("lecture des SHA {} : {}", shas_path, e);
            return ExitCode::from(2);
        }
    };
    let resolver = StaticShaResolver::new(
        shas_text
            .lines()
            .map(|l| l.trim().to_string())
            .filter(|l| !l.is_empty()),
    );

    match validate_discover(&text, &resolver) {
        Ok(valid) => {
            println!(
                "ACCEPTÉ — Discover {} : D1–D8 passés ({} SHA complets vérifiés)",
                valid.mission, valid.shas_checked
            );
            ExitCode::SUCCESS
        }
        Err(rejection) => {
            eprintln!("{}", rejection);
            ExitCode::from(2)
        }
    }
}
