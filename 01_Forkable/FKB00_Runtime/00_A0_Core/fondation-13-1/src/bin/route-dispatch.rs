//! `route-dispatch` — interface en ligne de commande de la fonction Router
//! (D-N055 F1-3). Sous-commandes :
//!
//! * `validate --dispatch <fichier.json> --journal <journal.jsonl> --designs <designs.txt>`
//!   — valide le dispatch sans inscrire (sort 0 si accepté, 2 si rejeté).
//! * `type --dispatch <fichier.json> --journal <journal.jsonl> --designs <designs.txt>`
//!   — valide puis inscrit l'événement au journal (append-only, `seq` =
//!   numéro de ligne) et l'émet sur stdout. `relay`, `ack`, `pulse`,
//!   `request-judgment`, `render-judgment` font de même pour leur type
//!   d'événement (le type est vérifié contre celui de la sous-commande).
//!
//! `designs.txt` : un design signé par ligne (la référence exacte telle
//! qu'elle apparaît dans `design_ref`).
//! `journal.jsonl` : créé s'il n'existe pas.
//!
//! Zéro appel sortant : la liste des designs signés est lue dans
//! `designs.txt`, fournie par l'opérateur (vérification au fichier).

use r10_validator::router::{
    inscribe, now_iso, validate_dispatch, Journal, StaticDesignResolver,
};
use r10_validator::{now_unix, parse_json};
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: route-dispatch (validate|type|relay|ack|pulse|request-judgment|render-judgment) --dispatch <fichier.json> --journal <journal.jsonl> --designs <designs.txt>".to_string()
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

fn expected_type(cmd: &str) -> Option<&'static str> {
    match cmd {
        "type" => Some("dispatch_typed"),
        "relay" => Some("dispatch_relayed"),
        "ack" => Some("dispatch_ack"),
        "pulse" => Some("pulse"),
        "request-judgment" => Some("judgment_requested"),
        "render-judgment" => Some("judgment_rendered"),
        _ => None,
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let cmds = [
        "validate",
        "type",
        "relay",
        "ack",
        "pulse",
        "request-judgment",
        "render-judgment",
    ];
    if args.is_empty() || !cmds.contains(&args[0].as_str()) {
        eprintln!("{}", usage());
        return ExitCode::from(2);
    }
    let cmd = args[0].clone();
    let rest = &args[1..];
    let dispatch_path = match arg_value(rest, "--dispatch") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let journal_path = match arg_value(rest, "--journal") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let designs_path = match arg_value(rest, "--designs") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };

    let dispatch_text = match fs::read_to_string(&dispatch_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("lecture du dispatch {} : {}", dispatch_path, e);
            return ExitCode::from(2);
        }
    };
    let dispatch = match parse_json(&dispatch_text) {
        Ok(j) => j,
        Err(e) => {
            eprintln!("REJET R1 — dispatch : JSON invalide : {}", e);
            return ExitCode::from(2);
        }
    };
    let journal_text = match fs::read_to_string(&journal_path) {
        Ok(t) => t,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => String::new(),
        Err(e) => {
            eprintln!("lecture du journal {} : {}", journal_path, e);
            return ExitCode::from(2);
        }
    };
    let journal = match Journal::from_jsonl(&journal_text) {
        Ok(j) => j,
        Err(e) => {
            eprintln!("journal invalide : {}", e);
            return ExitCode::from(2);
        }
    };
    let designs_text = match fs::read_to_string(&designs_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("lecture des designs {} : {}", designs_path, e);
            return ExitCode::from(2);
        }
    };
    let designs = StaticDesignResolver::new(
        designs_text
            .lines()
            .map(|l| l.trim().to_string())
            .filter(|l| !l.is_empty()),
    );

    // Le type de l'événement est vérifié contre la sous-commande (sauf
    // `validate`, qui accepte tout type valide).
    if let Some(expected) = expected_type(&cmd) {
        match dispatch.get("type").and_then(|v| v.as_str()) {
            Some(t) if t == expected => {}
            Some(t) => {
                eprintln!(
                    "REJET R8 — champ 'type', valeur reçue '{}' : la sous-commande '{}' attend '{}'",
                    t, cmd, expected
                );
                return ExitCode::from(2);
            }
            None => {
                eprintln!("REJET R1 — champ 'type' : la sous-commande '{}' attend '{}'", cmd, expected);
                return ExitCode::from(2);
            }
        }
    }

    let now = now_unix();
    match cmd.as_str() {
        "validate" => match validate_dispatch(&dispatch, &journal, &designs, now) {
            Ok(valid) => {
                println!(
                    "ACCEPTÉ — event_id {} type {} dispatch_id {} (seq suivant {}, at {})",
                    valid.event_id,
                    valid.typ,
                    valid.dispatch_id,
                    journal.next_seq(),
                    now_iso()
                );
                ExitCode::SUCCESS
            }
            Err(rejection) => {
                eprintln!("{}", rejection);
                ExitCode::from(2)
            }
        },
        _ => match inscribe(&dispatch, &journal, &designs, now) {
            Ok(line) => {
                let mut out = journal_text;
                if !out.is_empty() && !out.ends_with('\n') {
                    out.push('\n');
                }
                out.push_str(&line);
                out.push('\n');
                if let Err(e) = fs::write(&journal_path, out) {
                    eprintln!("écriture du journal {} : {}", journal_path, e);
                    return ExitCode::from(2);
                }
                println!("{}", line);
                ExitCode::SUCCESS
            }
            Err(rejection) => {
                eprintln!("{}", rejection);
                ExitCode::from(2)
            }
        },
    }
}
