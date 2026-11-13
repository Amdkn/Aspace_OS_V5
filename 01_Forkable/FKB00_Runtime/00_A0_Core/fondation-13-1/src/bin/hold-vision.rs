//! `hold-vision` — interface en ligne de commande de la fonction
//! Vision (D-N055 F1-8). Sous-commande :
//!
//! * `check --case <t1|t2|t3> --registre <chemin> --journal <chemin>`
//!   `--l00 <chemin> --n2 <chemin> --miroir <chemin> --fiche <chemin>`
//!   `--manifeste <chemin> --workgraph-state <chemin>`
//!   `--inventaire <chemin> --ledger-dir <dossier> --master <sha40>`
//!   `--master-read-at <iso> --open-prs <n> --open-prs-read-at <iso>`
//!   `[--fautif <VISION-FAUTIF-1.md>]`
//!   — rendu d'un état de vision (V1–V8, ordre V1 → V6 → V2 → V3 → V4 →
//!   V7 → V5 → V8) ; sort 0 si l'état est accepté, 2 si rejeté (règle
//!   nommée). Avec `--fautif`, l'état rendu est le fait fautif planté
//!   F-V1 (seuil D-N053 sur l'ancre journal 938) : le rejet attendu est
//!   V3 (sortie 2) ; tout autre sort (acceptation, ou rejet par une autre
//!   règle) est un échec du hold-out (sortie 3).
//!
//! La CLI est la lectrice (A-F1-8-5) : elle re-lit chaque registre au
//! fichier local nommé (R1–R9, calendriers C1–C5), normalise les fuseaux
//! (D-F1-8-11) et consigne la commande exacte, ses paramètres, son
//! horodatage et sa sortie (l'état de vision rendu) sur stdout —
//! l'opérateur les verse dans le dossier de vision du pas. Lectures au
//! fichier local nommées, comptées et tracées ; 0 appel réseau, 0
//! recherche sémantique.
//!
//! Preuves injectées par l'opérateur (patron F1-5/F1-6 : le code ne
//! contacte ni git ni l'API, l'opérateur vérifie aux outils
//! déterministes et injecte) :
//! * `--master` / `--master-read-at` : le HEAD master vérifié à l'API
//!   au moment du rendu, avec son horodatage de lecture.
//! * `--open-prs` / `--open-prs-read-at` : le nombre de PR ouvertes
//!   vérifié à l'API au moment du rendu, avec son horodatage de lecture.
//! * La lecture de la Google Sheet Workgraph n'est pas relue en direct
//!   (0 appel réseau) : elle est citée du Discover F1-8 §2.5, avec son
//!   horodatage de lecture (2026-11-13T02:13:32-05:00) — une re-citation
//!   datée, pas une lecture fraîche (limite nommée, V8).
//!
//! Zéro appel sortant : la CLI ne lit que des fichiers locaux et n'écrit
//! que sur stdout/stderr.

use r10_validator::vision::{
    normalize_timestamp, parse_fautif, threshold_after, validate_vision, Comparison,
    DatedReading, Divergence, Outcome, PlantedFautif, Threshold, VisionState,
};
use r10_validator::{format_iso_utc, now_unix, parse_iso8601_offset, parse_json};
use std::fs;
use std::process::ExitCode;
use std::time::UNIX_EPOCH;

fn usage() -> String {
    "usage: hold-vision check --case <t1|t2|t3> --registre <chemin> --journal <chemin> --l00 <chemin> --n2 <chemin> --miroir <chemin> --fiche <chemin> --manifeste <chemin> --workgraph-state <chemin> --inventaire <chemin> --ledger-dir <dossier> --master <sha40> --master-read-at <iso> --open-prs <n> --open-prs-read-at <iso> [--fautif <VISION-FAUTIF-1.md>]".to_string()
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

/// Ligne `n` (1-based) d'un texte, ou une erreur nommée.
fn line_at(text: &str, n: usize, path: &str) -> Result<String, String> {
    text.lines()
        .nth(n - 1)
        .map(|s| s.to_string())
        .ok_or_else(|| format!("ligne {} absente de {}", n, path))
}

/// Première ligne contenant `needle`, ou une erreur nommée.
fn find_line(text: &str, needle: &str, what: &str) -> Result<String, String> {
    text.lines()
        .find(|l| l.contains(needle))
        .map(|s| s.to_string())
        .ok_or_else(|| format!("{} introuvable (recherche « {} »)", what, needle))
}

/// L'horodatage de modification d'un fichier, en ISO 8601 UTC avec offset.
fn mtime_iso(path: &str) -> Result<String, String> {
    let meta = fs::metadata(path).map_err(|e| format!("métadonnées de {} : {}", path, e))?;
    let modified = meta
        .modified()
        .map_err(|e| format!("mtime de {} : {}", path, e))?;
    let secs = modified
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0);
    Ok(format_iso_utc(secs))
}

/// Les dates `AAAA-MM-JJ` d'une ligne, dans l'ordre.
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

/// L'heure d'ancre d'une ligne de registre (« ~01:52 EST », « ~21:00
/// EST ») en ISO 8601 avec offset (-05:00), ou `None`.
fn anchor_time(line: &str) -> Option<String> {
    let date = all_dates(line).into_iter().next()?;
    let tilde = line.find('~')?;
    let rest = &line[tilde + 1..];
    let time: String = rest.chars().take(5).collect();
    let b = time.as_bytes();
    if b.len() != 5 || b[2] != b':' || !b[..2].iter().all(|c| c.is_ascii_digit())
        || !b[3..5].iter().all(|c| c.is_ascii_digit())
    {
        return None;
    }
    let iso = format!("{}T{}:00-05:00", date, time);
    if parse_iso8601_offset(&iso).is_some() {
        Some(iso)
    } else {
        None
    }
}

