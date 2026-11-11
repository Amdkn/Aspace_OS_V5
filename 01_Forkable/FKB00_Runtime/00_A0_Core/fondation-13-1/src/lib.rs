//! Validateur R10 v1 — fonction Recevoir (D-N055 F1-2, Fondation 13 → 1).
//!
//! Routeur — fonction Router (D-N055 F1-3) : voir le module `router`
//! (validation R1–R8, inscription append-only, relais comme événement).
//!
//! La fonction Recevoir consigne un reçu R10 comme donnée du changeset, sans
//! Graham comme session séparée. Ce module est le contrôle déterministe :
//! il valide un dépôt JSON avant consignation, et pose `recorded_at` à la
//! consignation depuis l'horloge système — jamais repris du dépôt.
//!
//! Règles (Discover F1-2 §2), appliquées dans l'ordre
//! V1 → V8 → V7 → V2 → V3 → V4 → V5 → V6 :
//! * V1 — le dépôt est un objet JSON portant exactement les 9 clés R10 v1.
//! * V8 — `schema` = `aspace.r10-receipt.v1` exactement.
//! * V7 — `entry_id` = `G-<date>-<nnn>`, correspond au nom de fichier de
//!   destination, et n'est pas déjà consigné (jamais réécrit).
//! * V2 — `mission_id` non vide et unique (un dépôt par mission).
//! * V3 — `sha` = exactement 40 caractères `[0-9a-f]`, et le SHA résout.
//! * V4 — `observed_at` ISO 8601 avec offset, date valide, pas dans le futur.
//! * V5 — `proof` est une liste non vide de chaînes non vides.
//! * V6 — `summary` non vide, nommant le livrable (PR et/ou SHA du merge).
//!
//! Un dépôt mal formé est rejeté avec sa raison nommée — jamais corrigé
//! silencieusement, jamais de reçu inventé (D-F1-2-4).
//!
//! Zéro dépendance externe, zéro appel sortant : la résolution du SHA est
//! injectée par l'appelant (`ShaResolver`) ; la seule horloge lue est
//! l'horloge système, pour `recorded_at`.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Recevoir).

pub mod router;

use std::collections::HashSet;
use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

/// Les 9 clés exactes du format R10 v1 (Discover F1-2 §1).
pub const R10_KEYS: [&str; 9] = [
    "entry_id",
    "issuer",
    "mission_id",
    "observed_at",
    "proof",
    "recorded_at",
    "schema",
    "sha",
    "summary",
];

/// Valeur exacte de `schema` pour le format R10 v1.
pub const R10_SCHEMA: &str = "aspace.r10-receipt.v1";

// ---------------------------------------------------------------------------
// JSON minimal (std seul — aucune dépendance externe)
// ---------------------------------------------------------------------------

/// Valeur JSON.
#[derive(Debug, Clone, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Num(String),
    Str(String),
    Arr(Vec<Json>),
    Obj(Vec<(String, Json)>),
}

impl Json {
    /// Lit un champ d'un objet par son nom.
    pub fn get(&self, key: &str) -> Option<&Json> {
        match self {
            Json::Obj(pairs) => pairs.iter().find(|(k, _)| k == key).map(|(_, v)| v),
            _ => None,
        }
    }

    /// La valeur comme chaîne, si c'en est une.
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Json::Str(s) => Some(s),
            _ => None,
        }
    }

    /// Sérialise en JSON compact (une seule ligne — forme du ledger).
    pub fn to_compact(&self) -> String {
        let mut out = String::new();
        self.write_compact(&mut out);
        out
    }

    fn write_compact(&self, out: &mut String) {
        match self {
            Json::Null => out.push_str("null"),
            Json::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            Json::Num(n) => out.push_str(n),
            Json::Str(s) => write_json_string(out, s),
            Json::Arr(items) => {
                out.push('[');
                for (i, item) in items.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    item.write_compact(out);
                }
                out.push(']');
            }
            Json::Obj(pairs) => {
                out.push('{');
                for (i, (k, v)) in pairs.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    write_json_string(out, k);
                    out.push(':');
                    v.write_compact(out);
                }
                out.push('}');
            }
        }
    }
}

fn write_json_string(out: &mut String, s: &str) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0C}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
}

struct Parser<'a> {
    bytes: &'a [u8],
    pos: usize,
}

impl<'a> Parser<'a> {
    fn new(text: &'a str) -> Self {
        Parser {
            bytes: text.as_bytes(),
            pos: 0,
        }
    }

    fn peek(&self) -> Option<u8> {
        self.bytes.get(self.pos).copied()
    }

