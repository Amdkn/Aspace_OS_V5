//! `take-action` — interface en ligne de commande de la fonction Action
//! (D-N055 F1-9). Sous-commande :
//!
//! * `check --case <t1|t2|t3|t4|fautif|f-a1|f-a2|f-a3|f-a4>`
//!   `--dossier <ACTION-F1-9.md>`
//!   `--journal <journal-router.jsonl> --design <design F1-9>`
//!   `[--fautif <ACTION-FAUTIF-1.md>] [--planted-rule <A2|A3|A6>]`
//!   `[--pr <n>] [--now <iso>]`
//!   — rendu d'un acte (A1–A8, ordre A1 → A4 → A2 → A3 → A6 → A7 →
//!   A5 → A8) ; sort 0 si l'acte est ACCEPTÉ ou NON POSÉ (absence
//!   consignée, A7), 2 si REJETÉ (raison nommée). La règle attendue du
//!   rejet du fautif est A2 par défaut (F-A1, F-A2), A3 pour F-A3, A6
//!   pour F-A4 — surchargeable par `--planted-rule`.
//!
//! Lectures au fichier local, nommées, comptées et tracées (A-F1-9-5) :
//! le dossier d'action (bloc du cas), le journal-router (seq contigus,
//! événements par dispatch_id — le journal fait foi pour
//! `judgment_rendered`, `merge_executed` et le routage), le design signé
//! (la signature « SIGNÉ » y est vérifiée), et le dossier fautif quand
//! il est donné. La PR est injectée par l'opérateur (`--pr`, numéro
//! vérifié à l'API ; 0 = aucune PR ouverte pour ce pas) — la CLI ne fait
//! aucun appel réseau, aucun appel en écriture d'état (O3 conservée).
//!
//! La CLI consigne la commande exacte, ses paramètres, son horodatage et
//! sa sortie dans le dossier d'action (section `## Rendus CLI`, A7).

use r10_validator::action::{parse_case, validate_action, ActionOutcome, PlantedFautif};
use r10_validator::{format_iso_utc, now_unix, parse_iso8601_offset, parse_json, Json};
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: take-action check --case <t1|t2|t3|t4|fautif|f-a1|f-a2|f-a3|f-a4> --dossier <ACTION-F1-9.md> --journal <journal-router.jsonl> --design <DESIGN-FONDATION-13-1-F1-9-PROJET.md> [--fautif <ACTION-FAUTIF-N.md>] [--planted-rule <A2|A3|A6>] [--pr <n>] [--now <iso>]".to_string()
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

/// Faits du journal pour un dispatch : jugement rendu, merge exécuté,
/// routage complet (typé + relayé + accusé). Le journal fait foi : le
/// dossier affirme, le journal prouve.
///
/// Le jugement est rendu sous le dispatch du juge (`D-N055-<pas>-JUDGE`,
/// patron seq 47 F1-8), pas sous le dispatch de l'acte — le CLI cherche
/// donc le `judgment_rendered` sous `judge_dispatch_id`, et le
/// `merge_executed` / le routage sous `dispatch_id`.
struct JournalFacts {
    lines: usize,
    max_seq: usize,
    judgment_rendered: bool,
    merge_executed: bool,
    dispatch_routed: bool,
}