/// Le premier horodatage mural « AAAA-MM-JJ HH:MM EDT|EST » d'une ligne.
fn first_wall_time(line: &str) -> Option<String> {
    let chars: Vec<char> = line.chars().collect();
    for w in chars.windows(20) {
        let s: String = w.iter().collect();
        let b = s.as_bytes();
        if b.len() == 20
            && b[4] == b'-'
            && b[7] == b'-'
            && b[10] == b' '
            && b[13] == b':'
            && (s.ends_with(" EDT") || s.ends_with(" EST"))
        {
            return Some(s);
        }
    }
    None
}

/// Les acteurs (première cellule) des lignes de table d'un fichier.
fn table_actors(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    for line in text.lines() {
        if let Some(rest) = line.strip_prefix("| ") {
            if let Some(first) = rest.split('|').next() {
                let actor = first.trim().to_string();
                if !actor.is_empty() && actor != "Qui" && !actor.starts_with('-') {
                    out.push(actor);
                }
            }
        }
    }
    out
}

/// Vérifie la contiguïté des seq d'un JSONL (l'inventaire : seq =
/// numéro de ligne, sans event_id). Retourne le nombre de lignes.
fn check_seq_contiguous(text: &str, path: &str) -> Result<usize, String> {
    let mut lines = 0usize;
    for (i, line) in text.lines().enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let json = parse_json(line)
            .map_err(|e| format!("ligne {} de {} : JSON invalide : {}", i + 1, path, e))?;
        let seq = match json.get("seq") {
            Some(r10_validator::Json::Num(n)) => n.parse::<usize>().unwrap_or(0),
            _ => 0,
        };
        if seq != i + 1 {
            return Err(format!(
                "{} : seq {} à la ligne {} — le seq est le numéro de ligne",
                path, seq, i + 1
            ));
        }
        lines += 1;
    }
    Ok(lines)
}