    fn skip_ws(&mut self) {
        while matches!(self.peek(), Some(b' ' | b'\t' | b'\n' | b'\r')) {
            self.pos += 1;
        }
    }

    fn expect(&mut self, b: u8) -> Result<(), String> {
        if self.peek() == Some(b) {
            self.pos += 1;
            Ok(())
        } else {
            Err(format!("attendu '{}' à l'octet {}", b as char, self.pos))
        }
    }

    fn parse_value(&mut self, depth: usize) -> Result<Json, String> {
        if depth > 64 {
            return Err("profondeur JSON maximale dépassée".to_string());
        }
        self.skip_ws();
        match self.peek() {
            Some(b'{') => self.parse_object(depth),
            Some(b'[') => self.parse_array(depth),
            Some(b'"') => Ok(Json::Str(self.parse_string()?)),
            Some(b't') => self.parse_lit("true", Json::Bool(true)),
            Some(b'f') => self.parse_lit("false", Json::Bool(false)),
            Some(b'n') => self.parse_lit("null", Json::Null),
            Some(b'-') | Some(b'0'..=b'9') => self.parse_number(),
            Some(c) => Err(format!(
                "caractère inattendu '{}' à l'octet {}",
                c as char, self.pos
            )),
            None => Err("fin de texte inattendue".to_string()),
        }
    }

    fn parse_lit(&mut self, lit: &str, value: Json) -> Result<Json, String> {
        if self.bytes[self.pos..].starts_with(lit.as_bytes()) {
            self.pos += lit.len();
            Ok(value)
        } else {
            Err(format!("littéral '{}' invalide à l'octet {}", lit, self.pos))
        }
    }

    fn parse_number(&mut self) -> Result<Json, String> {
        let start = self.pos;
        if self.peek() == Some(b'-') {
            self.pos += 1;
        }
        while matches!(self.peek(), Some(b'0'..=b'9' | b'.' | b'e' | b'E' | b'+' | b'-')) {
            self.pos += 1;
        }
        if self.pos == start {
            return Err(format!("nombre invalide à l'octet {}", start));
        }
        let text = std::str::from_utf8(&self.bytes[start..self.pos])
            .map_err(|_| "nombre non UTF-8".to_string())?;
        // Validation stricte de la forme JSON d'un nombre.
        let mut chars = text.chars().peekable();
        if chars.peek() == Some(&'-') {
            chars.next();
        }
        match chars.next() {
            Some('0') => {}
            Some('1'..='9') => {
                while matches!(chars.peek(), Some('0'..='9')) {
                    chars.next();
                }
            }
            _ => return Err(format!("nombre invalide '{}'", text)),
        }
        if chars.peek() == Some(&'.') {
            chars.next();
            if !matches!(chars.peek(), Some('0'..='9')) {
                return Err(format!("nombre invalide '{}'", text));
            }
            while matches!(chars.peek(), Some('0'..='9')) {
                chars.next();
            }
        }
        if matches!(chars.peek(), Some('e') | Some('E')) {
            chars.next();
            if matches!(chars.peek(), Some('+') | Some('-')) {
                chars.next();
            }
            if !matches!(chars.peek(), Some('0'..='9')) {
                return Err(format!("nombre invalide '{}'", text));
            }
            while matches!(chars.peek(), Some('0'..='9')) {
                chars.next();
            }
        }
        if chars.next().is_some() {
            return Err(format!("nombre invalide '{}'", text));
        }
        Ok(Json::Num(text.to_string()))
    }