fn read_journal(
    text: &str,
    path: &str,
    dispatch_id: &str,
    judge_dispatch_id: &str,
) -> Result<JournalFacts, String> {
    let mut max_seq = 0usize;
    let mut seen: Vec<usize> = Vec::new();
    let mut judgment_rendered = false;
    let mut merge_executed = false;
    let mut typed = false;
    let mut relayed = false;
    let mut ack = false;
    for (n, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let json = parse_json(line)
            .map_err(|e| format!("journal {} ligne {} : JSON invalide ({})", path, n + 1, e))?;
        let seq = match json.get("seq") {
            Some(Json::Num(s)) => s
                .parse::<usize>()
                .map_err(|_| format!("journal {} ligne {} : seq non numérique", path, n + 1))?,
            _ => return Err(format!("journal {} ligne {} : seq absent", path, n + 1)),
        };
        seen.push(seq);
        if seq > max_seq {
            max_seq = seq;
        }
        let typ = json.get("type").and_then(|v| v.as_str()).unwrap_or("");
        let did = json
            .get("dispatch_id")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        if did == judge_dispatch_id && typ == "judgment_rendered" {
            judgment_rendered = true;
        }
        if did == dispatch_id {
            match typ {
                "merge_executed" => merge_executed = true,
                "dispatch_typed" => typed = true,
                "dispatch_relayed" => relayed = true,
                "dispatch_ack" => ack = true,
                _ => {}
            }
        }
    }
    seen.sort_unstable();
    for (i, seq) in seen.iter().enumerate() {
        if *seq != i + 1 {
            return Err(format!(
                "journal {} : seq non contigus — seq {} attendu à la ligne {}, trouvé {}",
                path,
                i + 1,
                i + 1,
                seq
            ));
        }
    }
    Ok(JournalFacts {
        lines: seen.len(),
        max_seq,
        judgment_rendered,
        merge_executed,
        dispatch_routed: typed && relayed && ack,
    })
}

