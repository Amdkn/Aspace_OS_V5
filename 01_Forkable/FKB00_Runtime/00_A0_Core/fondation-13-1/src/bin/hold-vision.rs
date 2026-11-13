//! `hold-vision` — interface en ligne de commande de la fonction
//! Vision (D-N055 F1-8, généralisée F1-11, D-F1-11-4). Sous-commande :
//!
//! * `check --case <t1|t2|t3> --registre <chemin> --journal <chemin>`
//!   `--l00 <chemin> --n2 <chemin> --miroir <chemin> --fiche <chemin>`
//!   `--manifeste <chemin> --workgraph-state <chemin>`
//!   `--inventaire <chemin> --ledger-dir <dossier> --master <sha40>`
//!   `--master-read-at <iso> --open-prs <n> --open-prs-read-at <iso>`
//!   `[--dispatch-a <D-N055>] [--dispatch-b <D-N053>]`
//!   `[--workgraph-key <pulse_NNNN>] [--sheet-value <texte>]`
//!   `[--sheet-read-at <iso>] [--fautif <VISION-FAUTIF-1.md>]`
//!   — rendu d'un état de vision (V1–V9, ordre V1 → V6 → V2 → V3 → V4 →
//!   V7 → V5 → V8 → V9) ; sort 0 si l'état est accepté, 2 si rejeté (règle
//!   nommée). Avec `--fautif`, l'état rendu est le fait fautif planté :
//!   F-V1 (seuil D-N053 sur l'ancre journal 938) — rejet attendu V3
//!   (sortie 2) — ou F-V5 (libellés « seq 37 » et « 0 PR ouverte »
//!   présentés comme courants — dossier portant des lignes `**Libellé`) —
//!   rejet attendu V9 (sortie 2) ; tout autre sort (acceptation, ou
//!   rejet par une autre règle) est un échec du hold-out (sortie 3).
//!
//! Généralisation (D-F1-11-4) : les 9 gates A1–A9 sont des recherches
//! (dernière ligne / dernier événement / dernière valeur — le numéro est
//! une sortie, pas une entrée) ; les 11 libellés B1–B11 sont des sorties
//! calculées (le seq lu, le nombre de PR lu, le dernier reçu compté) ;
//! les entrées non lisibles sont injectées par l'opérateur
//! (`--dispatch-a`, `--dispatch-b`, `--workgraph-key`, `--sheet-value`,
//! `--sheet-read-at`, patron `--master` / `--open-prs` déjà dans le
//! code). Le commentaire daté l.496 (A9) est supprimé. La règle V9
//! (D-F1-11-10) rejette un libellé daté qui ne correspond pas à la
//! valeur lue au journal / au registre / à l'API.
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
//! * `--sheet-value` / `--sheet-read-at` : la valeur lue de la Google
//!   Sheet Workgraph, avec son horodatage de lecture (absentes, la
//!   lecture citée du Discover F1-8 §2.5 est portée comme telle, datée).
//!
//! Zéro appel sortant : la CLI ne lit que des fichiers locaux et n'écrit
//! que sur stdout/stderr.

use r10_validator::vision::{
    canonical_label_value, normalize_timestamp, parse_fautif, parse_fautif_labels,
    threshold_after, validate_vision, Comparison, DatedReading, Divergence, Outcome,
    PlantedFautif, Threshold, VisionLabel, VisionState,
};
use r10_validator::{format_iso_utc, now_unix, parse_iso8601_offset, parse_json};
use std::fs;
use std::process::ExitCode;
use std::time::UNIX_EPOCH;