    fn parse_string(&mut self) -> Result<String, String> {
        self.expect(b'"')?;
        let mut out = String::new();
        loop {
            let b = self.peek().ok_or("chaîne non terminée")?;
            self.pos += 1;
            match b {
                b'"' => return Ok(out),
                b'\\' => {
                    let esc = self.peek().ok_or("échappement non terminé")?;
                    self.pos += 1;
                    match esc {
                        b'"' => out.push('"'),
                        b'\\' => out.push('\\'),
                        b'/' => out.push('/'),
                        b'b' => out.push('\u{08}'),
                        b'f' => out.push('\u{0C}'),
                        b'n' => out.push('\n'),
                        b'r' => out.push('\r'),
                        b't' => out.push('\t'),
                        b'u' => {
                            let hi = self.parse_hex4()?;
                            if (0xD800..0xDC00).contains(&hi) {
                                // Paire de substitution UTF-16.
                                if self.peek() == Some(b'\\')
                                    && self.bytes.get(self.pos + 1) == Some(&b'u')
                                {
                                    self.pos += 2;
                                    let lo = self.parse_hex4()?;
                                    if !(0xDC00..0xE000).contains(&lo) {
                                        return Err("substitution basse invalide".to_string());
                                    }
                                    let cp = 0x10000
                                        + ((hi - 0xD800) << 10)
                                        + (lo - 0xDC00);
                                    out.push(
                                        char::from_u32(cp)
                                            .ok_or("point de code invalide")?,
                                    );
                                } else {
                                    return Err(
                                        "substitution haute sans substitution basse".to_string()
                                    );
                                }
                            } else if (0xDC00..0xE000).contains(&hi) {
                                return Err("substitution basse isolée".to_string());
                            } else {
                                out.push(char::from_u32(hi).ok_or("point de code invalide")?);
                            }
                        }
                        _ => {
                            return Err(format!(
                                "échappement invalide '\\{}'",
                                esc as char
                            ))
                        }
                    }
                }
                0x00..=0x1F => return Err("caractère de contrôle nu dans une chaîne".to_string()),
                _ => {
                    // Octet UTF-8 : on le reprend tel quel ; la validité UTF-8
                    // de l'ensemble est vérifiée à l'entrée (texte &str).
                    out.push(b as char);
                    // Les octets de suite UTF-8 (> 0x7F) sont poussés un à un
                    // puis réassemblés ci-dessous : on reconstruit à partir
                    // des octets d'origine pour ne pas corrompre le texte.
                    // (Voir parse_json : la chaîne est re-décodée en UTF-8.)
                    let _ = &out;
                }
            }
        }
    }

    fn parse_hex4(&mut self) -> Result<u32, String> {
        let mut value: u32 = 0;
        for _ in 0..4 {
            let b = self.peek().ok_or("séquence \\u tronquée")?;
            self.pos += 1;
            let digit = match b {
                b'0'..=b'9' => (b - b'0') as u32,
                b'a'..=b'f' => (b - b'a' + 10) as u32,
                b'A'..=b'F' => (b - b'A' + 10) as u32,
                _ => return Err(format!("hexadécimal invalide '{}'", b as char)),
            };
            value = value * 16 + digit;
        }
        Ok(value)
    }

    fn parse_array(&mut self, depth: usize) -> Result<Json, String> {
        self.expect(b'[')?;
        let mut items = Vec::new();
        self.skip_ws();
        if self.peek() == Some(b']') {
            self.pos += 1;
            return Ok(Json::Arr(items));
        }
        loop {
            items.push(self.parse_value(depth + 1)?);
            self.skip_ws();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b']') => {
                    self.pos += 1;
                    return Ok(Json::Arr(items));
                }
                _ => return Err(format!("',' ou ']' attendu à l'octet {}", self.pos)),
            }
        }
    }

    fn parse_object(&mut self, depth: usize) -> Result<Json, String> {
        self.expect(b'{')?;
        let mut pairs = Vec::new();
        self.skip_ws();
        if self.peek() == Some(b'}') {
            self.pos += 1;
            return Ok(Json::Obj(pairs));
        }
        loop {
            self.skip_ws();
            if self.peek() != Some(b'"') {
                return Err(format!("clé de chaîne attendue à l'octet {}", self.pos));
            }
            let key = self.parse_string()?;
            self.skip_ws();
            self.expect(b':')?;
            let value = self.parse_value(depth + 1)?;
            pairs.push((key, value));
            self.skip_ws();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b'}') => {
                    self.pos += 1;
                    return Ok(Json::Obj(pairs));
                }
                _ => return Err(format!("',' ou '}}' attendu à l'octet {}", self.pos)),
            }
        }
    }
}

/// Parse un texte JSON en `Json`.
///
/// Note : le parseur travaille sur les octets UTF-8 ; les caractères
/// multi-octets des chaînes sont décodés correctement parce que l'entrée
/// est un `&str` valide et que les octets sont re-assemblés en UTF-8 par
/// la conversion finale (voir `parse_json`).
pub fn parse_json(text: &str) -> Result<Json, String> {
    // Re-décodage sûr : on parse sur les octets, puis on corrige les
    // chaînes qui auraient été assemblées octet par octet.
    let mut parser = Parser::new(text);
    let value = parser.parse_value(0)?;
    parser.skip_ws();
    if parser.pos != parser.bytes.len() {
        return Err(format!(
            "contenu après la valeur JSON à l'octet {}",
            parser.pos
        ));
    }
    Ok(fix_strings(value, text))
}

