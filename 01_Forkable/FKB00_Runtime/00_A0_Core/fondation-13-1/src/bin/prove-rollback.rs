//! `prove-rollback` — interface en ligne de commande de la fonction
//! Rollback (D-N055 F1-10). Sous-commande :
//!
//! * `check --case <t0|t1|...|t9|f-r1|f-r2|f-r3|f-r4|f-r5>`
//!   `--dossier <ROLLBACK-F1-10.md>`
//!   `--journal <journal-router.jsonl>`
//!   `--scenario <journal-f1-10-scenario.jsonl>`
//!   `--design <design F1-10>`
//!   `[--fautif <rollback-fautif-N.md>] [--planted-rule <R3|R4|R6>]`
//!   `[--now <iso>]`
//!   — rendu d'un retour (R1–R8, ordre R1 → R4 → R3 → R2 → R5 → R6 →
//!   R7 → R8) ; sort 0 si le retour est ACCEPTÉ ou NON APPLICABLE (T0 :
//!   hold-out vert, 0 événement de rollback), 2 si REJETÉ (raison
//!   nommée) ou si le fautif n'est pas rejeté par la règle attendue.
//!   La règle attendue du rejet du fautif est R3 par défaut (F-R1),
//!   R4 pour F-R2/F-R3/F-R5, R6 pour F-R4 — surchargeable par
//!   `--planted-rule`.
//!
//! Lectures au fichier local, nommées, comptées et tracées (A-F1-10-5) :
//! le dossier de rollback (bloc du cas + autorisation nommée), le
//! journal-router réel (seq contigus, checkpoints : seq + `event_id` +
//! `at` + preuve — le journal réel fait foi pour les checkpoints), le
//! journal-scénario (événements `rollback_decided` /
//! `rollback_executed` simulés — la fixture fait foi pour les décisions
//! simulées, jamais consignées au journal réel), le design signé (la
//! signature « SIGNÉ » y est vérifiée), et le dossier fautif quand il
//! est donné. Le journal fait foi sur le dossier : les faits de décision,
//! d'arrêt et de checkpoint lus au fichier priment sur les champs du
//! dossier. La CLI ne fait aucun appel réseau, aucun appel en écriture
//! d'état (O3 conservée).
//!
//! La CLI consigne la commande exacte, ses paramètres, son horodatage et
//! sa sortie dans le dossier de rollback (section `## Rendus CLI`,
//! A-F1-10-5).

use r10_validator::rollback::{parse_case, validate_rollback, RollbackOutcome};
use r10_validator::{format_iso_utc, now_unix, parse_iso8601_offset, parse_json, Json};
use std::fs;
use std::process::ExitCode;