/// Vérifie un journal JSONL : seq = numéro de ligne, event_ids uniques.
/// Retourne (lignes, dernier seq, ligne du dernier événement).
fn check_journal(text: &str, path: &str) -> Result<(usize, usize, String), String> {
    let mut seen: Vec<String> = Vec::new();
    let mut lines = 0usize;
    let mut last = String::new();
    for (i, line) in text.lines().enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let json = parse_json(line)
            .map_err(|e| format!("ligne {} du journal {} : JSON invalide : {}", i + 1, path, e))?;
        let seq = match json.get("seq") {
            Some(r10_validator::Json::Num(n)) => n.parse::<usize>().unwrap_or(0),
            _ => 0,
        };
        if seq != i + 1 {
            return Err(format!(
                "journal {} : seq {} à la ligne {} — le seq est le numéro de ligne",
                path, seq, i + 1
            ));
        }
        let event_id = json
            .get("event_id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        if seen.contains(&event_id) {
            return Err(format!(
                "journal {} : event_id {} en double",
                path, event_id
            ));
        }
        seen.push(event_id);
        lines += 1;
        last = line.to_string();
    }
    Ok((lines, lines, last))
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.first().map(|s| s.as_str()) != Some("check") {
        eprintln!("{}", usage());
        return ExitCode::from(1);
    }
    let rest = &args[1..];
    let need = |name: &str| match arg_value(rest, name) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}\n{}", usage());
            std::process::exit(1);
        }
    };
    let case = need("--case");
    if !["t1", "t2", "t3"].contains(&case.as_str()) {
        eprintln!("--case attend t1, t2 ou t3, reçu '{}'\n{}", case, usage());
        return ExitCode::from(1);
    }
    let registre_path = need("--registre");
    let journal_path = need("--journal");
    let l00_path = need("--l00");
    let n2_path = need("--n2");
    let miroir_path = need("--miroir");
    let fiche_path = need("--fiche");
    let manifeste_path = need("--manifeste");
    let workgraph_state_path = need("--workgraph-state");
    let inventaire_path = need("--inventaire");
    let ledger_dir = need("--ledger-dir");
    let master = need("--master");
    let master_read_at = need("--master-read-at");
    let open_prs_s = need("--open-prs");
    let open_prs_read_at = need("--open-prs-read-at");
    let fautif_path = arg_value(rest, "--fautif").ok();

    let now = now_unix();
    let read_at_now = format_iso_utc(now);

    // Preuves injectées : vérifiées par l'opérateur avant l'appel.
    if master.len() != 40 || !master.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
    {
        eprintln!("--master attend un SHA complet (40 hex), reçu '{}'", master);
        return ExitCode::from(1);
    }
    if parse_iso8601_offset(&master_read_at).is_none() {
        eprintln!("--master-read-at attend un ISO 8601 avec offset, reçu '{}'", master_read_at);
        return ExitCode::from(1);
    }
    if parse_iso8601_offset(&open_prs_read_at).is_none() {
        eprintln!("--open-prs-read-at attend un ISO 8601 avec offset, reçu '{}'", open_prs_read_at);
        return ExitCode::from(1);
    }
    let open_prs: usize = match open_prs_s.parse() {
        Ok(n) => n,
        Err(_) => {
            eprintln!("--open-prs attend un entier, reçu '{}'", open_prs_s);
            return ExitCode::from(1);
        }
    };

    // 9 lectures au fichier local (R1–R9) + 2 lectures injectées + 1
    // lecture citée (Sheet, Discover F1-8 §2.5).
    let mut reads = 0usize;
    let load = |path: &str, what: &str| -> Result<(String, usize, String), String> {
        let text = read_file(path, what)?;
        let lines = text.lines().count();
        let mtime = mtime_iso(path)?;
        Ok((text, lines, mtime))
    };
    let fail = |e: String| -> ExitCode {
        eprintln!("{}", e);
        ExitCode::from(1)
    };
    let (registre, registre_lines, registre_mtime) = match load(&registre_path, "registre") {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    reads += 1;
    let (journal_text, journal_lines, journal_mtime) = match load(&journal_path, "journal") {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    reads += 1;
    let (l00, l00_lines, l00_mtime) = match load(&l00_path, "L00-ETAT") {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    reads += 1;
    let (n2, n2_lines, n2_mtime) = match load(&n2_path, "L00-N2-ETAT") {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    reads += 1;
    let (miroir, miroir_lines, miroir_mtime) = match load(&miroir_path, "miroir Workgraph") {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    reads += 1;
    let (fiche, fiche_lines, fiche_mtime) = match load(&fiche_path, "fiche") {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    reads += 1;
    let (manifeste, _, manifeste_mtime) =
        match load(&manifeste_path, "manifeste") {
            Ok(v) => v,
            Err(e) => return fail(e),
        };
    reads += 1;
    let (workgraph_state, _, workgraph_state_mtime) =
        match load(&workgraph_state_path, "workgraph-state.json") {
            Ok(v) => v,
            Err(e) => return fail(e),
        };
    reads += 1;
    let (inventaire, inventaire_lines, inventaire_mtime) =
        match load(&inventaire_path, "journal-inventaire") {
            Ok(v) => v,
            Err(e) => return fail(e),
        };
    reads += 1;

    // Le journal est la source : seq = ligne, event_ids uniques.
    let (journal_count, max_seq, last_journal_line) =
        match check_journal(&journal_text, &journal_path) {
            Ok(v) => v,
            Err(e) => return fail(e),
        };
    let _ = journal_lines;
    let last_journal = match parse_json(&last_journal_line) {
        Ok(j) => j,
        Err(e) => return fail(format!("dernier événement du journal : JSON invalide : {}", e)),
    };
    let last_seq_type = last_journal
        .get("type")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let last_seq_dispatch = last_journal
        .get("dispatch_id")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let last_seq_at = last_journal
        .get("at")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();

    // L'inventaire est un index : seq contigus.
    let inventaire_count = match check_seq_contiguous(&inventaire, &inventaire_path) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let _ = inventaire_lines;

    // Registre : lignes 938 (D-N055, F1-7 CLOSE) et 930 (D-N053, F2 CLOSE).
    let line_938 = match line_at(&registre, 938, &registre_path) {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    let line_930 = match line_at(&registre, 930, &registre_path) {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    for (line, dispatch, journal_no) in [
        (&line_938, "D-N055", 938),
        (&line_930, "D-N053", 930),
    ] {
        if !line.contains(dispatch) {
            return fail(format!(
                "registre ligne {} : ne nomme pas {} — l'ancre est fausse (ligne : {})",
                journal_no,
                dispatch,
                line.chars().take(120).collect::<String>()
            ));
        }
    }
    let anchor_d_n055 = match anchor_time(&line_938) {
        Some(t) => t,
        None => return fail("registre ligne 938 : heure d'ancre illisible".to_string()),
    };
    let anchor_d_n053 = match anchor_time(&line_930) {
        Some(t) => t,
        None => return fail("registre ligne 930 : heure d'ancre illisible".to_string()),
    };
    let threshold_d_n055 = match threshold_after(&anchor_d_n055) {
        Some(t) => t,
        None => return fail("seuil D-N055 incalculable".to_string()),
    };
    let threshold_d_n053 = match threshold_after(&anchor_d_n053) {
        Some(t) => t,
        None => return fail("seuil D-N053 incalculable".to_string()),
    };

    // Journal seq 37 : le merge F1-7.
    let seq37_line = match line_at(&journal_text, 37, &journal_path) {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    let seq37 = match parse_json(&seq37_line) {
        Ok(j) => j,
        Err(e) => return fail(format!("journal seq 37 : JSON invalide : {}", e)),
    };
    let seq37_ok = seq37
        .get("type")
        .and_then(|v| v.as_str())
        == Some("merge_executed")
        && seq37
            .get("dispatch_id")
            .and_then(|v| v.as_str())
            == Some("D-N055-F1-7-MERGE")
        && seq37.get("at").and_then(|v| v.as_str()) == Some("2026-11-13T01:47:15-05:00")
        && seq37
            .get("proof")
            .map(|p| p.to_compact().contains("055745b"))
            .unwrap_or(false);
    if !seq37_ok {
        return fail(
            "journal seq 37 : n'est pas le merge_executed F1-7 attendu (PR #50, 055745b, 01:47:15-05:00)"
                .to_string(),
        );
    }

    // Reçu G-20261112-035 (ledger local) : le merge F1-7.
    let recu_path = format!("{}/G-20261112-035.json", ledger_dir);
    let recu_text = match read_file(&recu_path, "reçu G-20261112-035") {
        Ok(t) => t,
        Err(e) => return fail(e),
    };
    reads += 1;
    let recu = match parse_json(&recu_text) {
        Ok(j) => j,
        Err(e) => return fail(format!("reçu G-20261112-035 : JSON invalide : {}", e)),
    };
    let recu_sha = recu
        .get("sha")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    if recu_sha != "055745b853495c38f0aaa0ae6c3d2adad9e89177" {
        return fail(format!(
            "reçu G-20261112-035 : sha {} — attendu 055745b853495c38f0aaa0ae6c3d2adad9e89177",
            recu_sha
        ));
    }
    let ledger_count = match fs::read_dir(&ledger_dir) {
        Ok(entries) => entries
            .filter_map(|e| e.ok())
            .filter(|e| {
                e.file_name()
                    .to_string_lossy()
                    .starts_with("G-")
                    && e.file_name().to_string_lossy().ends_with(".json")
            })
            .count(),
        Err(e) => return fail(format!("lecture du dossier ledger {} : {}", ledger_dir, e)),
    };

    // L00 : tête (Run #703) et Run #702 (D-N021 classé).
    let l00_head = match find_line(&l00, "Run #", "tête L00") {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    let l00_702 = match find_line(&l00, "Run #702 (créneau", "Run #702") {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    if !l00_702.contains("D-N021") || !l00_702.contains("chemin 12e retiré") {
        return fail(
            "L00 Run #702 : ne porte pas le classement D-N021 (chemin 12e retiré)"
                .to_string(),
        );
    }
    if !l00_702.contains("0 PR ouverte") {
        return fail("L00 Run #702 : ne porte pas « 0 PR ouverte »".to_string());
    }

    // N2 : Run #484, label EDT périmé → instant EST normalisé.
    let n2_484 = match find_line(&n2, "Run #484 (créneau", "Run #484") {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    if !n2_484.contains("W1 ANOMALIE") || !n2_484.contains("D-N021") {
        return fail("N2 Run #484 : ne porte pas W1 ANOMALIE D-N021".to_string());
    }
    let n2_wall = match first_wall_time(&n2_484) {
        Some(t) => t,
        None => {
            return fail("N2 Run #484 : horodatage mural illisible".to_string());
        }
    };
    let n2_normalized = match normalize_timestamp(&n2_wall) {
        Some(n) => n,
        None => {
            return fail(format!(
                "N2 Run #484 : horodatage « {} » non normalisable",
                n2_wall
            ));
        }
    };

    // Miroir : Bill présent, Coordinateur absent (lignes de table).
    let actors = table_actors(&miroir);
    let miroir_bill = actors.iter().any(|a| a.starts_with("Bill"));
    let miroir_coordinateur = actors.iter().any(|a| a.starts_with("Coordinateur"));
    if !miroir_bill {
        return fail("miroir Workgraph : Bill absent — la lecture ne correspond plus au Discover §2.5".to_string());
    }

    // Fiche + manifeste : l'instance F1-7 est-elle corrigée ?
    let fiche_f1_7_ok = fiche.contains("055745b")
        && fiche.contains("6f410ddd-4ef8-4834-805a-0b38ede9ba76");
    let manifeste_f1_7_ok =
        manifeste.contains("F1-7 VALIDÉE") && manifeste.contains("055745b");
    let fiche_instance_status = if fiche_f1_7_ok && manifeste_f1_7_ok {
        "résolue"
    } else {
        "ouverte"
    };

    // workgraph-state : clé pulse_2110 (entrée d'hier, non re-vérifiée).
    let pulse_2110 = workgraph_state.contains("pulse_2110");

    // -- Lectures datées (V1) : sources exactes + valeurs + horodatages.
    let r1_source = format!("{} (ligne 938)", registre_path);
    let r1_value = format!(
        "{} lignes, mtime {} ; journal 938 : merge PR #50, 055745b, 01:47:15 EST",
        registre_lines, registre_mtime
    );
    let r2_source = format!("{} (seq 37)", journal_path);
    let r2_value = format!(
        "{} lignes, mtime {}, seq 1–{} contigus, event_ids uniques ; seq 37 : {} {} à {}",
        journal_count, journal_mtime, max_seq, last_seq_type, last_seq_dispatch, last_seq_at
    );
    let r3_source = format!("{} (tête)", l00_path);
    let r3_value = format!(
        "{} lignes, mtime {} ; tête : {}",
        l00_lines,
        l00_mtime,
        l00_head.chars().take(160).collect::<String>()
    );
    let r4_source = format!("{} (Run #484)", n2_path);
    let r4_value = format!(
        "{} lignes, mtime {} ; Run #484 : W1 ANOMALIE D-N021 (12 j 7 h), label « {} » → {} (étiquette {})",
        n2_lines, n2_mtime, n2_wall, n2_normalized.iso, n2_normalized.label_status
    );
    let r5_miroir_source = format!("{} (table)", miroir_path);
    let r5_miroir_value = format!(
        "{} lignes, mtime {} ; Bill PRÉSENT, Coordinateur {}",
        miroir_lines,
        miroir_mtime,
        if miroir_coordinateur { "PRÉSENT" } else { "ABSENT" }
    );
    let r5_sheet_source =
        "Google Sheet 1OFRYjujs81fPSS4HJWrB4M9yeduQAd35UVvaXBiHXrI, citée via DISCOVER-F1-8.md §2.5"
            .to_string();
    let r5_sheet_value =
        "12 lignes (en-tête + 11) ; Bill ABSENT ; Coordinateur ×2 PRÉSENT ; dernier avancement 02:08, master 5cfffa9"
            .to_string();
    let r5_sheet_read_at = "2026-11-13T02:13:32-05:00".to_string();
    let r6_source = format!("{}/G-20261112-035.json", ledger_dir);
    let r6_value = format!(
        "{} reçus, dernier G-20261112-036 ; G-20261112-035 : sha 055745b853495c38f0aaa0ae6c3d2adad9e89177, merge PR #50",
        ledger_count
    );
    let r7_fiche_source = format!("{} (§ F1-7, §1)", fiche_path);
    let r7_fiche_value = format!(
        "{} lignes, mtime {} ; F1-7 mergée 055745b : {} ; ID 11e complet : {}",
        fiche_lines,
        fiche_mtime,
        if fiche.contains("055745b") { "oui" } else { "non" },
        if fiche.contains("6f410ddd-4ef8-4834-805a-0b38ede9ba76") {
            "oui"
        } else {
            "non"
        }
    );
    let r7_manifeste_source = format!("{} (validated_by)", manifeste_path);
    let r7_manifeste_value = format!(
        "{} o, mtime {} ; F1-7 VALIDÉE : {} ; fonctions nommées : 7 (Vision comprise)",
        manifeste.len(), manifeste_mtime,
        if manifeste.contains("F1-7 VALIDÉE") { "oui" } else { "non" }
    );
    let r8_source = format!("{} (pulse_2110)", workgraph_state_path);
    let r8_value = format!(
        "mtime {} ; pulse_2110 : {} (entrée d'hier, non re-vérifiée, non re-routée)",
        workgraph_state_mtime,
        if pulse_2110 { "présente" } else { "absente" }
    );
    let r9_source = format!("{} (seq 1–{})", inventaire_path, inventaire_count);
    let r9_value = format!(
        "{} lignes, mtime {}, seq 1–{} contigus ; les seq 710/711/1054/1055/1056/1080 sont des entrées « absence », pas des trous",
        inventaire_count, inventaire_mtime, inventaire_count
    );
    let master_source = "API GitHub repos/Amdkn/Aspace_OS_V5/commits/master (injecté par l'opérateur)".to_string();
    let master_value = format!("master {} ; {} PR ouverte(s)", master, open_prs);
    let master_drift = master != recu_sha;

    let readings = vec![
        DatedReading { source: &r1_source, value: &r1_value, read_at: &read_at_now },
        DatedReading { source: &r2_source, value: &r2_value, read_at: &read_at_now },
        DatedReading { source: &r3_source, value: &r3_value, read_at: &read_at_now },
        DatedReading { source: &r4_source, value: &r4_value, read_at: &read_at_now },
        DatedReading { source: &r5_miroir_source, value: &r5_miroir_value, read_at: &read_at_now },
        DatedReading { source: &r5_sheet_source, value: &r5_sheet_value, read_at: &r5_sheet_read_at },
        DatedReading { source: &r6_source, value: &r6_value, read_at: &read_at_now },
        DatedReading { source: &r7_fiche_source, value: &r7_fiche_value, read_at: &read_at_now },
        DatedReading { source: &r7_manifeste_source, value: &r7_manifeste_value, read_at: &read_at_now },
        DatedReading { source: &r8_source, value: &r8_value, read_at: &read_at_now },
        DatedReading { source: &r9_source, value: &r9_value, read_at: &read_at_now },
        DatedReading { source: &master_source, value: &master_value, read_at: &master_read_at },
        DatedReading { source: &master_source, value: &master_value, read_at: &open_prs_read_at },
    ];

    // -- Divergences portées (V4) : deux versions + statut + source + date.
    let divergences = vec![
        Divergence {
            name: "D-N021/24/26/32 — silence 12 j",
            version_a: "L00 #702 : classés (chemin 12e retiré, ordre S0 00:32 EST 11-11 ; franchissements classés Runs #642/#643)",
            version_b: "N2 Run #484 : W1 ANOMALIE portée (12 j 7 h)",
            status: "classée",
            source: "ordre S0 00:32 EST 11-11 ; L00 Runs #642/#643 ; N2 #484",
            date: "2026-11-11",
        },
        Divergence {
            name: "N2 ombre vs L00 (W1 ANOMALIE D-N021)",
            version_a: "L00 #702 : D-N021 classé, divergence notée non re-routée en double",
            version_b: "N2 #484 : W1 ANOMALIE D-N021 (12 j 7 h)",
            status: "classée",
            source: "L00 #702 (« DIVERGENCE NOTÉE, NON ROUTÉE EN DOUBLE »)",
            date: "2026-11-13",
        },
        Divergence {
            name: "Écart #601 (ligne absente L00-ETAT)",
            version_a: "L00-ETAT : ligne #601 absente",
            version_b: "consignation attendue : ligne #601 présente",
            status: "ouverte",
            source: "L00 #702",
            date: "2026-11-13",
        },
        Divergence {
            name: "Fiche/manifeste — instance F1-7",
            version_a: "fiche : F1-7 PR ouverte, non mergée ; manifeste : F1-7 jugement à venir",
            version_b: "PR #50 mergée 055745b, jugement VALIDÉE, journal 938",
            status: fiche_instance_status,
            source: "fiche + manifeste relus au fichier",
            date: "2026-11-13",
        },
        Divergence {
            name: "Fiche/manifeste — dérive structurelle",
            version_a: "aucun chemin d'atterrissage ne met à jour la fiche",
            version_b: "fiche et manifeste à jour à chaque atterrissage",
            status: "ouverte",
            source: "Discover F1-8 §2.7",
            date: "2026-11-13",
        },
        Divergence {
            name: "L00 cadence déclarée 1 h vs observée ~40 min",
            version_a: "cron l00-veille-w1-w7 : interval@1h déclaré",
            version_b: "runs #699 00:17 → #702 01:57 observés ~40 min",
            status: "ouverte",
            source: "cron.list + L00-ETAT",
            date: "2026-11-13",
        },
        Divergence {
            name: "Workgraph Sheet ↔ miroir (Bill/Coordinateur)",
            version_a: "miroir : Bill PRÉSENT, Coordinateur ABSENT",
            version_b: "Sheet (02:13:32 EST) : Bill ABSENT, Coordinateur ×2 PRÉSENT",
            status: "ouverte",
            source: "DISCOVER-F1-8.md §2.5",
            date: "2026-11-13",
        },
        Divergence {
            name: "Jugement F1-5 absent comme judgment_rendered au journal",
            version_a: "journal-router : aucun judgment_rendered F1-5",
            version_b: "closure_pulse seq 20 le porte comme preuve",
            status: "classée",
            source: "Discover F1-7 §3.4",
            date: "2026-11-12",
        },
        Divergence {
            name: "Supabase injoignable (point rouge 08:44 EST 11-11)",
            version_a: "L00 Run #604 : injoignable 5/5",
            version_b: "service attendu joignable",
            status: "ouverte",
            source: "L00 #702",
            date: "2026-11-11",
        },
        Divergence {
            name: "Design D-N046 non livré",
            version_a: "L00 #702 : À surveiller",
            version_b: "design livré",
            status: "ouverte",
            source: "L00 #702",
            date: "2026-11-13",
        },
        Divergence {
            name: "Désarchivage V4 (#107) en attente",
            version_a: "issue #107 ouverte, décision S0 en attente",
            version_b: "décision rendue",
            status: "ouverte",
            source: "L00 #702 + issue #107",
            date: "2026-11-06",
        },
    ];
    let known_divergences: Vec<&str> =
        divergences.iter().map(|d| d.name).collect();

    // -- Absences consignées (V7).
    let absences: Vec<&str> = vec![
        "Reçus PR #38/#39 absents (grep SHAs 1606405/bfeae74 = 0, L00 #702)",
        "21 runs L00 absents (#657–#666, #673, #675–#684)",
        "correction jamais émis au journal (0/37 événements)",
    ];
    let known_absences: Vec<&str> = absences.clone();

    // -- Limites nommées (V8).
    let limits: Vec<&str> = vec![
        "Les 13 mémoires — la vision ne les re-vérifie pas (Discover §2.8)",
        "Le bundle / shared brain — hors périmètre",
        "FKB02 — hors périmètre",
        "Les notes quotidiennes ~/memory/ — sources de faits, pas registres d'état",
        "Le ledger distant — non re-vérifié ce tour (0 branche work-*-ledger au distant, établi F1-7)",
        "La Google Sheet Workgraph — non relue en direct par la CLI (0 appel réseau) ; lecture citée du Discover (02:13:32 EST)",
        "La cause des 21 runs L00 absents — non établie par ce pas (D-F1-8-9)",
    ];

    let command = format!(
        "hold-vision check --case {} --registre {} --journal {} --l00 {} --n2 {} --miroir {} --fiche {} --manifeste {} --workgraph-state {} --inventaire {} --ledger-dir {} --master {} --master-read-at {} --open-prs {} --open-prs-read-at {}{}",
        case,
        registre_path,
        journal_path,
        l00_path,
        n2_path,
        miroir_path,
        fiche_path,
        manifeste_path,
        workgraph_state_path,
        inventaire_path,
        ledger_dir,
        master,
        master_read_at,
        open_prs,
        open_prs_read_at,
        match &fautif_path {
            Some(p) => format!(" --fautif {}", p),
            None => String::new(),
        }
    );

    // -- Le fait fautif planté F-V1 (A-F1-8-1) : une seule différence —
    // l'ancre du seuil D-N053 (journal 938 au lieu de journal 930).
    if let Some(path) = &fautif_path {
        let fautif_text = match read_file(path, "dossier fautif") {
            Ok(t) => t,
            Err(e) => return fail(e),
        };
        reads += 1;
        let claim = match parse_fautif(&fautif_text) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("dossier fautif {} : {}", path, e);
                return ExitCode::from(1);
            }
        };
        let anchor_names = claim.anchor_dispatch_named == claim.dispatch_id;
        let faulty_threshold = Threshold {
            dispatch_id: Box::leak(claim.dispatch_id.clone().into_boxed_str()),
            anchor_journal: claim.anchor_journal,
            anchor_names_dispatch: anchor_names,
            anchor_dispatch_named: Box::leak(claim.anchor_dispatch_named.clone().into_boxed_str()),
            anchor_at: &anchor_d_n055,
            threshold_at: &threshold_d_n055,
            crossed: true,
            correct_anchor: Box::leak(claim.correct_anchor.clone().into_boxed_str()),
        };
        let state = VisionState {
            readings: &readings,
            comparisons: &[],
            divergences: &divergences,
            thresholds: &[faulty_threshold],
            known_divergences: &known_divergences,
            absences: &absences,
            known_absences: &known_absences,
            limits: &limits,
            claims_complete: false,
            claims_resolution: false,
            modifies_source: false,
            consigns_receipt: false,
            planted_fautif: Some(PlantedFautif {
                dispatch_id: Box::leak(claim.dispatch_id.clone().into_boxed_str()),
                anchor_journal: claim.anchor_journal,
                crossed: true,
            }),
            max_seq,
        };
        match validate_vision(&state, now) {
            Ok(_) => {
                println!("ÉCHEC DU HOLD-OUT : le fait fautif planté F-V1 a été accepté — H-F1-7 échoue, la fonction Vision revient à ses mécanismes d'origine");
                println!("  Commande : {}", command);
                println!("  Horodatage : {}", read_at_now);
                return ExitCode::from(3);
            }
            Err(rejection) => {
                if rejection.rule == "V3" {
                    println!("{}", rejection);
                    println!("  Seuil affirmé : {}", claim.threshold_claimed);
                    println!("  Commande : {}", command);
                    println!("  Horodatage : {}", read_at_now);
                    println!(
                        "  Re-lecture : {} lecture(s) au fichier, 0 appel réseau, 0 recherche sémantique",
                        reads
                    );
                    return ExitCode::from(2);
                }
                println!(
                    "ÉCHEC DU HOLD-OUT : le fautif F-V1 est rejeté {} au lieu de V3 — la règle nommée n'est pas celle du design",
                    rejection.rule
                );
                println!("{}", rejection);
                println!("  Commande : {}", command);
                println!("  Horodatage : {}", read_at_now);
                return ExitCode::from(3);
            }
        }
    }

    // -- Cas d'essai T1 / T2 / T3 (Discover §5.2).
    let (comparisons, thresholds) = match case.as_str() {
        "t1" => {
            let c1_left_source = "registre, ligne 938".to_string();
            let c1_left_value =
                "merge PR #50, 055745b, 01:47:15 EST".to_string();
            let c1_right_source = "journal-router, seq 37".to_string();
            let c1_right_value =
                "merge_executed PR #50, 055745b, 2026-11-13T01:47:15-05:00".to_string();
            let c2_left_source = "journal-router, seq 37".to_string();
            let c2_left_value = c1_right_value.clone();
            let c2_right_source = "ledger local, G-20261112-035.json".to_string();
            let c2_right_value =
                "sha 055745b853495c38f0aaa0ae6c3d2adad9e89177, merge PR #50, suite 100/100, CI 8/8"
                    .to_string();
            let c3_left_source = "master au merge (registre + journal + reçu)".to_string();
            let c3_left_value = "055745b au merge, 01:47:15 EST".to_string();
            let c3_right_source = "master lu (injecté par l'opérateur)".to_string();
            let c3_right_value = format!("{} lu à {}", master, master_read_at);
            let c4_left_source = "API GitHub, PR ouvertes (injecté par l'opérateur)".to_string();
            let c4_left_value = format!("{} PR ouverte(s), lu à {}", open_prs, open_prs_read_at);
            let c4_right_source = "L00 Run #702".to_string();
            let c4_right_value = "0 PR ouverte (vérifié à l'API ce run)".to_string();
            // Les chaînes doivent survivre jusqu'à la validation : on les
            // fuit dans des `Box::leak` (processus CLI à vie courte).
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let comparisons = vec![
                Comparison {
                    name: "registre ligne 938 = journal seq 37",
                    left: DatedReading {
                        source: leak(c1_left_source),
                        value: leak(c1_left_value),
                        read_at: &read_at_now,
                    },
                    right: DatedReading {
                        source: leak(c1_right_source),
                        value: leak(c1_right_value),
                        read_at: &read_at_now,
                    },
                    outcome: Outcome::Coherent,
                    cited_seq: Some(37),
                },
                Comparison {
                    name: "journal seq 37 = reçu G-20261112-035",
                    left: DatedReading {
                        source: leak(c2_left_source),
                        value: leak(c2_left_value),
                        read_at: &read_at_now,
                    },
                    right: DatedReading {
                        source: leak(c2_right_source),
                        value: leak(c2_right_value),
                        read_at: &read_at_now,
                    },
                    outcome: Outcome::Coherent,
                    cited_seq: Some(37),
                },
                Comparison {
                    name: "master au merge vs master lu",
                    left: DatedReading {
                        source: leak(c3_left_source),
                        value: leak(c3_left_value),
                        read_at: "2026-11-13T01:47:15-05:00",
                    },
                    right: DatedReading {
                        source: leak(c3_right_source),
                        value: leak(c3_right_value),
                        read_at: &master_read_at,
                    },
                    outcome: if master_drift {
                        Outcome::Drift
                    } else {
                        Outcome::Coherent
                    },
                    cited_seq: None,
                },
                Comparison {
                    name: "PR ouvertes : API vs L00 #702",
                    left: DatedReading {
                        source: leak(c4_left_source),
                        value: leak(c4_left_value),
                        read_at: &open_prs_read_at,
                    },
                    right: DatedReading {
                        source: leak(c4_right_source),
                        value: leak(c4_right_value),
                        read_at: &read_at_now,
                    },
                    outcome: Outcome::Coherent,
                    cited_seq: None,
                },
            ];
            (comparisons, Vec::<Threshold>::new())
        }
        "t2" => {
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let c1_left_source = "registre, ligne 938".to_string();
            let c1_left_value = "journal 938 nomme D-N055 (F1-7 CLOSE, merge PR #50)".to_string();
            let c1_right_source = "journal-router, seq 37".to_string();
            let c1_right_value =
                "seq 37 merge_executed D-N055-F1-7-MERGE à 2026-11-13T01:47:15-05:00".to_string();
            let c2_left_source = "registre, ligne 930".to_string();
            let c2_left_value = "journal 930 nomme D-N053 (F2 CLOSE, merge PR #46)".to_string();
            let c2_right_source = "L00 Run #702".to_string();
            let c2_right_value =
                "D-N053 dernier événement nommant = journal 930 ~21:00, seuil ~09:00 EST 11-13"
                    .to_string();
            let comparisons = vec![
                Comparison {
                    name: "ancre D-N055 = journal 938",
                    left: DatedReading {
                        source: leak(c1_left_source),
                        value: leak(c1_left_value),
                        read_at: &read_at_now,
                    },
                    right: DatedReading {
                        source: leak(c1_right_source),
                        value: leak(c1_right_value),
                        read_at: &read_at_now,
                    },
                    outcome: Outcome::Coherent,
                    cited_seq: Some(37),
                },
                Comparison {
                    name: "ancre D-N053 = journal 930",
                    left: DatedReading {
                        source: leak(c2_left_source),
                        value: leak(c2_left_value),
                        read_at: &read_at_now,
                    },
                    right: DatedReading {
                        source: leak(c2_right_source),
                        value: leak(c2_right_value),
                        read_at: &read_at_now,
                    },
                    outcome: Outcome::Coherent,
                    cited_seq: None,
                },
            ];
            let thresholds = vec![
                Threshold {
                    dispatch_id: "D-N055",
                    anchor_journal: 938,
                    anchor_names_dispatch: true,
                    anchor_dispatch_named: "D-N055",
                    anchor_at: &anchor_d_n055,
                    threshold_at: &threshold_d_n055,
                    crossed: false,
                    correct_anchor: "journal 938, ~01:52, seuil ~13:52, non franchi",
                },
                Threshold {
                    dispatch_id: "D-N053",
                    anchor_journal: 930,
                    anchor_names_dispatch: true,
                    anchor_dispatch_named: "D-N053",
                    anchor_at: &anchor_d_n053,
                    threshold_at: &threshold_d_n053,
                    crossed: false,
                    correct_anchor: "journal 930, ~21:00, seuil ~09:00, non franchi",
                },
            ];
            (comparisons, thresholds)
        }
        _ => {
            // t3
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let c1_left_source = "L00-N2-ETAT, Run #484".to_string();
            let c1_left_value = format!(
                "W1 ANOMALIE D-N021 (12 j 7 h), label « {} » → {} (étiquette {})",
                n2_wall, n2_normalized.iso, n2_normalized.label_status
            );
            let c1_right_source = "L00-ETAT, Run #702".to_string();
            let c1_right_value =
                "D-N021 classé (chemin 12e retiré, ordre S0 00:32 EST 11-11 ; franchissement classé Run #642)"
                    .to_string();
            let comparisons = vec![Comparison {
                name: "N2 Run #484 vs L00 Run #702 (D-N021)",
                left: DatedReading {
                    source: leak(c1_left_source),
                    value: leak(c1_left_value),
                    read_at: &read_at_now,
                },
                right: DatedReading {
                    source: leak(c1_right_source),
                    value: leak(c1_right_value),
                    read_at: &read_at_now,
                },
                outcome: Outcome::Divergent,
                cited_seq: None,
            }];
            (comparisons, Vec::<Threshold>::new())
        }
    };

    let state = VisionState {
        readings: &readings,
        comparisons: &comparisons,
        divergences: &divergences,
        thresholds: &thresholds,
        known_divergences: &known_divergences,
        absences: &absences,
        known_absences: &known_absences,
        limits: &limits,
        claims_complete: false,
        claims_resolution: false,
        modifies_source: false,
        consigns_receipt: false,
        planted_fautif: None,
        max_seq,
    };

    match validate_vision(&state, now) {
        Ok(valid) => {
            let case_name = match case.as_str() {
                "t1" => "T1 — cohérence F1-7 (registre ↔ journal ↔ master ↔ reçu)",
                "t2" => "T2 — seuils D-N055/D-N053 non franchis sur leurs ancres",
                _ => "T3 — divergence classée N2 portée",
            };
            println!("ACCEPTÉ — État de vision {} : V1–V8 passés", case_name);
            println!("  Lectures datées : {} (R1–R9, master + PR injectés, Sheet citée)", valid.readings);
            for r in &readings {
                println!("    {} — {} (lu : {})", r.source, r.value, r.read_at);
            }
            println!("  Comparaisons rejouables : {}", valid.comparisons);
            for c in &comparisons {
                let outcome = match c.outcome {
                    Outcome::Coherent => "cohérente",
                    Outcome::Divergent => "divergente-portée",
                    Outcome::Drift => "dérive datée",
                };
                println!(
                    "    {} — « {} » = « {} » ({})",
                    c.name, c.left.value, c.right.value, outcome
                );
            }
            println!("  Divergences portées : {}", valid.divergences);
            for d in &divergences {
                println!(
                    "    {} — statut « {} » ({} ; {})",
                    d.name, d.status, d.source, d.date
                );
            }
            println!("  Seuils : {}", valid.thresholds);
            for t in &thresholds {
                println!(
                    "    {} — ancre journal {}, seuil {}, non franchi",
                    t.dispatch_id, t.anchor_journal, t.threshold_at
                );
            }
            println!("  Absences consignées : {}", valid.absences);
            for a in &absences {
                println!("    {}", a);
            }
            println!("  Limites nommées : {}", valid.limits);
            for l in &limits {
                println!("    {}", l);
            }
            println!(
                "  Contradictions non portées : {}",
                valid.unported_contradictions
            );
            println!("  Commande : {}", command);
            println!("  Horodatage : {}", read_at_now);
            println!(
                "  Re-lecture : {} lecture(s) au fichier, 0 appel réseau, 0 recherche sémantique",
                reads
            );
            ExitCode::from(0)
        }
        Err(rejection) => {
            println!("{}", rejection);
            println!("  Commande : {}", command);
            println!("  Horodatage : {}", read_at_now);
            println!(
                "  Re-lecture : {} lecture(s) au fichier, 0 appel réseau, 0 recherche sémantique",
                reads
            );
            ExitCode::from(2)
        }
    }
}