/// Les chaînes du parseur octet-par-octet perdent les caractères UTF-8
/// multi-octets (chaque octet poussé comme `char`). On les reconstruit en
/// re-parsant les littéraux de chaîne du texte d'origine.
fn fix_strings(value: Json, _text: &str) -> Json {
    // Le parseur ci-dessus pousse les octets > 0x7F comme des `char`
    // latin-1 : chaque octet UTF-8 devient un point de code 0x80..0xFF.
    // On ré-encode chaque chaîne en latin-1 puis on décode en UTF-8.
    match value {
        Json::Str(s) => {
            let bytes: Vec<u8> = s.chars().map(|c| c as u32 as u8).collect();
            match String::from_utf8(bytes) {
                Ok(fixed) => Json::Str(fixed),
                Err(_) => Json::Str(s),
            }
        }
        Json::Arr(items) => Json::Arr(items.into_iter().map(|v| fix_strings(v, _text)).collect()),
        Json::Obj(pairs) => Json::Obj(
            pairs
                .into_iter()
                .map(|(k, v)| {
                    let kbytes: Vec<u8> = k.chars().map(|c| c as u32 as u8).collect();
                    let kfixed = String::from_utf8(kbytes).unwrap_or(k);
                    (kfixed, fix_strings(v, _text))
                })
                .collect(),
        ),
        other => other,
    }
}

// ---------------------------------------------------------------------------
// Temps — ISO 8601 avec offset (algorithme civil de Howard Hinnant)
// ---------------------------------------------------------------------------

fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y_adj = if m <= 2 { y - 1 } else { y };
    let era = if y_adj >= 0 { y_adj } else { y_adj - 399 } / 400;
    let yoe = y_adj - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146097 + doe - 719468
}

fn civil_from_days(z: i64) -> (i64, i64, i64) {
    let z = z + 719468;
    let era = if z >= 0 { z } else { z - 146096 } / 146097;
    let doe = z - era * 146097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    (if m <= 2 { y + 1 } else { y }, m, d)
}

pub(crate) fn days_in_month(y: i64, m: i64) -> i64 {
    match m {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 => {
            if (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 {
                29
            } else {
                28
            }
        }
        _ => 0,
    }
}

fn parse_u32(s: &str) -> Option<i64> {
    if s.is_empty() || !s.bytes().all(|b| b.is_ascii_digit()) {
        return None;
    }
    s.parse::<i64>().ok()
}

/// Parse `AAAA-MM-JJTHH:MM:SS±HH:MM` en secondes Unix (UTC).
/// Retourne `None` si la forme est mauvaise, la date impossible, ou
/// l'offset hors bornes.
pub fn parse_iso8601_offset(s: &str) -> Option<i64> {
    let b = s.as_bytes();
    if b.len() != 25 {
        return None;
    }
    if b[4] != b'-' || b[7] != b'-' || b[10] != b'T' || b[13] != b':' || b[16] != b':' || b[19] != b'+'
        && b[19] != b'-'
    {
        return None;
    }
    if b[22] != b':' {
        return None;
    }
    let year = parse_u32(&s[0..4])?;
    let month = parse_u32(&s[5..7])?;
    let day = parse_u32(&s[8..10])?;
    let hour = parse_u32(&s[11..13])?;
    let minute = parse_u32(&s[14..16])?;
    let second = parse_u32(&s[17..19])?;
    let off_sign = if b[19] == b'+' { 1 } else { -1 };
    let off_h = parse_u32(&s[20..22])?;
    let off_m = parse_u32(&s[23..25])?;
    if !(1..=12).contains(&month) || day < 1 || day > days_in_month(year, month) {
        return None;
    }
    if hour > 23 || minute > 59 || second > 59 {
        return None;
    }
    if off_h > 14 || off_m > 59 || (off_h == 14 && off_m != 0) {
        return None;
    }
    let days = days_from_civil(year, month, day);
    let local = days * 86400 + hour * 3600 + minute * 60 + second;
    Some(local - off_sign * (off_h * 3600 + off_m * 60))
}

/// Formate des secondes Unix en ISO 8601 UTC avec offset `+00:00`.
/// `recorded_at` est posé en UTC : la règle R10 exige ISO 8601 avec offset
/// et `recorded_at` ≥ `observed_at` — l'offset UTC satisfait les deux, et la
/// comparaison se fait en secondes Unix, indépendante de l'offset.
pub fn format_iso_utc(epoch: i64) -> String {
    let days = epoch.div_euclid(86400);
    let secs = epoch.rem_euclid(86400);
    let (y, m, d) = civil_from_days(days);
    let (hh, mm, ss) = (secs / 3600, (secs % 3600) / 60, secs % 60);
    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}+00:00",
        y, m, d, hh, mm, ss
    )
}

