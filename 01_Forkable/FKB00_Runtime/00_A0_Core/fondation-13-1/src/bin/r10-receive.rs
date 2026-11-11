//! `r10-receive` — interface en ligne de commande de la fonction Recevoir
//! (D-N055 F1-2). Deux sous-commandes :
//!
//! * `validate --deposit <fichier.json> --ledger <ledger.json> --shas <shas.txt>`
//!   — valide le dépôt, sort 0 si accepté, 2 si rejeté (raison nommée).
//! * `consign --deposit <fichier.json> --ledger <ledger.json> --shas <shas.txt>`
//!   — valide puis émet le reçu JSON sur stdout, `recorded_at` posé à la
//!   consignation depuis l'horloge système (jamais repris du dépôt).
//!
//! `ledger.json` : `{"entry_ids": [...], "mission_ids": [...]}` — union des
//! branches `work-dn*-ledger` (le store unique).
//! `shas.txt` : un SHA complet (40 hex) par ligne — les SHA qui résolvent.
//!
//! Zéro appel sortant : la résolution du SHA est lue dans `shas.txt`,
//! fournie par l'opérateur (vérification au git local ou à l'API).

use r10_validator::{consign, now_unix, parse_json, validate, Ledger, StaticShaResolver};
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: r10-receive (validate|consign) --deposit <fichier.json> --ledger <ledger.json> --shas <shas.txt>".to_string()
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
    if args.is_empty() || (args[0] != "validate" && args[0] != "consign") {
        eprintln!("{}", usage());
        return ExitCode::from(2);
    }
    let cmd = args[0].clone();
    let rest = &args[1..];
    let deposit_path = match arg_value(rest, "--deposit") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let ledger_path = match arg_value(rest, "--ledger") {
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

    let deposit_text = match fs::read_to_string(&deposit_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("lecture du dépôt {} : {}", deposit_path, e);
            return ExitCode::from(2);
        }
    };
    let deposit = match parse_json(&deposit_text) {
        Ok(j) => j,
        Err(e) => {
            eprintln!("REJET V1 — dépôt : JSON invalide : {}", e);
            return ExitCode::from(2);
        }
    };
    let ledger_text = match fs::read_to_string(&ledger_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("lecture du ledger {} : {}", ledger_path, e);
            return ExitCode::from(2);
        }
    };
    let ledger = match Ledger::from_json(&ledger_text) {
        Ok(l) => l,
        Err(e) => {
            eprintln!("ledger invalide : {}", e);
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

    let now = now_unix();
    match cmd.as_str() {
        "validate" => match validate(&deposit, &ledger, &resolver, now) {
            Ok(valid) => {
                println!(
                    "ACCEPTÉ — entry_id {} mission_id {} sha {}",
                    valid.entry_id, valid.mission_id, valid.sha
                );
                ExitCode::SUCCESS
            }
            Err(rejection) => {
                eprintln!("{}", rejection);
                ExitCode::from(2)
            }
        },
        "consign" => match consign(&deposit, &ledger, &resolver, now) {
            Ok(receipt) => {
                println!("{}", receipt);
                ExitCode::SUCCESS
            }
            Err(rejection) => {
                eprintln!("{}", rejection);
                ExitCode::from(2)
            }
        },
        _ => unreachable!(),
    }
}