fn main() -> ExitCode {
    let argv: Vec<String> = std::env::args().collect();
    let args: Vec<String> = argv.iter().skip(1).cloned().collect();
    if args.is_empty() || args[0] != "check" {
        eprintln!("{}", usage());
        return ExitCode::from(2);
    }
    let rest = &args[1..];
    let case_name = match arg_value(rest, "--case") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let dossier_path = match arg_value(rest, "--dossier") {
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
    let design_path = match arg_value(rest, "--design") {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{} — {}", usage(), e);
            return ExitCode::from(2);
        }
    };
    let fautif_path = arg_value(rest, "--fautif").ok();
    let pr: usize = arg_value(rest, "--pr")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(0);
    let now_iso = arg_value(rest, "--now").ok();
    let now_epoch = match &now_iso {
        Some(s) => match parse_iso8601_offset(s) {
            Some(epoch) => epoch,
            None => {
                eprintln!("--now invalide (ISO 8601 avec offset attendu) : {}", s);
                return ExitCode::from(2);
            }
        },
        None => now_unix(),
    };
    let now_text = match &now_iso {
        Some(s) => s.clone(),
        None => format_iso_utc(now_epoch),
    };

    let heading = match case_name.as_str() {
        "t1" => "T1",
        "t2" => "T2",
        "t3" => "T3",
        "t4" => "T4",
        "fautif" | "f-a1" => "F-A1",
        "f-a2" => "F-A2",
        "f-a3" => "F-A3",
        "f-a4" => "F-A4",
        other => {
            eprintln!("cas inconnu : {} — attendu t1|t2|t3|t4|fautif|f-a1|f-a2|f-a3|f-a4", other);
            return ExitCode::from(2);
        }
    };
    // Règle attendue du rejet du fautif : A2 par défaut, A3 pour F-A3,
    // A6 pour F-A4 — surchargeable par --planted-rule (A2/A3/A6).
    let planted_rule: &'static str = match arg_value(rest, "--planted-rule").as_deref() {
        Ok("A3") => "A3",
        Ok("A6") => "A6",
        Ok(_) => "A2",
        Err(_) => match case_name.as_str() {
            "f-a3" => "A3",
            "f-a4" => "A6",
            _ => "A2",
        },
    };

    // Lecture 1 : le dossier d'action (ou le dossier fautif).
    let (case_text, case_source) = match &fautif_path {
        Some(path) => match read_file(path, "du dossier fautif") {
            Ok(t) => (t, path.clone()),
            Err(e) => {
                eprintln!("{}", e);
                return ExitCode::from(2);
            }
        },
        None => match read_file(&dossier_path, "du dossier d'action") {
            Ok(t) => (t, dossier_path.clone()),
            Err(e) => {
                eprintln!("{}", e);
                return ExitCode::from(2);
            }
        },
    };
    let mut data = match parse_case(&case_text, heading) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("parse du bloc {} dans {} : {}", heading, case_source, e);
            return ExitCode::from(2);
        }
    };

    // Lecture 2 : le journal-router — il fait foi pour les événements.
    let journal_text = match read_file(&journal_path, "du journal-router") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let judge_dispatch_id = format!("D-N055-{}-JUDGE", data.step);
    let facts = match read_journal(
        &journal_text,
        &journal_path,
        &data.dispatch_id,
        &judge_dispatch_id,
    ) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    // Le journal prime sur le dossier pour les faits d'événement.
    data.judgment_rendered = facts.judgment_rendered;
    match case_name.as_str() {
        "t1" => data.act_posed = facts.merge_executed,
        "t3" => data.act_posed = facts.dispatch_routed,
        "t4" => data.act_posed = pr > 0,
        _ => {}
    }

    // Lecture 3 : le design signé — la signature y est vérifiée.
    let design_text = match read_file(&design_path, "du design signé") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    data.design_signed = design_text.contains("SIGNÉ");

    let planted = fautif_path.as_ref().map(|_| PlantedFautif {
        dispatch_id: &data.dispatch_id,
        expected_rule: planted_rule,
    });
    let case = data.as_case(planted);

    let outcome = validate_action(&case, now_epoch);
    let exact_command = argv.join(" ");
    let (line, code) = match &outcome {
        Ok(ActionOutcome::Accepted(valid)) => (
            format!(
                "ACCEPTÉ — Action {} ({}) : {} — A1–A8 passés, 0 question posée — rapport : {}",
                heading, valid.dispatch_id, valid.act, valid.report
            ),
            ExitCode::SUCCESS,
        ),
        Ok(ActionOutcome::NotPosed { reason }) => (
            format!(
                "NON POSÉE — Action {} ({}) : {} — {}",
                heading, case.dispatch_id, case.act, reason
            ),
            ExitCode::SUCCESS,
        ),
        Err(rejection) => (
            format!("{}", rejection),
            ExitCode::from(2),
        ),
    };
    println!("{}", line);
    println!(
        "lectures : dossier {} (bloc {}) ; journal {} ({} lignes, seq 1–{} contigus ; jugement rendu pour {} : {} ; merge exécuté pour {} : {} ; routage complet pour {} : {}) ; design {} (SIGNÉ : {}) ; PR injectée : {}",
        case_source,
        heading,
        journal_path,
        facts.lines,
        facts.max_seq,
        judge_dispatch_id,
        facts.judgment_rendered,
        case.dispatch_id,
        facts.merge_executed,
        case.dispatch_id,
        facts.dispatch_routed,
        design_path,
        data.design_signed,
        if pr == 0 {
            "aucune".to_string()
        } else {
            format!("#{}", pr)
        },
    );

    // Consignation (A7, A-F1-9-5) : commande exacte, paramètres,
    // horodatage et sortie, dans le dossier d'action.
    let render_line = format!(
        "- {} — `{}` → {}",
        now_text, exact_command, line
    );
    let dossier_text = match read_file(&dossier_path, "du dossier d'action") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let mut out = dossier_text;
    if !out.ends_with('\n') {
        out.push('\n');
    }
    if !out.contains("## Rendus CLI") {
        out.push_str("\n## Rendus CLI\n\n");
    }
    out.push_str(&render_line);
    out.push('\n');
    if let Err(e) = fs::write(&dossier_path, out) {
        eprintln!("consignation dans {} : {}", dossier_path, e);
        return ExitCode::from(2);
    }
    println!("consigné dans {} (section ## Rendus CLI)", dossier_path);
    code
}