/// Horloge système, en secondes Unix.
pub fn now_unix() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0)
}

// ---------------------------------------------------------------------------
// Validation R10 v1
// ---------------------------------------------------------------------------

/// État du ledger contre lequel un dépôt est validé (union des branches
/// `work-dn*-ledger` — le store unique).
#[derive(Debug, Default, Clone)]
pub struct Ledger {
    /// `entry_id` déjà consignés.
    pub entry_ids: HashSet<String>,
    /// `mission_id` déjà consignés.
    pub mission_ids: HashSet<String>,
}

impl Ledger {
    /// Construit un `Ledger` depuis un JSON `{"entry_ids": [...],
    /// "mission_ids": [...]}` (même forme que la fixture de la suite).
    pub fn from_json(text: &str) -> Result<Ledger, String> {
        let json = parse_json(text)?;
        let mut ledger = Ledger::default();
        if let Some(Json::Arr(ids)) = json.get("entry_ids") {
            for id in ids {
                if let Some(s) = id.as_str() {
                    ledger.entry_ids.insert(s.to_string());
                }
            }
        }
        if let Some(Json::Arr(ids)) = json.get("mission_ids") {
            for id in ids {
                if let Some(s) = id.as_str() {
                    ledger.mission_ids.insert(s.to_string());
                }
            }
        }
        Ok(ledger)
    }
}

/// Résolution d'un SHA complet (commit existant, vérifié au git local ou à
/// l'API — la seule opération qui touche au monde extérieur, et elle est
/// injectée par l'appelant : le validateur lui-même ne fait aucun appel).
pub trait ShaResolver {
    fn resolves(&self, sha: &str) -> bool;
}

/// Résolveur statique (suite de tests, démonstrations) : l'ensemble des
/// SHA connus qui résolvent.
#[derive(Debug, Default, Clone)]
pub struct StaticShaResolver {
    pub shas: HashSet<String>,
}

impl StaticShaResolver {
    pub fn new(shas: impl IntoIterator<Item = String>) -> Self {
        StaticShaResolver {
            shas: shas.into_iter().collect(),
        }
    }
}

impl ShaResolver for StaticShaResolver {
    fn resolves(&self, sha: &str) -> bool {
        self.shas.contains(sha)
    }
}

/// Rejet motivé d'un dépôt mal formé : la règle violée, le champ fautif,
/// la valeur reçue (tronquée si longue), et les autres règles violées
/// dans le même dépôt quand elles sont connues (ex. fautif n° 4 : V7
/// d'abord, V2 nommé aussi).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Rejection {
    pub rule: &'static str,
    pub field: &'static str,
    pub received: String,
    pub detail: String,
    pub also_violated: Vec<&'static str>,
}

impl Rejection {
    fn new(rule: &'static str, field: &'static str, received: &str, detail: &str) -> Self {
        Rejection {
            rule,
            field,
            received: truncate(received, 120),
            detail: detail.to_string(),
            also_violated: Vec::new(),
        }
    }
}

impl fmt::Display for Rejection {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "REJET {} — champ '{}', valeur reçue '{}' : {}",
            self.rule, self.field, self.received, self.detail
        )?;
        if !self.also_violated.is_empty() {
            write!(f, " (aussi violée(s) : {})", self.also_violated.join(", "))?;
        }
        Ok(())
    }
}

fn truncate(s: &str, max: usize) -> String {
    if s.chars().count() > max {
        let t: String = s.chars().take(max).collect();
        format!("{}…", t)
    } else {
        s.to_string()
    }
}

fn describe_value(v: &Json) -> String {
    match v {
        Json::Null => "null".to_string(),
        Json::Bool(b) => format!("booléen {}", b),
        Json::Num(n) => format!("nombre {}", n),
        Json::Str(s) => format!("\"{}\"", truncate(s, 80)),
        Json::Arr(items) => format!("liste de {} entrée(s)", items.len()),
        Json::Obj(pairs) => format!("objet de {} clé(s)", pairs.len()),
    }
}

/// Un dépôt validé (prêt à consigner — `recorded_at` reste à poser).
#[derive(Debug, Clone)]
pub struct ValidDeposit {
    pub entry_id: String,
    pub issuer: String,
    pub mission_id: String,
    pub observed_at: String,
    pub observed_epoch: i64,
    pub proof: Vec<String>,
    pub schema: String,
    pub sha: String,
    pub summary: String,
}