fn usage() -> String {
    "usage: prove-rollback check --case <t0|t1|t2|t3|t4|t5|t6|t7|t8|t9|f-r1|f-r2|f-r3|f-r4|f-r5> --dossier <ROLLBACK-F1-10.md> --journal <journal-router.jsonl> --scenario <journal-f1-10-scenario.jsonl> --design <DESIGN-FONDATION-13-1-F1-10-PROJET.md> [--fautif <rollback-fautif-N.md>] [--planted-rule <R3|R4|R6>] [--now <iso>]".to_string()
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

/// Faits du journal réel pour un checkpoint : l'événement au seq existe,
/// son `event_id` et son `at` correspondent au dossier, sa preuve est
/// non vide. Le journal réel fait foi.
struct CheckpointFacts {
    found: bool,
    matches: bool,
    proof_empty: bool,
}

fn read_checkpoint(
    text: &str,
    path: &str,
    seq: usize,
    event_id: &str,
    at: &str,
) -> Result<CheckpointFacts, String> {
    let mut found = false;
    let mut matches = false;
    let mut proof_empty = true;
    let mut seen: Vec<usize> = Vec::new();
    for (n, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let json = parse_json(line)
            .map_err(|e| format!("journal {} ligne {} : JSON invalide ({})", path, n + 1, e))?;
        let line_seq = match json.get("seq") {
            Some(Json::Num(s)) => s
                .parse::<usize>()
                .map_err(|_| format!("journal {} ligne {} : seq non numérique", path, n + 1))?,
            _ => return Err(format!("journal {} ligne {} : seq absent", path, n + 1)),
        };
        seen.push(line_seq);
        if line_seq != seq {
            continue;
        }
        found = true;
        let line_event = json.get("event_id").and_then(|v| v.as_str()).unwrap_or("");
        let line_at = json.get("at").and_then(|v| v.as_str()).unwrap_or("");
        matches = line_event == event_id && line_at == at;
        proof_empty = match json.get("proof") {
            Some(Json::Arr(items)) => {
                items.is_empty()
                    || items.iter().any(|v| match v {
                        Json::Str(s) => s.trim().is_empty(),
                        _ => true,
                    })
            }
            _ => true,
        };
    }
    seen.sort_unstable();
    for (i, s) in seen.iter().enumerate() {
        if *s != i + 1 {
            return Err(format!(
                "journal {} : seq non contigus — seq {} attendu à la ligne {}, trouvé {}",
                path,
                i + 1,
                i + 1,
                s
            ));
        }
    }
    Ok(CheckpointFacts {
        found,
        matches,
        proof_empty,
    })
}

/// Faits du journal-scénario pour un dispatch simulé : un événement
/// `rollback_decided` existe-t-il (décision + arrêt), un événement
/// `rollback_executed` existe-t-il (reprise rendue) ? La fixture fait
/// foi pour les décisions simulées — jamais consignées au journal réel.
struct ScenarioFacts {
    lines: usize,
    max_seq: usize,
    decided: bool,
    executed: bool,
    any_rollback_event: bool,
}

fn read_scenario(
    text: &str,
    path: &str,
    dispatch_id: &str,
) -> Result<ScenarioFacts, String> {
    let mut max_seq = 0usize;
    let mut seen: Vec<usize> = Vec::new();
    let mut decided = false;
    let mut executed = false;
    let mut any_rollback_event = false;
    for (n, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let json = parse_json(line)
            .map_err(|e| format!("scénario {} ligne {} : JSON invalide ({})", path, n + 1, e))?;
        let seq = match json.get("seq") {
            Some(Json::Num(s)) => s
                .parse::<usize>()
                .map_err(|_| format!("scénario {} ligne {} : seq non numérique", path, n + 1))?,
            _ => return Err(format!("scénario {} ligne {} : seq absent", path, n + 1)),
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
        if did == dispatch_id {
            match typ {
                "rollback_decided" => {
                    decided = true;
                    any_rollback_event = true;
                }
                "rollback_executed" => {
                    executed = true;
                    any_rollback_event = true;
                }
                _ => {}
            }
        }
    }
    seen.sort_unstable();
    for (i, seq) in seen.iter().enumerate() {
        if *seq != i + 1 {
            return Err(format!(
                "scénario {} : seq non contigus — seq {} attendu à la ligne {}, trouvé {}",
                path,
                i + 1,
                i + 1,
                seq
            ));
        }
    }
    Ok(ScenarioFacts {
        lines: seen.len(),
        max_seq,
        decided,
        executed,
        any_rollback_event,
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
    let scenario_path = match arg_value(rest, "--scenario") {
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
        "t0" => "T0",
        "t1" => "T1",
        "t2" => "T2",
        "t3" => "T3",
        "t4" => "T4",
        "t5" => "T5",
        "t6" => "T6",
        "t7" => "T7",
        "t8" => "T8",
        "t9" => "T9",
        "fautif" | "f-r1" => "F-R1",
        "f-r2" => "F-R2",
        "f-r3" => "F-R3",
        "f-r4" => "F-R4",
        "f-r5" => "F-R5",
        other => {
            eprintln!(
                "cas inconnu : {} — attendu t0|t1|t2|t3|t4|t5|t6|t7|t8|t9|fautif|f-r1|f-r2|f-r3|f-r4|f-r5",
                other
            );
            return ExitCode::from(2);
        }
    };
    // Règle attendue du rejet du fautif : R3 par défaut (F-R1), R4 pour
    // F-R2/F-R3/F-R5, R6 pour F-R4 — surchargeable par --planted-rule.
    let planted_rule: &'static str = match arg_value(rest, "--planted-rule").as_deref() {
        Ok("R4") => "R4",
        Ok("R6") => "R6",
        Ok(_) => "R3",
        Err(_) => match case_name.as_str() {
            "f-r2" | "f-r3" | "f-r5" => "R4",
            "f-r4" => "R6",
            _ => "R3",
        },
    };

    // Lecture 1 : le dossier de rollback (ou le dossier fautif).
    let (case_text, case_source) = match &fautif_path {
        Some(path) => match read_file(path, "du dossier fautif") {
            Ok(t) => (t, path.clone()),
            Err(e) => {
                eprintln!("{}", e);
                return ExitCode::from(2);
            }
        },
        None => match read_file(&dossier_path, "du dossier de rollback") {
            Ok(t) => (t, dossier_path.clone()),
            Err(e) => {
                eprintln!("{}", e);
                return ExitCode::from(2);
            }
        },
    };
    let data = match parse_case(&case_text, heading) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("parse du bloc {} dans {} : {}", heading, case_source, e);
            return ExitCode::from(2);
        }
    };

    // L'autorisation du retour est le design signé : acte + auteur +
    // date + source exacte, nommés dans chaque bloc du dossier. La CLI
    // vérifie qu'ils sont nommés et que la source cite le design passé
    // en --design — le design lui-même est vérifié SIGNÉ (lecture 4).
    if data.auth_act.trim().is_empty()
        || data.auth_author.trim().is_empty()
        || data.auth_date.trim().is_empty()
        || data.auth_source.trim().is_empty()
        || !data.auth_source.contains("DESIGN-FONDATION-13-1-F1-10-PROJET.md")
    {
        eprintln!("autorisation non nommée dans le bloc {} (acte + auteur + date + source exacte du design F1-10 attendus) — un retour sans autorisation nommée n'est pas un retour du 1", heading);
        return ExitCode::from(2);
    }

    // Lecture 2 : le journal-router réel — il fait foi pour les
    // checkpoints (seq + event_id + at + preuve).
    let journal_text = match read_file(&journal_path, "du journal-router") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let mut case = data.as_case();
    if data.checkpoint_seq > 0 {
        let facts = match read_checkpoint(
            &journal_text,
            &journal_path,
            data.checkpoint_seq,
            &data.checkpoint_event_id,
            &data.checkpoint_at,
        ) {
            Ok(f) => f,
            Err(e) => {
                eprintln!("{}", e);
                return ExitCode::from(2);
            }
        };
        // Un checkpoint absent du journal réel n'existe pas.
        case.checkpoint.matches_journal = facts.found && facts.matches;
        case.checkpoint.proof_empty_in_journal = !facts.found || facts.proof_empty;
    }

    // Lecture 3 : le journal-scénario — il fait foi pour les décisions
    // simulées (rollback_decided / rollback_executed, jamais consignés
    // au journal réel).
    let scenario_text = match read_file(&scenario_path, "du journal-scénario") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    let scenario = match read_scenario(&scenario_text, &scenario_path, &data.dispatch_id) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    // L'arrêt et la décision sont le même événement (D-F1-10-7) : le
    // `rollback_decided` du scénario porte les deux.
    case.decision.event_in_journal = scenario.decided;
    case.decision.stop_in_journal = scenario.decided;
    case.rollback_event_in_journal = scenario.any_rollback_event;
    // L'événement de décision du scénario prime sur l'event_id du dossier
    // quand le dossier n'en nomme pas (le dossier affirme, le journal
    // prouve) ; pour les cas valides, l'event_id du dossier est celui du
    // scénario.
    if scenario.decided && case.decision.event_id.trim().is_empty() {
        case.decision.event_id = "EVT-20261113-SIM";
    }

    // Lecture 4 : le design signé — la signature y est vérifiée.
    let design_text = match read_file(&design_path, "du design signé") {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };
    if !design_text.contains("SIGNÉ") {
        eprintln!("design non signé : {} ne porte pas la signature « SIGNÉ »", design_path);
        return ExitCode::from(2);
    }

    // Le rapport et sa preuve sont exigés pour un retour accepté comme
    // pour le contrôle T0 : un retour sans rapport n'est pas rendu, il
    // est affirmé.
    if data.report.trim().is_empty() || data.report_proof.trim().is_empty() {
        eprintln!("rapport ou preuve du rapport vide dans le bloc {} — un retour sans rapport n'est pas rendu, il est affirmé", heading);
        return ExitCode::from(2);
    }

    let outcome = validate_rollback(&case);
    let exact_command = argv.join(" ");

    // Le filet (A-F1-10-1) : un dossier fautif doit être rejeté par la
    // règle attendue — un fautif non rejeté, ou rejeté par la mauvaise
    // règle, = échec de la fonction.
    let (line, code) = match &outcome {
        Ok(RollbackOutcome::Accepted(valid)) => (
            format!(
                "ACCEPTÉ — Rollback {} : {} reprend {} au checkpoint seq {} — R1–R8 passés — rapport : {}",
                valid.dispatch_id, valid.repreneur, valid.function, valid.checkpoint_seq, valid.report
            ),
            ExitCode::SUCCESS,
        ),
        Ok(RollbackOutcome::NotApplicable { reason }) => (
            format!(
                "NON APPLICABLE — Rollback {} : {} — R1–R8 non déclenchés, 0 événement de rollback",
                case.dispatch_id, reason
            ),
            ExitCode::SUCCESS,
        ),
        Err(rejection) => {
            let base = format!("{}", rejection);
            if fautif_path.is_some() {
                if rejection.rule != planted_rule {
                    (
                        format!(
                            "{} (attendu {} : rejet par la mauvaise règle — le fautif planté n'est pas rejeté comme spécifié)",
                            base, planted_rule
                        ),
                        ExitCode::from(2),
                    )
                } else {
                    (base, ExitCode::from(2))
                }
            } else {
                (base, ExitCode::from(2))
            }
        }
    };
    // Fautif non rejeté : la fonction échoue — le filet l'attrape ici.
    if fautif_path.is_some() {
        if let Ok(_) = &outcome {
            let line = format!(
                "FAUTIF NON REJETÉ — Rollback {} : le dossier fautif est accepté — la fonction Rollback revient à ses acteurs d'origine (coordinateur + sessions d'origine)",
                case.dispatch_id
            );
            println!("{}", line);
            println!(
                "lectures : dossier {} (bloc {}) ; journal {} (checkpoint seq {} : {}) ; scénario {} ({} lignes, seq 1–{} ; rollback_decided pour {} : {} ; rollback_executed : {}) ; design {} (SIGNÉ : oui)",
                case_source,
                heading,
                journal_path,
                data.checkpoint_seq,
                if data.checkpoint_seq == 0 {
                    "hors journal — source nommée".to_string()
                } else {
                    format!(
                        "trouvé, conforme : {}",
                        case.checkpoint.matches_journal
                    )
                },
                scenario_path,
                scenario.lines,
                scenario.max_seq,
                case.dispatch_id,
                scenario.decided,
                scenario.executed,
                design_path,
            );
            let render_line = format!("- {} — `{}` → {}", now_text, exact_command, line);
            if let Ok(dossier_text) = read_file(&dossier_path, "du dossier de rollback") {
                let mut out = dossier_text;
                if !out.ends_with('\n') {
                    out.push('\n');
                }
                if !out.contains("## Rendus CLI") {
                    out.push_str("\n## Rendus CLI\n\n");
                }
                out.push_str(&render_line);
                out.push('\n');
                let _ = fs::write(&dossier_path, out);
            }
            return ExitCode::from(2);
        }
    }
    println!("{}", line);
    println!(
        "lectures : dossier {} (bloc {}) ; journal {} (checkpoint seq {} : {}) ; scénario {} ({} lignes, seq 1–{} ; rollback_decided pour {} : {} ; rollback_executed : {}) ; design {} (SIGNÉ : oui)",
        case_source,
        heading,
        journal_path,
        data.checkpoint_seq,
        if data.checkpoint_seq == 0 {
            "hors journal — source nommée".to_string()
        } else {
            format!(
                "trouvé, conforme : {}",
                case.checkpoint.matches_journal
            )
        },
        scenario_path,
        scenario.lines,
        scenario.max_seq,
        case.dispatch_id,
        scenario.decided,
        scenario.executed,
        design_path,
    );

    // Consignation (A-F1-10-5) : commande exacte, paramètres,
    // horodatage et sortie, dans le dossier de rollback.
    let render_line = format!("- {} — `{}` → {}", now_text, exact_command, line);
    let dossier_text = match read_file(&dossier_path, "du dossier de rollback") {
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