fn usage() -> String {
    "usage: hold-vision check --case <t1|t2|t3> --registre <chemin> --journal <chemin> --l00 <chemin> --n2 <chemin> --miroir <chemin> --fiche <chemin> --manifeste <chemin> --workgraph-state <chemin> --inventaire <chemin> --ledger-dir <dossier> --master <sha40> --master-read-at <iso> --open-prs <n> --open-prs-read-at <iso> [--dispatch-a <D-N055>] [--dispatch-b <D-N053>] [--workgraph-key <pulse_NNNN>] [--sheet-value <texte>] [--sheet-read-at <iso>] [--fautif <VISION-FAUTIF-1.md>]".to_string()
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

/// La dernière ligne (1-based) contenant `needle`, ou une erreur nommée
/// (A1/A2/A5/A6 : la recherche remplace la constante de ligne).
/// Pour les fichiers append-only (registre, N2, journal) : la dernière
/// en ordre de fichier est la plus récente.
fn last_line_naming(text: &str, needle: &str, what: &str) -> Result<(usize, String), String> {
    let mut found: Option<(usize, String)> = None;
    for (i, line) in text.lines().enumerate() {
        if line.contains(needle) {
            found = Some((i + 1, line.to_string()));
        }
    }
    found.ok_or_else(|| format!("{} introuvable (aucune ligne ne nomme « {} »)", what, needle))
}

/// La première ligne (1-based) contenant `needle`, ou une erreur nommée.
/// Pour le L00 (trié du plus récent au plus ancien) : la première en
/// ordre de fichier est la plus récente.
fn first_line_naming(text: &str, needle: &str, what: &str) -> Result<(usize, String), String> {
    for (i, line) in text.lines().enumerate() {
        if line.contains(needle) {
            return Ok((i + 1, line.to_string()));
        }
    }
    Err(format!("{} introuvable (aucune ligne ne nomme « {} »)", what, needle))
}

/// Le numéro de run « Run #NNN » d'une ligne, ou `None`.
fn run_number_in_line(line: &str) -> Option<usize> {
    let at = line.find("Run #")?;
    let rest = &line[at + 5..];
    let digits: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
    digits.parse().ok()
}

/// Le nombre « N PR ouverte(s) » d'une ligne, ou `None`.
fn pr_count_in_line(line: &str) -> Option<usize> {
    let at = line.find("PR ouverte")?;
    let before = line[..at].trim_end();
    let digits: String = before
        .chars()
        .rev()
        .take_while(|c| c.is_ascii_digit())
        .collect::<String>()
        .chars()
        .rev()
        .collect();
    digits.parse().ok()
}

/// Le premier SHA complet (40 hex) d'un texte, ou `None`.
fn find_sha40(text: &str) -> Option<String> {
    let bytes = text.as_bytes();
    let mut i = 0;
    while i + 40 <= bytes.len() {
        // Ne découper qu'aux frontières de caractères (le texte porte
        // des accents — un découpage à l'octet paniquerait).
        if !text.is_char_boundary(i) || !text.is_char_boundary(i + 40) {
            i += 1;
            continue;
        }
        let w = &text[i..i + 40];
        if w.bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
            && (i == 0 || !bytes[i - 1].is_ascii_hexdigit())
            && (i + 40 == bytes.len() || !bytes[i + 40].is_ascii_hexdigit())
        {
            return Some(w.to_string());
        }
        i += 1;
    }
    None
}

/// Le premier « PR #NN » d'un texte, ou `None`.
fn find_pr_number(text: &str) -> Option<usize> {
    let at = text.find("PR #")?;
    let rest = &text[at + 4..];
    let digits: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
    digits.parse().ok()
}

/// La fiche porte-t-elle le pas comme clos — « F1-8 CLOSE » ou « F1-8 clos »
/// (la fiche mêle les deux formes ; le design cite les deux en exemple).
fn fiche_step_closed(fiche: &str, step: &str) -> bool {
    let lower = fiche.to_lowercase();
    let s = step.to_lowercase();
    lower.contains(&format!("{} close", s)) || lower.contains(&format!("{} clos", s))
}

/// Le pas d'un dispatch de merge (« D-N055-F1-10-MERGE » → « F1-10 »).
fn merge_step_of(dispatch_id: &str, dispatch_a: &str) -> String {
    dispatch_id
        .strip_prefix(&format!("{}-", dispatch_a))
        .and_then(|s| s.strip_suffix("-MERGE"))
        .unwrap_or(dispatch_id)
        .to_string()
}

/// Les numéros de run des entrées L00 (lignes « Run #NNN (créneau ») et
/// les trous entre le premier et le dernier (B8 : comptage re-lu).
fn l00_entry_runs(text: &str) -> (Vec<usize>, Vec<usize>) {
    let mut runs: Vec<usize> = Vec::new();
    for line in text.lines() {
        if let Some(at) = line.find("Run #") {
            if line[at..].contains("(créneau") {
                let rest = &line[at + 5..];
                let digits: String =
                    rest.chars().take_while(|c| c.is_ascii_digit()).collect();
                if let Ok(n) = digits.parse::<usize>() {
                    runs.push(n);
                }
            }
        }
    }
    runs.sort_unstable();
    runs.dedup();
    if runs.is_empty() {
        return (runs, Vec::new());
    }
    let missing: Vec<usize> = (*runs.first().unwrap()..=*runs.last().unwrap())
        .filter(|n| !runs.contains(n))
        .collect();
    (runs, missing)
}

/// Formate des numéros manquants en plages (« #657–#666, #673, #675–#684 »).
fn format_ranges(missing: &[usize]) -> String {
    if missing.is_empty() {
        return "aucun".to_string();
    }
    let mut out = String::new();
    let mut i = 0;
    while i < missing.len() {
        let start = missing[i];
        let mut end = start;
        while i + 1 < missing.len() && missing[i + 1] == end + 1 {
            i += 1;
            end = missing[i];
        }
        if !out.is_empty() {
            out.push_str(", ");
        }
        if end == start {
            out.push_str(&format!("#{}", start));
        } else {
            out.push_str(&format!("#{}–#{}", start, end));
        }
        i += 1;
    }
    out
}

/// La dernière clé « pulse_* » d'un texte d'état, en ordre de fichier
/// (A8 : dérivée de l'état courant, pas une constante). Le format a
/// évolué : `pulse_HHMM` puis `pulse_HHMM_MMDD` — la clé complète est
/// reprise, suffixe compris ; la dernière en ordre de fichier est la
/// plus récente (l'état est append-only).
fn last_pulse_key(text: &str) -> Option<String> {
    let mut last: Option<String> = None;
    let bytes = text.as_bytes();
    let mut i = 0;
    while i + 6 < bytes.len() {
        // Ne découper qu'aux frontières de caractères (le texte porte
        // des accents — un découpage à l'octet paniquerait).
        if !text.is_char_boundary(i) || !text.is_char_boundary(i + 6) {
            i += 1;
            continue;
        }
        if &text[i..i + 6] == "pulse_" {
            let rest = &text[i + 6..];
            let digits: String =
                rest.chars().take_while(|c| c.is_ascii_digit()).collect();
            if !digits.is_empty() {
                let mut key = format!("pulse_{}", digits);
                let after = &rest[digits.len()..];
                if after.starts_with('_') {
                    let suffix: String = after[1..]
                        .chars()
                        .take_while(|c| c.is_ascii_digit())
                        .collect();
                    if !suffix.is_empty() {
                        key.push('_');
                        key.push_str(&suffix);
                    }
                }
                last = Some(key);
                i += 6 + digits.len();
            } else {
                i += 1;
            }
        } else {
            i += 1;
        }
    }
    last
}

/// Un événement du journal-router, lu au fichier (A3 : la recherche
/// remplace le seq constant).
struct JournalEvent {
    seq: usize,
    typ: String,
    dispatch_id: String,
    at: String,
    proof_compact: String,
}

fn parse_journal_events(text: &str, path: &str) -> Result<Vec<JournalEvent>, String> {
    let mut out = Vec::new();
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
        out.push(JournalEvent {
            seq,
            typ: json
                .get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            dispatch_id: json
                .get("dispatch_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            at: json
                .get("at")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            proof_compact: json
                .get("proof")
                .map(|p| p.to_compact())
                .unwrap_or_default(),
        });
    }
    Ok(out)
}

/// « ~HH:MM » d'un ISO 8601 avec offset, ou la chaîne telle quelle.
fn hhmm(iso: &str) -> String {
    if iso.len() >= 16 {
        format!("~{}", &iso[11..16])
    } else {
        iso.to_string()
    }
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
    // Arguments injectés par l'opérateur (D-F1-11-4) : les entrées non
    // lisibles depuis ce poste. Défauts = les dispatches du pas F1-11.
    let dispatch_a = arg_value(rest, "--dispatch-a")
        .unwrap_or_else(|_| "D-N055".to_string());
    let dispatch_b = arg_value(rest, "--dispatch-b")
        .unwrap_or_else(|_| "D-N053".to_string());
    let workgraph_key_arg = arg_value(rest, "--workgraph-key").ok();
    let sheet_value = arg_value(rest, "--sheet-value").ok();
    let sheet_read_at = arg_value(rest, "--sheet-read-at").ok();

    let now = now_unix();
    let read_at_now = format_iso_utc(now);
    let today = read_at_now[..10].to_string();

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
    if sheet_value.is_some() != sheet_read_at.is_some() {
        eprintln!("--sheet-value et --sheet-read-at vont ensemble (valeur + horodatage de lecture)");
        return ExitCode::from(1);
    }
    if let Some(at) = &sheet_read_at {
        if parse_iso8601_offset(at).is_none() {
            eprintln!("--sheet-read-at attend un ISO 8601 avec offset, reçu '{}'", at);
            return ExitCode::from(1);
        }
    }

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
    let _ = last_journal_line;

    // L'inventaire est un index : seq contigus.
    let inventaire_count = match check_seq_contiguous(&inventaire, &inventaire_path) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let _ = inventaire_lines;

    // A1/A2 — Registre : la dernière ligne nommant chaque dispatch
    // (le numéro est une SORTIE, pas une entrée — D-F1-11-4).
    let (a1_line, a1_text) = match last_line_naming(&registre, &dispatch_a, &format!("dispatch {} au registre", dispatch_a)) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let (a2_line, _a2_text) = match last_line_naming(&registre, &dispatch_b, &format!("dispatch {} au registre", dispatch_b)) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let anchor_d_n055 = match anchor_time(&a1_text) {
        Some(t) => t,
        None => return fail(format!("registre ligne {} : heure d'ancre illisible", a1_line)),
    };
    let anchor_d_n053 = match anchor_time(&_a2_text) {
        Some(t) => t,
        None => return fail(format!("registre ligne {} : heure d'ancre illisible", a2_line)),
    };
    let threshold_d_n055 = match threshold_after(&anchor_d_n055) {
        Some(t) => t,
        None => return fail("seuil D-N055 incalculable".to_string()),
    };
    let threshold_d_n053 = match threshold_after(&anchor_d_n053) {
        Some(t) => t,
        None => return fail("seuil D-N053 incalculable".to_string()),
    };
    // B9 : le seuil est re-calculé depuis l'ancre lue (ancre + 12 h) ;
    // le franchissement est re-calculé depuis l'instant du rendu.
    let crossed_d_n055 = now >= parse_iso8601_offset(&threshold_d_n055).unwrap_or(0);
    let crossed_d_n053 = now >= parse_iso8601_offset(&threshold_d_n053).unwrap_or(0);
    let correct_anchor_d_n055 = format!(
        "journal {}, {}, seuil {}, {}",
        a1_line,
        hhmm(&anchor_d_n055),
        hhmm(&threshold_d_n055),
        if crossed_d_n055 { "franchi" } else { "non franchi" }
    );
    let correct_anchor_d_n053 = format!(
        "journal {}, {}, seuil {}, {}",
        a2_line,
        hhmm(&anchor_d_n053),
        hhmm(&threshold_d_n053),
        if crossed_d_n053 { "franchi" } else { "non franchi" }
    );

    // A3 — Journal : le dernier merge_executed du dispatch A (la
    // recherche remplace le seq constant).
    let journal_events = match parse_journal_events(&journal_text, &journal_path) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let merge_event = journal_events
        .iter()
        .rev()
        .find(|e| e.typ == "merge_executed" && e.dispatch_id.starts_with(&format!("{}-", dispatch_a)));
    let merge_event = match merge_event {
        Some(e) => e,
        None => {
            return fail(format!(
                "journal : aucun merge_executed {}-* — la preuve du merge manque",
                dispatch_a
            ))
        }
    };
    let merge_seq = merge_event.seq;
    let merge_dispatch = merge_event.dispatch_id.clone();
    let merge_at = merge_event.at.clone();
    let merge_step = merge_step_of(&merge_dispatch, &dispatch_a);
    let merge_pr = match find_pr_number(&merge_event.proof_compact) {
        Some(n) => n,
        None => {
            return fail(format!(
                "journal seq {} : la preuve du merge ne porte pas de PR #NN",
                merge_seq
            ))
        }
    };
    let merge_sha = match find_sha40(&merge_event.proof_compact) {
        Some(s) => s,
        None => {
            return fail(format!(
                "journal seq {} : la preuve du merge ne porte pas de SHA complet (40 hex)",
                merge_seq
            ))
        }
    };
    let merge_short = &merge_sha[..7];

    // A4 — Ledger local : le reçu dont le sha est celui du merge trouvé
    // (B5 : le dernier reçu est compté, pas cité d'une constante).
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
    let mut recu_entry = String::new();
    let mut last_receipt = String::new();
    if let Ok(entries) = fs::read_dir(&ledger_dir) {
        let mut names: Vec<String> = entries
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| n.starts_with("G-") && n.ends_with(".json"))
            .collect();
        names.sort();
        if let Some(last) = names.last() {
            last_receipt = last.trim_end_matches(".json").to_string();
        }
        for name in &names {
            let path = format!("{}/{}", ledger_dir, name);
            if let Ok(text) = read_file(&path, "reçu") {
                reads += 1;
                if let Ok(j) = parse_json(&text) {
                    if let Some(sha) = j.get("sha").and_then(|v| v.as_str()) {
                        if sha == merge_sha {
                            recu_entry = name.trim_end_matches(".json").to_string();
                        }
                    }
                }
            }
        }
    }
    if recu_entry.is_empty() {
        return fail(format!(
            "ledger : aucun reçu ne porte le sha du merge seq {} ({} — PR #{})",
            merge_seq, merge_sha, merge_pr
        ));
    }
    // B8 (1) : les reçus PR #38/#39 sont-ils absents du ledger ?
    let pr38_39_count = {
        let mut n = 0usize;
        if let Ok(entries) = fs::read_dir(&ledger_dir) {
            for e in entries.flatten() {
                let name = e.file_name().to_string_lossy().to_string();
                if name.starts_with("G-") && name.ends_with(".json") {
                    let path = format!("{}/{}", ledger_dir, name);
                    if let Ok(text) = read_file(&path, "reçu") {
                        reads += 1;
                        if text.contains("1606405") || text.contains("bfeae74") {
                            n += 1;
                        }
                    }
                }
            }
        }
        n
    };

    // A5 — L00 : tête (première ligne « Run # ») et dernière ligne
    // nommant le dispatch A (B2 : le nombre de PR est lu à la tête).
    let l00_head = match find_line(&l00, "Run #", "tête L00") {
        Ok(l) => l,
        Err(e) => return fail(e),
    };
    let l00_head_run = match run_number_in_line(&l00_head) {
        Some(n) => n,
        None => return fail("tête L00 : numéro de run illisible".to_string()),
    };
    let l00_pr = match pr_count_in_line(&l00_head) {
        Some(n) => n,
        None => return fail("tête L00 : ne porte pas « N PR ouverte »".to_string()),
    };
    let (l00_a_line, _l00_a_text) = match first_line_naming(&l00, &dispatch_a, &format!("dispatch {} au L00", dispatch_a)) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let _ = l00_a_line;
    // B10 : la ligne de classement D-N021 est re-vérifiée au L00 courant
    // (première en ordre de fichier = la plus récente).
    let l00_d_n021 = l00
        .lines()
        .find(|l| l.contains("D-N021") && l.contains("chemin 12e retiré"));
    let l00_d_n021_ok = l00_d_n021.is_some();
    if !l00_d_n021_ok {
        return fail("L00 : le classement D-N021 (chemin 12e retiré) n'y est plus — la divergence portée est levée".to_string());
    }

    // A6 — N2 : dernière ligne nommant le dispatch A ; horodatage
    // mural normalisé (étiquette EDT périmée → instant EST).
    let (n2_a_line, n2_a_text) = match last_line_naming(&n2, &dispatch_a, &format!("dispatch {} au N2", dispatch_a)) {
        Ok(v) => v,
        Err(e) => return fail(e),
    };
    let _n2_run = run_number_in_line(&n2_a_text);
    let n2_wall = match first_wall_time(&n2_a_text) {
        Some(t) => t,
        None => {
            return fail(format!("N2 ligne {} : horodatage mural illisible", n2_a_line));
        }
    };
    let n2_normalized = match normalize_timestamp(&n2_wall) {
        Some(n) => n,
        None => {
            return fail(format!(
                "N2 ligne {} : horodatage « {} » non normalisable",
                n2_a_line, n2_wall
            ));
        }
    };

    // A7 — Fiche + manifeste : l'instance du pas du merge trouvé
    // est-elle corrigée (le pas est une sortie, pas une entrée) ?
    // Critère du design : la fiche porte le sha court du merge, le
    // manifeste porte « {step} VALIDÉE » + le sha court. Le marqueur
    // « {step} close/clos » relève de B7 (statut de divergence), pas
    // du gate A7.
    let fiche_ok = fiche.contains(merge_short);
    let manifeste_ok = manifeste.contains(&format!("{} VALIDÉE", merge_step))
        && manifeste.contains(merge_short);
    let fiche_instance_status = if fiche_ok && manifeste_ok {
        "résolue"
    } else {
        "ouverte"
    };
    if fiche_instance_status != "résolue" {
        return fail(format!(
            "fiche/manifeste : l'instance {} n'est pas corrigée (fiche porte le sha court {} : {} ; manifeste porte « {} VALIDÉE » + {} : {}) — la preuve finale ne peut pas être rendue sur un état en retard au merge",
            merge_step,
            merge_short,
            fiche.contains(merge_short),
            merge_step,
            merge_short,
            manifeste_ok
        ));
    }

    // A8 — workgraph-state : la clé est l'argument, ou la dernière
    // clé pulse_* lue dans l'état (jamais une constante).
    let workgraph_key = match &workgraph_key_arg {
        Some(k) => k.clone(),
        None => match last_pulse_key(&workgraph_state) {
            Some(k) => k,
            None => return fail("workgraph-state : aucune clé pulse_* lisible".to_string()),
        },
    };
    let workgraph_key_present = workgraph_state.contains(&workgraph_key);
    if !workgraph_key_present {
        return fail(format!(
            "workgraph-state : la clé {} est absente (dernière clé lue : {})",
            workgraph_key,
            last_pulse_key(&workgraph_state).unwrap_or_else(|| "aucune".to_string())
        ));
    }

    // Miroir : Bill présent, Coordinateur absent (lignes de table).
    let actors = table_actors(&miroir);
    let miroir_bill = actors.iter().any(|a| a.starts_with("Bill"));
    let miroir_coordinateur = actors.iter().any(|a| a.starts_with("Coordinateur"));
    if !miroir_bill {
        return fail("miroir Workgraph : Bill absent — la lecture ne correspond plus au Discover §2.5".to_string());
    }

    // -- Lectures datées (V1) : sources exactes + valeurs + horodatages.
    // B1 : r2 porte le seq lu ; B3/B4 : la Sheet est injectée ou citée
    // datée ; B5 : le dernier reçu est compté ; B6 : r9 garde les seq
    // d'inventaire F1-0 comme donnée datée.
    let (l00_runs, l00_missing) = l00_entry_runs(&l00);
    let _ = l00_runs;
    let correction_events: Vec<usize> = journal_events
        .iter()
        .filter(|e| e.typ == "correction")
        .map(|e| e.seq)
        .collect();
    let correction_list = correction_events
        .iter()
        .map(|s| s.to_string())
        .collect::<Vec<_>>()
        .join(", ");
    let r1_source = format!("{} (ligne {})", registre_path, a1_line);
    let r1_value = format!(
        "{} lignes, mtime {} ; journal {} : {} ; seuil {}",
        registre_lines, registre_mtime, a1_line, correct_anchor_d_n055, hhmm(&threshold_d_n055)
    );
    let r2_source = format!("{} (seq {})", journal_path, merge_seq);
    let r2_value = format!(
        "{} lignes, mtime {}, seq 1–{} contigus, event_ids uniques ; seq {} : merge_executed {} à {} (PR #{}, {})",
        journal_count, journal_mtime, max_seq, merge_seq, merge_dispatch, merge_at, merge_pr, merge_short
    );
    let r3_source = format!("{} (tête)", l00_path);
    let r3_value = format!(
        "{} lignes, mtime {} ; tête : {}",
        l00_lines,
        l00_mtime,
        l00_head.chars().take(160).collect::<String>()
    );
    let r4_source = format!("{} (ligne {})", n2_path, n2_a_line);
    let r4_value = format!(
        "{} lignes, mtime {} ; ligne {} : W1 ANOMALIE {}, label « {} » → {} (étiquette {})",
        n2_lines, n2_mtime, n2_a_line, dispatch_a, n2_wall, n2_normalized.iso, n2_normalized.label_status
    );
    let r5_miroir_source = format!("{} (table)", miroir_path);
    let r5_miroir_value = format!(
        "{} lignes, mtime {} ; Bill PRÉSENT, Coordinateur {}",
        miroir_lines,
        miroir_mtime,
        if miroir_coordinateur { "PRÉSENT" } else { "ABSENT" }
    );
    let (r5_sheet_source, r5_sheet_value, r5_sheet_read_at) = match (&sheet_value, &sheet_read_at) {
        (Some(v), Some(at)) => (
            "Google Sheet 1OFRYjujs81fPSS4HJWrB4M9yeduQAd35UVvaXBiHXrI, valeur injectée par l'opérateur".to_string(),
            v.clone(),
            at.clone(),
        ),
        _ => (
            "Google Sheet 1OFRYjujs81fPSS4HJWrB4M9yeduQAd35UVvaXBiHXrI, citée via DISCOVER-F1-8.md §2.5 (non relue ce run — dernière lecture citée : 2026-11-13T02:13:32-05:00)".to_string(),
            "12 lignes (en-tête + 11) ; Bill ABSENT ; Coordinateur ×2 PRÉSENT ; dernier avancement 02:08, master 5cfffa9".to_string(),
            "2026-11-13T02:13:32-05:00".to_string(),
        ),
    };
    let r6_source = format!("{}/{}.json", ledger_dir, recu_entry);
    let r6_value = format!(
        "{} reçus, dernier {} ; {} : sha {}, merge PR #{}",
        ledger_count, last_receipt, recu_entry, merge_sha, merge_pr
    );
    let r7_fiche_source = format!("{} (§ {}, §1)", fiche_path, merge_step);
    let r7_fiche_value = format!(
        "{} lignes, mtime {} ; {} mergée {} : {} ; {} CLOSE : {}",
        fiche_lines,
        fiche_mtime,
        merge_step,
        merge_short,
        if fiche.contains(merge_short) { "oui" } else { "non" },
        merge_step,
        if fiche_step_closed(&fiche, &merge_step) {
            "oui"
        } else {
            "non"
        }
    );
    let r7_manifeste_source = format!("{} (validated_by)", manifeste_path);
    let r7_manifeste_value = format!(
        "{} o, mtime {} ; {} VALIDÉE : {} ; fonctions nommées : 10 (Preuve finale comprise)",
        manifeste.len(), manifeste_mtime, merge_step,
        if manifeste.contains(&format!("{} VALIDÉE", merge_step)) { "oui" } else { "non" }
    );
    let r8_source = format!("{} ({})", workgraph_state_path, workgraph_key);
    let r8_value = format!(
        "mtime {} ; {} : présente (dernière clé lue dans l'état)",
        workgraph_state_mtime, workgraph_key
    );
    let r9_source = format!("{} (seq 1–{})", inventaire_path, inventaire_count);
    let r9_value = format!(
        "{} lignes, mtime {}, seq 1–{} contigus ; inventaire F1-0 (2026-11-11 00:15:56) : les seq 710/711/1054/1055/1056/1080 sont des entrées « absence », pas des trous",
        inventaire_count, inventaire_mtime, inventaire_count
    );
    let master_source = "API GitHub repos/Amdkn/Aspace_OS_V5/commits/master (injecté par l'opérateur)".to_string();
    let master_value = format!("master {} ; {} PR ouverte(s)", master, open_prs);
    let master_drift = master != merge_sha;

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
    // B7 : chaque statut est re-vérifié à sa source au rendu ; sinon
    // « non re-vérifié au {date} ».
    let not_reverified = format!("non re-vérifié au {}", today);
    let d_n021_status = if l00_d_n021_ok { "classée" } else { not_reverified.as_str() };
    let n2_ombre_status = if n2_a_text.contains("W1 ANOMALIE") && l00_d_n021_ok {
        "classée"
    } else {
        not_reverified.as_str()
    };
    let ecart_601_status = if l00_lines < 601 { "ouverte" } else { "résolue" };
    let derive_status = if fiche_step_closed(&fiche, &merge_step) {
        "résolue"
    } else {
        "ouverte"
    };
    let sheet_miroir_status = match &sheet_value {
        Some(v) => {
            let sheet_bill_absent = v.contains("Bill ABSENT");
            if sheet_bill_absent != miroir_bill { "ouverte" } else { "résolue" }
        }
        None => not_reverified.as_str(),
    };
    let judgment_f1_5 = journal_events
        .iter()
        .any(|e| e.typ == "judgment_rendered" && e.dispatch_id.contains("F1-5"));
    let closure_pulse_20 = journal_events
        .iter()
        .any(|e| e.seq == 20 && e.typ == "closure_pulse");
    let judgment_f1_5_status = if judgment_f1_5 {
        "résolue"
    } else if closure_pulse_20 {
        "classée"
    } else {
        not_reverified.as_str()
    };
    let d_n046_line = l00.lines().find(|l| l.contains("D-N046"));
    let d_n046_status = match d_n046_line {
        Some(l) if l.contains("non livré") => "ouverte",
        Some(l) if l.contains("livré") => "résolue",
        _ => not_reverified.as_str(),
    };
    let divergences = vec![
        Divergence {
            name: "D-N021/24/26/32 — silence 12 j",
            version_a: "L00 : classés (chemin 12e retiré, ordre S0 00:32 EST 11-11 ; franchissements classés Runs #642/#643)",
            version_b: "N2 : W1 ANOMALIE portée (12 j 7 h)",
            status: d_n021_status,
            source: "ordre S0 00:32 EST 11-11 ; L00 Runs #642/#643 ; N2",
            date: "2026-11-11",
        },
        Divergence {
            name: "N2 ombre vs L00 (W1 ANOMALIE D-N021)",
            version_a: "L00 : D-N021 classé, divergence notée non re-routée en double",
            version_b: "N2 : W1 ANOMALIE D-N021 (12 j 7 h)",
            status: n2_ombre_status,
            source: "L00 (D-N021, chemin 12e retiré) + N2",
            date: "2026-11-13",
        },
        Divergence {
            name: "Écart #601 (ligne absente L00-ETAT)",
            version_a: "L00-ETAT : ligne #601 absente",
            version_b: "consignation attendue : ligne #601 présente",
            status: ecart_601_status,
            source: "L00-ETAT",
            date: "2026-11-13",
        },
        Divergence {
            name: Box::leak(
                format!("Fiche/manifeste — instance {}", merge_step).into_boxed_str(),
            ),
            version_a: Box::leak(
                format!("fiche : {} PR ouverte, non mergée ; manifeste : {} jugement à venir", merge_step, merge_step).into_boxed_str(),
            ),
            version_b: Box::leak(
                format!("PR #{} mergée {}, jugement VALIDÉE, journal {}", merge_pr, merge_short, a1_line).into_boxed_str(),
            ),
            status: fiche_instance_status,
            source: "fiche + manifeste relus au fichier",
            date: "2026-11-13",
        },
        Divergence {
            name: "Fiche/manifeste — dérive structurelle",
            version_a: "aucun chemin d'atterrissage ne met à jour la fiche",
            version_b: "fiche et manifeste à jour à chaque atterrissage",
            status: derive_status,
            source: "Discover F1-8 §2.7",
            date: "2026-11-13",
        },
        Divergence {
            name: "L00 cadence déclarée 1 h vs observée ~40 min",
            version_a: "cron l00-veille-w1-w7 : interval@1h déclaré",
            version_b: "runs #699 00:17 → #702 01:57 observés ~40 min",
            status: not_reverified.as_str(),
            source: "cron.list + L00-ETAT",
            date: "2026-11-13",
        },
        Divergence {
            name: "Workgraph Sheet ↔ miroir (Bill/Coordinateur)",
            version_a: "miroir : Bill PRÉSENT, Coordinateur ABSENT",
            version_b: "Sheet (02:13:32 EST) : Bill ABSENT, Coordinateur ×2 PRÉSENT",
            status: sheet_miroir_status,
            source: "DISCOVER-F1-8.md §2.5",
            date: "2026-11-13",
        },
        Divergence {
            name: "Jugement F1-5 absent comme judgment_rendered au journal",
            version_a: "journal-router : aucun judgment_rendered F1-5",
            version_b: "closure_pulse seq 20 le porte comme preuve",
            status: judgment_f1_5_status,
            source: "Discover F1-7 §3.4",
            date: "2026-11-12",
        },
        Divergence {
            name: "Supabase injoignable (point rouge 08:44 EST 11-11)",
            version_a: "L00 Run #604 : injoignable 5/5",
            version_b: "service attendu joignable",
            status: not_reverified.as_str(),
            source: "L00 #702",
            date: "2026-11-11",
        },
        Divergence {
            name: "Design D-N046 non livré",
            version_a: "L00 : À surveiller",
            version_b: "design livré",
            status: d_n046_status,
            source: "L00",
            date: "2026-11-13",
        },
        Divergence {
            name: "Désarchivage V4 (#107) en attente",
            version_a: "issue #107 ouverte, décision S0 en attente",
            version_b: "décision rendue",
            status: not_reverified.as_str(),
            source: "L00 + issue #107",
            date: "2026-11-06",
        },
    ];
    let known_divergences: Vec<&str> =
        divergences.iter().map(|d| d.name).collect();

    // -- Absences consignées (V7). B8 : chaque absence est un comptage
    // lu au journal / au ledger / au L00 — jamais une constante.
    let absences: Vec<String> = vec![
        format!(
            "Reçus PR #38/#39 absents ({} reçu(s) dans le ledger portent 1606405 ou bfeae74)",
            pr38_39_count
        ),
        format!(
            "{} runs L00 absents ({})",
            l00_missing.len(),
            format_ranges(&l00_missing)
        ),
        format!(
            "correction émis {} fois au journal (seq {})",
            correction_events.len(),
            correction_list
        ),
    ];
    let known_absences: Vec<&str> = absences.iter().map(|s| s.as_str()).collect();

    // -- Limites nommées (V8).
    let limits: Vec<String> = vec![
        "Les 13 mémoires — la vision ne les re-vérifie pas (Discover §2.8)".to_string(),
        "Le bundle / shared brain — hors périmètre".to_string(),
        "FKB02 — hors périmètre".to_string(),
        "Les notes quotidiennes ~/memory/ — sources de faits, pas registres d'état".to_string(),
        "Le ledger distant — non re-vérifié ce tour (0 branche work-*-ledger au distant, établi F1-7)".to_string(),
        match (&sheet_value, &sheet_read_at) {
            (Some(_), Some(at)) => format!("La Google Sheet Workgraph — valeur injectée par l'opérateur, lue à {}", at),
            _ => "La Google Sheet Workgraph — non relue en direct par la CLI (0 appel réseau) ; lecture citée du Discover (02:13:32 EST)".to_string(),
        },
        format!(
            "La cause des {} runs L00 absents — non établie par ce pas (D-F1-8-9)",
            l00_missing.len()
        ),
    ];
    let known_limits: Vec<&str> = limits.iter().map(|s| s.as_str()).collect();

    // -- Libellés datés (V9) : sorties calculées — le seq lu, le nombre
    // de PR lu à la tête L00 vs l'API injectée.
    let seq_label = format!("seq {}", max_seq);
    let pr_l00_label = format!("{} PR ouverte(s)", l00_pr);
    let pr_api_label = format!("{} PR ouverte(s)", open_prs);
    let labels = vec![
        VisionLabel {
            name: "journal (dernier seq)",
            claimed: &seq_label,
            read: &seq_label,
            read_at: &read_at_now,
        },
        VisionLabel {
            name: Box::leak(
                format!("PR ouvertes (L00 Run #{} vs API)", l00_head_run).into_boxed_str(),
            ),
            claimed: &pr_l00_label,
            read: &pr_api_label,
            read_at: &open_prs_read_at,
        },
    ];

    let command = format!(
        "hold-vision check --case {} --registre {} --journal {} --l00 {} --n2 {} --miroir {} --fiche {} --manifeste {} --workgraph-state {} --inventaire {} --ledger-dir {} --master {} --master-read-at {} --open-prs {} --open-prs-read-at {} --dispatch-a {} --dispatch-b {}{}{}{}",
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
        dispatch_a,
        dispatch_b,
        match &workgraph_key_arg {
            Some(k) => format!(" --workgraph-key {}", k),
            None => String::new(),
        },
        match (&sheet_value, &sheet_read_at) {
            (Some(v), Some(at)) => format!(" --sheet-value '{}' --sheet-read-at {}", v, at),
            _ => String::new(),
        },
        match &fautif_path {
            Some(p) => format!(" --fautif {}", p),
            None => String::new(),
        }
    );

    // -- Les faits fautifs plantés (A-F1-8-1, A-F1-11-1) : une seule
    // différence chacun — F-V1 l'ancre du seuil D-N053 (journal 938 au
    // lieu de journal 930), F-V5 les libellés « seq 37 » et « 0 PR
    // ouverte » présentés comme courants. Le dossier F-V5 se reconnaît
    // à ses lignes `**Libellé`.
    if let Some(path) = &fautif_path {
        let fautif_text = match read_file(path, "dossier fautif") {
            Ok(t) => t,
            Err(e) => return fail(e),
        };
        reads += 1;
        if fautif_text.contains("**Libellé") {
            let claims = match parse_fautif_labels(&fautif_text) {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("dossier fautif {} : {}", path, e);
                    return ExitCode::from(1);
                }
            };
            // L'état est valide par ailleurs (une comparaison cohérente
            // registre ↔ journal, les divergences et absences portées) ;
            // seuls les libellés diffèrent — ceux du dossier remplacent
            // les valeurs affirmées calculées.
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let fautif_comparisons = vec![Comparison {
                name: leak(format!(
                    "registre ligne {} = journal seq {}",
                    a1_line, merge_seq
                )),
                left: DatedReading {
                    source: leak(format!("registre, ligne {}", a1_line)),
                    value: leak(a1_text.chars().take(160).collect::<String>()),
                    read_at: &read_at_now,
                },
                right: DatedReading {
                    source: leak(format!("journal-router, seq {}", merge_seq)),
                    value: leak(format!(
                        "merge_executed {} à {} (PR #{}, {})",
                        merge_dispatch, merge_at, merge_pr, merge_short
                    )),
                    read_at: &read_at_now,
                },
                outcome: Outcome::Coherent,
                cited_seq: Some(merge_seq),
            }];
            let mut fautif_labels: Vec<VisionLabel> = Vec::new();
            for claim in &claims {
                let canonical = canonical_label_value(&claim.claimed);
                let (name, read, read_at): (&str, &str, &str) = if claim.name == "seq" {
                    ("journal (dernier seq)", seq_label.as_str(), read_at_now.as_str())
                } else if claim.name == "PR" {
                    (
                        Box::leak(
                            format!("PR ouvertes (L00 Run #{} vs API)", l00_head_run)
                                .into_boxed_str(),
                        ),
                        pr_api_label.as_str(),
                        open_prs_read_at.as_str(),
                    )
                } else {
                    (claim.name.as_str(), "", read_at_now.as_str())
                };
                fautif_labels.push(VisionLabel {
                    name,
                    claimed: leak(canonical),
                    read,
                    read_at,
                });
            }
            let state = VisionState {
                readings: &readings,
                comparisons: &fautif_comparisons,
                divergences: &divergences,
                thresholds: &[],
                known_divergences: &known_divergences,
                absences: &known_absences,
                known_absences: &known_absences,
                limits: &known_limits,
                claims_complete: false,
                claims_resolution: false,
                modifies_source: false,
                consigns_receipt: false,
                planted_fautif: None,
                max_seq,
                labels: &fautif_labels,
            };
            match validate_vision(&state, now) {
                Ok(_) => {
                    println!("ÉCHEC DU HOLD-OUT : le fait fautif planté F-V5 a été accepté — H-F1-11 échoue, la fonction Vision revient à ses mécanismes d'origine");
                    println!("  Commande : {}", command);
                    println!("  Horodatage : {}", read_at_now);
                    return ExitCode::from(3);
                }
                Err(rejection) => {
                    if rejection.rule == "V9" {
                        println!("{}", rejection);
                        println!("  Libellés fautifs : {}", claims.iter().map(|c| format!("{} = {}", c.name, c.claimed)).collect::<Vec<_>>().join(" ; "));
                        println!("  Commande : {}", command);
                        println!("  Horodatage : {}", read_at_now);
                        println!(
                            "  Re-lecture : {} lecture(s) au fichier, 0 appel réseau, 0 recherche sémantique",
                            reads
                        );
                        return ExitCode::from(2);
                    }
                    println!(
                        "ÉCHEC DU HOLD-OUT : le fautif F-V5 est rejeté {} au lieu de V9 — la règle nommée n'est pas celle du design",
                        rejection.rule
                    );
                    println!("{}", rejection);
                    println!("  Commande : {}", command);
                    println!("  Horodatage : {}", read_at_now);
                    return ExitCode::from(3);
                }
            }
        }
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
            absences: &known_absences,
            known_absences: &known_absences,
            limits: &known_limits,
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
            labels: &labels,
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

    // -- Cas d'essai T1 / T2 / T3 (Discover §5.2) — toutes les valeurs
    // sont lues (registre, journal, ledger, L00, N2) ou injectées
    // (master, PR ouvertes) ; le numéro est une sortie.
    let (comparisons, thresholds) = match case.as_str() {
        "t1" => {
            let c1_left_source = format!("registre, ligne {}", a1_line);
            let c1_left_value = a1_text.chars().take(160).collect::<String>();
            let c1_right_source = format!("journal-router, seq {}", merge_seq);
            let c1_right_value = format!(
                "merge_executed {} à {} (PR #{}, {})",
                merge_dispatch, merge_at, merge_pr, merge_short
            );
            let c2_left_source = format!("journal-router, seq {}", merge_seq);
            let c2_left_value = c1_right_value.clone();
            let c2_right_source = format!("ledger local, {}.json", recu_entry);
            let c2_right_value = format!(
                "sha {}, merge PR #{}, suite 100/100, CI 8/8",
                merge_sha, merge_pr
            );
            let c3_left_source = "master au merge (registre + journal + reçu)".to_string();
            let c3_left_value = format!("{} au merge, {}", merge_short, merge_at);
            let c3_right_source = "master lu (injecté par l'opérateur)".to_string();
            let c3_right_value = format!("{} lu à {}", master, master_read_at);
            let c4_left_source = "API GitHub, PR ouvertes (injecté par l'opérateur)".to_string();
            let c4_left_value = format!("{} PR ouverte(s), lu à {}", open_prs, open_prs_read_at);
            let c4_right_source = format!("L00 Run #{}", l00_head_run);
            let c4_right_value = format!("{} PR ouverte(s) (lu à {})", l00_pr, read_at_now);
            let c4_outcome = if l00_pr == open_prs {
                Outcome::Coherent
            } else {
                Outcome::Divergent
            };
            // Les chaînes doivent survivre jusqu'à la validation : on les
            // fuit dans des `Box::leak` (processus CLI à vie courte).
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let comparisons = vec![
                Comparison {
                    name: leak(format!(
                        "registre ligne {} = journal seq {}",
                        a1_line, merge_seq
                    )),
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
                    cited_seq: Some(merge_seq),
                },
                Comparison {
                    name: leak(format!(
                        "journal seq {} = reçu {}",
                        merge_seq, recu_entry
                    )),
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
                    cited_seq: Some(merge_seq),
                },
                Comparison {
                    name: "master au merge vs master lu",
                    left: DatedReading {
                        source: leak(c3_left_source),
                        value: leak(c3_left_value),
                        read_at: leak(merge_at.clone()),
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
                    name: leak(format!(
                        "PR ouvertes : API vs L00 #{}",
                        l00_head_run
                    )),
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
                    outcome: c4_outcome,
                    cited_seq: None,
                },
            ];
            (comparisons, Vec::<Threshold>::new())
        }
        "t2" => {
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let c1_left_source = format!("registre, ligne {}", a1_line);
            let c1_left_value = format!(
                "journal {} nomme {} ({} CLOSE, merge PR #{})",
                a1_line, dispatch_a, merge_step, merge_pr
            );
            let c1_right_source = format!("journal-router, seq {}", merge_seq);
            let c1_right_value = format!(
                "seq {} merge_executed {} à {}",
                merge_seq, merge_dispatch, merge_at
            );
            let c2_left_source = format!("registre, ligne {}", a2_line);
            let c2_left_value = format!("journal {} nomme {}", a2_line, dispatch_b);
            let c2_right_source = format!("registre, dernière ligne nommant {}", dispatch_b);
            let c2_right_value = format!(
                "{} dernier événement nommant = journal {} {}, seuil {} EST {}",
                dispatch_b,
                a2_line,
                hhmm(&anchor_d_n053),
                hhmm(&threshold_d_n053),
                &threshold_d_n053[..10]
            );
            let comparisons = vec![
                Comparison {
                    name: leak(format!("ancre {} = journal {}", dispatch_a, a1_line)),
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
                    cited_seq: Some(merge_seq),
                },
                Comparison {
                    name: leak(format!("ancre {} = journal {}", dispatch_b, a2_line)),
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
                    dispatch_id: Box::leak(dispatch_a.clone().into_boxed_str()),
                    anchor_journal: a1_line as u32,
                    anchor_names_dispatch: true,
                    anchor_dispatch_named: Box::leak(dispatch_a.clone().into_boxed_str()),
                    anchor_at: &anchor_d_n055,
                    threshold_at: &threshold_d_n055,
                    crossed: crossed_d_n055,
                    correct_anchor: Box::leak(correct_anchor_d_n055.clone().into_boxed_str()),
                },
                Threshold {
                    dispatch_id: Box::leak(dispatch_b.clone().into_boxed_str()),
                    anchor_journal: a2_line as u32,
                    anchor_names_dispatch: true,
                    anchor_dispatch_named: Box::leak(dispatch_b.clone().into_boxed_str()),
                    anchor_at: &anchor_d_n053,
                    threshold_at: &threshold_d_n053,
                    crossed: crossed_d_n053,
                    correct_anchor: Box::leak(correct_anchor_d_n053.clone().into_boxed_str()),
                },
            ];
            (comparisons, thresholds)
        }
        _ => {
            // t3
            let leak = |s: String| -> &'static str { Box::leak(s.into_boxed_str()) };
            let c1_left_source = format!("L00-N2-ETAT, ligne {}", n2_a_line);
            let c1_left_value = n2_a_text.chars().take(160).collect::<String>();
            let c1_right_source = "L00-ETAT".to_string();
            let c1_right_value =
                "D-N021 classé (chemin 12e retiré, ordre S0 00:32 EST 11-11 ; franchissement classé Run #642)"
                    .to_string();
            let comparisons = vec![Comparison {
                name: leak(format!(
                    "N2 ligne {} vs L00 (D-N021)",
                    n2_a_line
                )),
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
        absences: &known_absences,
        known_absences: &known_absences,
        limits: &known_limits,
        claims_complete: false,
        claims_resolution: false,
        modifies_source: false,
        consigns_receipt: false,
        planted_fautif: None,
        max_seq,
        labels: &labels,
    };

    match validate_vision(&state, now) {
        Ok(valid) => {
            let case_name = match case.as_str() {
                "t1" => format!("T1 — cohérence {} (registre ↔ journal ↔ master ↔ reçu)", merge_step),
                "t2" => format!(
                    "T2 — seuils {}/{} {} sur leurs ancres",
                    dispatch_a,
                    dispatch_b,
                    if crossed_d_n055 || crossed_d_n053 { "franchis" } else { "non franchis" }
                ),
                _ => "T3 — divergence classée N2 portée".to_string(),
            };
            println!("ACCEPTÉ — État de vision {} : V1–V9 passés", case_name);
            println!("  Lectures datées : {} (R1–R9, master + PR injectés, Sheet citée ou injectée)", valid.readings);
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
                    "    {} — ancre journal {}, seuil {}, {}",
                    t.dispatch_id,
                    t.anchor_journal,
                    t.threshold_at,
                    if t.crossed { "franchi" } else { "non franchi" }
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
            println!("  Libellés datés (V9) : {}", labels.len());
            for l in &labels {
                println!(
                    "    {} — le libellé dit « {} », la valeur lue porte « {} » (lu : {})",
                    l.name, l.claimed, l.read, l.read_at
                );
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