fn valid_entry_id_shape(entry_id: &str) -> bool {
    // G-AAAAAAAA-NNN : 'G', '-', 8 chiffres, '-', 3 chiffres.
    let b = entry_id.as_bytes();
    if b.len() != 14 || b[0] != b'G' || b[1] != b'-' || b[10] != b'-' {
        return false;
    }
    if !b[2..10].iter().all(|c| c.is_ascii_digit()) || !b[11..14].iter().all(|c| c.is_ascii_digit())
    {
        return false;
    }
    let month = parse_u32(&entry_id[6..8]).unwrap_or(0);
    let day = parse_u32(&entry_id[8..10]).unwrap_or(0);
    let year = parse_u32(&entry_id[2..6]).unwrap_or(0);
    (1..=12).contains(&month) && day >= 1 && day <= days_in_month(year, month)
}

/// Nomme-t-on un livrable ? Une référence de PR (`#123`) ou un SHA
/// (suite hexadécimale de 7 à 40 caractères) dans le résumé.
fn summary_names_deliverable(summary: &str) -> bool {
    let bytes = summary.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'#' {
            let mut j = i + 1;
            while j < bytes.len() && bytes[j].is_ascii_digit() {
                j += 1;
            }
            if j > i + 1 {
                return true;
            }
            i = j;
        } else if bytes[i].is_ascii_hexdigit() {
            let mut j = i;
            while j < bytes.len() && bytes[j].is_ascii_hexdigit() {
                j += 1;
            }
            if j - i >= 7 {
                return true;
            }
            i = j;
        } else {
            i += 1;
        }
    }
    false
}

/// Valide un dépôt R10 v1, dans l'ordre V1 → V8 → V7 → V2 → V3 → V4 → V5 → V6.
///
/// `now_unix` est l'horloge de consignation (V4 : `observed_at` ne doit pas
/// être dans le futur). La valeur `recorded_at` du dépôt est ignorée ici :
/// elle est posée par `consign`, jamais reprise.
pub fn validate(
    deposit: &Json,
    ledger: &Ledger,
    resolver: &dyn ShaResolver,
    now_unix: i64,
) -> Result<ValidDeposit, Rejection> {
    // V1 — Format : objet, exactement les 9 clés R10 v1.
    let pairs = match deposit {
        Json::Obj(pairs) => pairs,
        other => {
            return Err(Rejection::new(
                "V1",
                "(dépôt)",
                &describe_value(other),
                "le dépôt doit être un objet JSON",
            ))
        }
    };
    let mut keys: Vec<&str> = pairs.iter().map(|(k, _)| k.as_str()).collect();
    keys.sort_unstable();
    let mut expected = R10_KEYS;
    expected.sort_unstable();
    if keys != expected {
        let mut missing: Vec<&str> = expected
            .iter()
            .filter(|k| !keys.contains(k))
            .copied()
            .collect();
        let mut unknown: Vec<&str> = keys
            .iter()
            .filter(|k| !expected.contains(k))
            .copied()
            .collect();
        missing.sort_unstable();
        unknown.sort_unstable();
        let mut detail = String::new();
        if !missing.is_empty() {
            detail.push_str(&format!("clé(s) manquante(s) : {}", missing.join(", ")));
        }
        if !unknown.is_empty() {
            if !detail.is_empty() {
                detail.push_str(" ; ");
            }
            detail.push_str(&format!("clé(s) inconnue(s) : {}", unknown.join(", ")));
        }
        return Err(Rejection::new(
            "V1",
            "(clés)",
            &format!("{} clé(s) : {}", keys.len(), keys.join(", ")),
            &detail,
        ));
    }

    // V8 — schema exact.
    let schema = match deposit.get("schema") {
        Some(Json::Str(s)) => s.clone(),
        Some(other) => {
            return Err(Rejection::new(
                "V8",
                "schema",
                &describe_value(other),
                "schema doit être la chaîne exacte aspace.r10-receipt.v1",
            ))
        }
        None => unreachable!("V1 garantit la présence de schema"),
    };
    if schema != R10_SCHEMA {
        return Err(Rejection::new(
            "V8",
            "schema",
            &schema,
            "schema doit être exactement aspace.r10-receipt.v1",
        ));
    }

    // V7 — entry_id cohérent et jamais consigné.
    let entry_id = match deposit.get("entry_id") {
        Some(Json::Str(s)) => s.clone(),
        Some(other) => {
            return Err(Rejection::new(
                "V7",
                "entry_id",
                &describe_value(other),
                "entry_id doit être une chaîne G-<date>-<nnn>",
            ))
        }
        None => unreachable!("V1 garantit la présence de entry_id"),
    };
    if !valid_entry_id_shape(&entry_id) {
        return Err(Rejection::new(
            "V7",
            "entry_id",
            &entry_id,
            "entry_id doit avoir la forme G-AAAAMMJJ-NNN (date valide)",
        ));
    }
    if ledger.entry_ids.contains(&entry_id) {
        let mut rejection = Rejection::new(
            "V7",
            "entry_id",
            &entry_id,
            "entry_id déjà consigné — un reçu n'est jamais réécrit",
        );
        // Fautif n° 4 : la réécriture porte aussi le mission_id déjà
        // consigné — V2 est nommé aussi.
        if let Some(Json::Str(m)) = deposit.get("mission_id") {
            if ledger.mission_ids.contains(m) {
                rejection.also_violated.push("V2");
                rejection.detail.push_str(&format!(
                    " ; mission_id '{}' déjà consigné aussi (V2)",
                    m
                ));
            }
        }
        return Err(rejection);
    }

    // V2 — mission_id présent et unique.
    let mission_id = match deposit.get("mission_id") {
        Some(Json::Str(s)) if !s.is_empty() => s.clone(),
        Some(Json::Str(_)) => {
            return Err(Rejection::new(
                "V2",
                "mission_id",
                "\"\"",
                "mission_id ne doit pas être vide",
            ))
        }
        Some(other) => {
            return Err(Rejection::new(
                "V2",
                "mission_id",
                &describe_value(other),
                "mission_id doit être une chaîne non vide",
            ))
        }
        None => unreachable!("V1 garantit la présence de mission_id"),
    };
    if ledger.mission_ids.contains(&mission_id) {
        return Err(Rejection::new(
            "V2",
            "mission_id",
            &mission_id,
            "mission_id déjà consigné — un dépôt par mission",
        ));
    }

    // V3 — sha 40 hex, et le SHA résout.
    let sha = match deposit.get("sha") {
        Some(Json::Str(s)) => s.clone(),
        Some(other) => {
            return Err(Rejection::new(
                "V3",
                "sha",
                &describe_value(other),
                "sha doit être une chaîne de 40 caractères hexadécimaux",
            ))
        }
        None => unreachable!("V1 garantit la présence de sha"),
    };
    if sha.len() != 40 || !sha.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)) {
        return Err(Rejection::new(
            "V3",
            "sha",
            &sha,
            "SHA court ou mal formé — fournir le SHA complet (40 caractères [0-9a-f])",
        ));
    }
    if !resolver.resolves(&sha) {
        return Err(Rejection::new(
            "V3",
            "sha",
            &sha,
            "SHA complet introuvable (ne résout ni au git local ni à l'API)",
        ));
    }

    // V4 — observed_at ISO 8601 avec offset, date valide, pas dans le futur.
    let observed_at = match deposit.get("observed_at") {
        Some(Json::Str(s)) => s.clone(),
        Some(other) => {
            return Err(Rejection::new(
                "V4",
                "observed_at",
                &describe_value(other),
                "observed_at doit être une chaîne ISO 8601 avec offset",
            ))
        }
        None => unreachable!("V1 garantit la présence de observed_at"),
    };
    let observed_epoch = match parse_iso8601_offset(&observed_at) {
        Some(epoch) => epoch,
        None => {
            return Err(Rejection::new(
                "V4",
                "observed_at",
                &observed_at,
                "observed_at doit avoir la forme AAAA-MM-JJTHH:MM:SS±HH:MM (date valide, offset présent)",
            ))
        }
    };
    if observed_epoch > now_unix {
        return Err(Rejection::new(
            "V4",
            "observed_at",
            &observed_at,
            "observed_at est dans le futur par rapport à l'horloge de consignation",
        ));
    }

    // V5 — proof[] non vide, chaque entrée une chaîne non vide.
    let proof = match deposit.get("proof") {
        Some(Json::Arr(items)) => {
            if items.is_empty() {
                return Err(Rejection::new(
                    "V5",
                    "proof",
                    "[]",
                    "proof ne doit pas être vide (au moins 1 entrée vérifiable)",
                ));
            }
            let mut out = Vec::with_capacity(items.len());
            for item in items {
                match item {
                    Json::Str(s) if !s.is_empty() => out.push(s.clone()),
                    _ => {
                        return Err(Rejection::new(
                            "V5",
                            "proof",
                            &describe_value(item),
                            "chaque entrée de proof doit être une chaîne non vide",
                        ))
                    }
                }
            }
            out
        }
        Some(other) => {
            return Err(Rejection::new(
                "V5",
                "proof",
                &describe_value(other),
                "proof doit être une liste d'au moins 1 entrée",
            ))
        }
        None => unreachable!("V1 garantit la présence de proof"),
    };

    // V6 — summary nomme le livrable.
    let summary = match deposit.get("summary") {
        Some(Json::Str(s)) => s.clone(),
        Some(other) => {
            return Err(Rejection::new(
                "V6",
                "summary",
                &describe_value(other),
                "summary doit être une chaîne non vide nommant le livrable",
            ))
        }
        None => unreachable!("V1 garantit la présence de summary"),
    };
    if summary.is_empty() || !summary_names_deliverable(&summary) {
        return Err(Rejection::new(
            "V6",
            "summary",
            &summary,
            "summary doit nommer le livrable de la mission (numéro de PR et/ou SHA du merge)",
        ));
    }

    let issuer = match deposit.get("issuer") {
        Some(Json::Str(s)) => s.clone(),
        _ => String::new(),
    };

    Ok(ValidDeposit {
        entry_id,
        issuer,
        mission_id,
        observed_at,
        observed_epoch,
        proof,
        schema,
        sha,
        summary,
    })
}

/// Consigne un dépôt : le valide, puis pose `recorded_at` à la
/// consignation depuis l'horloge système (UTC, ISO 8601 avec offset) —
/// la valeur `recorded_at` éventuellement présente dans le dépôt est
/// ignorée et remplacée, jamais reprise (D-F1-2-1).
///
/// Retourne le JSON du reçu consigné (une seule ligne, forme du ledger).
/// `now_unix` est l'instant de consignation ; en production, `now_unix()`.
pub fn consign(
    deposit: &Json,
    ledger: &Ledger,
    resolver: &dyn ShaResolver,
    now_unix: i64,
) -> Result<String, Rejection> {
    let valid = validate(deposit, ledger, resolver, now_unix)?;
    let recorded_at = format_iso_utc(now_unix);
    debug_assert!(
        now_unix >= valid.observed_epoch,
        "V4 garantit recorded_at >= observed_at"
    );
    let receipt = Json::Obj(vec![
        ("entry_id".to_string(), Json::Str(valid.entry_id)),
        ("issuer".to_string(), Json::Str(valid.issuer)),
        ("mission_id".to_string(), Json::Str(valid.mission_id)),
        ("observed_at".to_string(), Json::Str(valid.observed_at)),
        (
            "proof".to_string(),
            Json::Arr(valid.proof.into_iter().map(Json::Str).collect()),
        ),
        ("recorded_at".to_string(), Json::Str(recorded_at)),
        ("schema".to_string(), Json::Str(valid.schema)),
        ("sha".to_string(), Json::Str(valid.sha)),
        ("summary".to_string(), Json::Str(valid.summary)),
    ]);
    Ok(receipt.to_compact())
}

/// Nom du fichier de destination d'un reçu dans le ledger.
pub fn receipt_filename(entry_id: &str) -> String {
    format!("ledger/receipts/{}.json", entry_id)
}

#[cfg(test)]
mod unit_tests {
    use super::*;

    #[test]
    fn iso_roundtrip() {
        // 2026-11-11T00:27:43-05:00 = 2026-11-11T05:27:43Z.
        let epoch = parse_iso8601_offset("2026-11-11T00:27:43-05:00").unwrap();
        assert_eq!(format_iso_utc(epoch), "2026-11-11T05:27:43+00:00");
        assert_eq!(parse_iso8601_offset("2026-11-11 00:27:43 EST"), None);
        assert_eq!(parse_iso8601_offset("2026-02-30T00:00:00-05:00"), None);
        assert_eq!(parse_iso8601_offset("2024-02-29T12:00:00+00:00").is_some(), true);
        assert_eq!(parse_iso8601_offset("2026-11-11T00:27:43+00:00").is_some(), true);
    }

    #[test]
    fn json_strings_unicode() {
        let v = parse_json(r#"{"a":"café — été","b":["x\ny"]}"#).unwrap();
        assert_eq!(v.get("a").unwrap().as_str(), Some("café — été"));
        assert_eq!(v.to_compact(), r#"{"a":"café — été","b":["x\ny"]}"#);
    }

    #[test]
    fn entry_id_shape() {
        assert!(valid_entry_id_shape("G-20261111-002"));
        assert!(valid_entry_id_shape("G-20261111-901"));
        assert!(!valid_entry_id_shape("G-20261131-002")); // 31 novembre impossible
        assert!(!valid_entry_id_shape("G-20260230-002")); // 30 février impossible
        assert!(!valid_entry_id_shape("22f374d"));
        assert!(!valid_entry_id_shape("G-20261111-02"));
    }
}
