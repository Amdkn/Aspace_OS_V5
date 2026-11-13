//! Routeur — fonction Router (D-N055 F1-3, Fondation 13 → 1).
//!
//! La fonction Router route un dispatch comme événement du journal, sans
//! Nardole comme session séparée. Ce module est le contrôle déterministe :
//! il valide un dispatch avant typage, l'inscrit dans le journal
//! d'événements (JSONL, append-only — une ligne = un événement, le numéro
//! de séquence = le numéro de ligne), et inscrit le relais comme événement
//! lu par sa destinataire.
//!
//! Règles (Discover F1-3 §4), appliquées dans l'ordre
//! R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 :
//! * R1 — le dispatch est un objet JSON portant exactement les 9 clés
//!   (la 10e, `seq`, est assignée par le routeur à l'inscription — le
//!   numéro de séquence est le numéro de ligne, il ne peut pas être dans
//!   la soumission ; correction portée en avant, voir la fiche §7).
//! * R2 — `design_ref` non vide et nommant un design signé existant
//!   (injecté par l'appelant, comme le résolveur de SHA du validateur).
//! * R3 — `dispatch_id` unique pour un `dispatch_typed` (jamais re-typé) ;
//!   `event_id` unique dans le journal.
//! * R4 — `actor_to` est une fonction du 1 (mapping D2), jamais une session.
//! * R5 — `at` ISO 8601 avec offset, date valide, pas dans le futur.
//! * R6 — `payload` nomme l'acte (au moins un verbe + un objet).
//! * R7 — `proof[]` non vide pour `dispatch_ack` et `judgment_rendered`.
//! * R8 — `type` connu et transition légale (ack/relayed après typed ;
//!   rendered après requested ; correction référence un événement existant).
//!   Correction portée en avant (fiche §7) : le relais suit tout acte de
//!   création du dispatch — `dispatch_typed` OU `judgment_requested` —
//!   car une demande de jugement est elle-même un dispatch (même garanties
//!   : design_ref, payload, preuve). L'accusé, lui, suit seulement le
//!   typage d'un dispatch de livraison.
//!
//! Un dispatch mal formé est rejeté avec sa raison nommée — jamais corrigé
//! silencieusement, jamais routé quand même (D-F1-3-4).
//!
//! Zéro dépendance externe, zéro appel sortant : la liste des designs
//! signés est injectée par l'appelant (`DesignResolver`) ; la seule horloge
//! lue est l'horloge système, pour `at` et la vérification R5.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Router).

use super::{
    days_in_month, format_iso_utc, now_unix, parse_iso8601_offset, parse_json, Json, Rejection,
};
use std::collections::HashSet;

/// Les 9 clés du dispatch soumis (la 10e, `seq`, est assignée à
/// l'inscription — voir l'en-tête du module).
pub const DISPATCH_KEYS: [&str; 9] = [
    "actor_from",
    "actor_to",
    "at",
    "design_ref",
    "dispatch_id",
    "event_id",
    "payload",
    "proof",
    "type",
];

/// Les 15 types d'événements du journal (Discover F1-3 §3, + `closure_pulse`
/// légalisé A-F1-5-3, + `merge_executed` légalisé A-F1-6-4, + `fact_recalled`
/// légalisé A-F1-7-3, + `vision_held` légalisé A-F1-8-3, + `action_taken`
/// légalisé A-F1-9-3, + `rollback_decided` et `rollback_executed` légalisés
/// A-F1-10-3, + `proof_rendered` légalisé A-F1-11-2).
pub const EVENT_TYPES: [&str; 15] = [
    "action_taken",
    "closure_pulse",
    "correction",
    "dispatch_ack",
    "dispatch_relayed",
    "dispatch_typed",
    "fact_recalled",
    "judgment_rendered",
    "judgment_requested",
    "merge_executed",
    "proof_rendered",
    "pulse",
    "rollback_decided",
    "rollback_executed",
    "vision_held",
];

/// Les 13 fonctions, sans doublon, dans l'ordre du mapping D2.
pub const FUNCTIONS_13: [&str; 13] = [
    "structurer",
    "judge",
    "executor",
    "router",
    "receiver",
    "verifier",
    "decider",
    "discoverer",
    "observer",
    "interfacer",
    "fluer",
    "memorizer",
    "fabricator",
];

fn is_function(name: &str) -> bool {
    FUNCTIONS_13.contains(&name)
}

/// État du journal contre lequel un dispatch est validé (lu depuis le
/// fichier JSONL — le journal est la source, pas une copie).
#[derive(Debug, Default, Clone)]
pub struct Journal {
    /// Nombre de lignes du journal (le prochain `seq` est `lines + 1`).
    pub lines: usize,
    /// `dispatch_id` déjà typés (`dispatch_typed` inscrit).
    pub typed: HashSet<String>,
    /// `dispatch_id` pour lesquels un `judgment_requested` est inscrit.
    pub requested: HashSet<String>,
    /// `dispatch_id` pour lesquels un `rollback_decided` est inscrit
    /// (A-F1-10-3 : la reprise rendue suit la décision, elle ne la
    /// précède pas ; un retour n'est décidé qu'une fois).
    pub decided: HashSet<String>,
    /// `event_id` déjà inscrits.
    pub event_ids: HashSet<String>,
}

impl Journal {
    /// Reconstruit l'état depuis un texte JSONL (une ligne = un événement).
    /// Une ligne vide finale est ignorée ; une ligne mal formée est une
    /// erreur (le journal ne se répare pas silencieusement).
    pub fn from_jsonl(text: &str) -> Result<Journal, String> {
        let mut journal = Journal::default();
        for (i, line) in text.lines().enumerate() {
            if line.trim().is_empty() {
                continue;
            }
            let json = parse_json(line)
                .map_err(|e| format!("ligne {} du journal : JSON invalide : {}", i + 1, e))?;
            journal.lines += 1;
            let event_id = json
                .get("event_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let dispatch_id = json
                .get("dispatch_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let typ = json
                .get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            if !event_id.is_empty() {
                journal.event_ids.insert(event_id);
            }
            match typ {
                "dispatch_typed" => {
                    journal.typed.insert(dispatch_id);
                }
                "judgment_requested" => {
                    journal.requested.insert(dispatch_id);
                }
                "rollback_decided" => {
                    journal.decided.insert(dispatch_id);
                }
                _ => {}
            }
        }
        Ok(journal)
    }

    /// Le `seq` du prochain événement (numéro de ligne).
    pub fn next_seq(&self) -> usize {
        self.lines + 1
    }
}

/// Résolution d'un design signé (le design existe et est signé — vérifié par
/// l'opérateur ; la seule opération qui touche au monde extérieur, et elle
/// est injectée par l'appelant : le routeur lui-même ne fait aucun appel).
pub trait DesignResolver {
    fn is_signed(&self, design_ref: &str) -> bool;
}

/// Résolveur statique (suite de tests, démonstrations) : l'ensemble des
/// designs signés connus.
#[derive(Debug, Default, Clone)]
pub struct StaticDesignResolver {
    pub designs: HashSet<String>,
}

impl StaticDesignResolver {
    pub fn new(designs: impl IntoIterator<Item = String>) -> Self {
        StaticDesignResolver {
            designs: designs.into_iter().collect(),
        }
    }
}

impl DesignResolver for StaticDesignResolver {
    fn is_signed(&self, design_ref: &str) -> bool {
        self.designs.contains(design_ref)
    }
}

/// Un dispatch validé, prêt à inscrire (`seq` reste à assigner).
#[derive(Debug, Clone)]
pub struct ValidDispatch {
    pub event_id: String,
    pub typ: String,
    pub dispatch_id: String,
    pub actor_from: String,
    pub actor_to: String,
    pub at: String,
    pub design_ref: String,
    pub payload: String,
    pub proof: Vec<String>,
}

fn rejection(
    rule: &'static str,
    field: &'static str,
    received: &str,
    detail: &str,
) -> Rejection {
    Rejection {
        rule,
        field,
        received: received.chars().take(120).collect(),
        detail: detail.to_string(),
        also_violated: Vec::new(),
    }
}

fn valid_event_id_shape(event_id: &str) -> bool {
    // EVT-AAAAAAAA-NNN : 'EVT', '-', 8 chiffres, '-', 3 chiffres (16 car.).
    let b = event_id.as_bytes();
    if b.len() != 16 || b[0] != b'E' || b[1] != b'V' || b[2] != b'T' || b[3] != b'-'
        || b[12] != b'-'
    {
        return false;
    }
    if b[4..12].iter().all(|c| c.is_ascii_digit())
        && b[13..16].iter().all(|c| c.is_ascii_digit())
    {
        // Date valide (30 février impossible, comme pour entry_id).
        let year: i64 = event_id[4..8].parse().unwrap_or(0);
        let month: i64 = event_id[8..10].parse().unwrap_or(0);
        let day: i64 = event_id[10..12].parse().unwrap_or(0);
        (1..=12).contains(&month) && day >= 1 && day <= days_in_month(year, month)
    } else {
        false
    }
}

/// `payload` nomme-t-il l'acte ? Au moins un verbe + un objet (deux mots).
fn payload_names_act(payload: &str) -> bool {
    let words: Vec<&str> = payload.split_whitespace().collect();
    words.len() >= 2
}

/// Valide un dispatch, dans l'ordre R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8.
pub fn validate_dispatch(
    dispatch: &Json,
    journal: &Journal,
    designs: &dyn DesignResolver,
    now_unix: i64,
) -> Result<ValidDispatch, Rejection> {
    // R1 — Format : objet, exactement les 9 clés du dispatch.
    let pairs = match dispatch {
        Json::Obj(pairs) => pairs,
        other => {
            return Err(rejection(
                "R1",
                "(dispatch)",
                &format!("{:?}", other),
                "le dispatch doit être un objet JSON",
            ))
        }
    };
    let mut keys: Vec<&str> = pairs.iter().map(|(k, _)| k.as_str()).collect();
    keys.sort_unstable();
    let mut expected = DISPATCH_KEYS;
    expected.sort_unstable();
    if keys != expected {
        let missing: Vec<&str> = expected
            .iter()
            .filter(|k| !keys.contains(k))
            .copied()
            .collect();
        let unknown: Vec<&str> = keys
            .iter()
            .filter(|k| !expected.contains(k))
            .copied()
            .collect();
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
        // `seq` dans la soumission est une clé inconnue : elle est assignée
        // par le routeur à l'inscription, jamais soumise.
        return Err(rejection(
            "R1",
            "(clés)",
            &format!("{} clé(s) : {}", keys.len(), keys.join(", ")),
            &detail,
        ));
    }

    let str_field = |key: &'static str| -> Result<String, Rejection> {
        match dispatch.get(key) {
            Some(Json::Str(s)) => Ok(s.clone()),
            Some(other) => Err(rejection(
                "R1",
                key,
                &format!("{:?}", other),
                "le champ doit être une chaîne",
            )),
            None => unreachable!("R1 garantit la présence des 9 clés"),
        }
    };

    let event_id = str_field("event_id")?;
    let typ = str_field("type")?;
    let dispatch_id = str_field("dispatch_id")?;
    let actor_from = str_field("actor_from")?;
    let actor_to = str_field("actor_to")?;
    let at = str_field("at")?;
    let design_ref = str_field("design_ref")?;
    let payload = str_field("payload")?;
    let proof = match dispatch.get("proof") {
        Some(Json::Arr(items)) => {
            let mut out = Vec::with_capacity(items.len());
            for item in items {
                match item {
                    Json::Str(s) => out.push(s.clone()),
                    _ => {
                        return Err(rejection(
                            "R7",
                            "proof",
                            &format!("{:?}", item),
                            "chaque entrée de proof doit être une chaîne",
                        ))
                    }
                }
            }
            out
        }
        Some(_) => {
            return Err(rejection(
                "R7",
                "proof",
                "non-liste",
                "proof doit être une liste (éventuellement vide)",
            ))
        }
        None => unreachable!("R1 garantit la présence de proof"),
    };

    // R2 — Design signé référencé.
    if design_ref.trim().is_empty() {
        return Err(rejection(
            "R2",
            "design_ref",
            &design_ref,
            "aucun design signé référencé — un dispatch sans design signé n'est jamais routé",
        ));
    }
    if !designs.is_signed(&design_ref) {
        return Err(rejection(
            "R2",
            "design_ref",
            &design_ref,
            "le design référencé n'est pas un design signé connu",
        ));
    }

    // R3 — `dispatch_id` unique pour un `dispatch_typed` ; `event_id` unique.
    if !valid_event_id_shape(&event_id) {
        return Err(rejection(
            "R3",
            "event_id",
            &event_id,
            "event_id doit avoir la forme EVT-AAAAMMJJ-NNN",
        ));
    }
    if journal.event_ids.contains(&event_id) {
        return Err(rejection(
            "R3",
            "event_id",
            &event_id,
            "event_id déjà inscrit au journal — un événement n'est jamais réécrit",
        ));
    }
    if typ == "dispatch_typed" && journal.typed.contains(&dispatch_id) {
        return Err(rejection(
            "R3",
            "dispatch_id",
            &dispatch_id,
            "dispatch_id déjà typé — un dispatch n'est jamais typé deux fois (pas de double-envoi)",
        ));
    }

    // R4 — Destinataire = fonction, jamais session.
    if !is_function(&actor_to) {
        return Err(rejection(
            "R4",
            "actor_to",
            &actor_to,
            "le destinataire doit être une fonction du 1 (mapping D2) — jamais une session",
        ));
    }
    if !is_function(&actor_from) {
        return Err(rejection(
            "R4",
            "actor_from",
            &actor_from,
            "l'émetteur doit être une fonction du 1 (mapping D2) — jamais une session",
        ));
    }

    // R5 — `at` ISO 8601 avec offset, date valide, pas dans le futur.
    let at_epoch = match parse_iso8601_offset(&at) {
        Some(epoch) => epoch,
        None => {
            return Err(rejection(
                "R5",
                "at",
                &at,
                "at doit avoir la forme AAAA-MM-JJTHH:MM:SS±HH:MM (date valide, offset présent)",
            ))
        }
    };
    if at_epoch > now_unix {
        return Err(rejection(
            "R5",
            "at",
            &at,
            "at est dans le futur par rapport à l'horloge d'inscription",
        ));
    }

    // R6 — `payload` nomme l'acte.
    if payload.trim().is_empty() || !payload_names_act(&payload) {
        return Err(rejection(
            "R6",
            "payload",
            &payload,
            "payload doit nommer l'acte à exécuter (au moins un verbe + un objet)",
        ));
    }

    // R7 — `proof[]` non vide pour `dispatch_ack` et `judgment_rendered`.
    if (typ == "dispatch_ack" || typ == "judgment_rendered")
        && (proof.is_empty() || proof.iter().any(|p| p.is_empty()))
    {
        return Err(rejection(
            "R7",
            "proof",
            &format!("liste de {} entrée(s)", proof.len()),
            "proof ne doit pas être vide pour un accusé ou un jugement rendu (au moins 1 entrée vérifiable non vide)",
        ));
    }

    // R8 — Type connu et transition légale.
    if !EVENT_TYPES.contains(&typ.as_str()) {
        return Err(rejection(
            "R8",
            "type",
            &typ,
            "type inconnu — l'un des 14 types du journal (Discover F1-3 §3, + `closure_pulse` A-F1-5-3, + `merge_executed` A-F1-6-4, + `fact_recalled` A-F1-7-3, + `vision_held` A-F1-8-3, + `action_taken` A-F1-9-3, + `rollback_decided` et `rollback_executed` A-F1-10-3)",
        ));
    }
    match typ.as_str() {
        "dispatch_relayed" => {
            // Le relais suit tout acte de création du dispatch : un typage
            // ou une demande de jugement (correction portée en avant, fiche
            // §7 — une demande de jugement est elle-même un dispatch).
            if !journal.typed.contains(&dispatch_id)
                && !journal.requested.contains(&dispatch_id)
            {
                return Err(rejection(
                    "R8",
                    "dispatch_id",
                    &dispatch_id,
                    "aucun dispatch_typed ni judgment_requested pour ce dispatch_id — le relais suit l'acte qu'il relaie, il ne le précède pas",
                ));
            }
        }
        "dispatch_ack" => {
            if !journal.typed.contains(&dispatch_id) {
                return Err(rejection(
                    "R8",
                    "dispatch_id",
                    &dispatch_id,
                    "aucun dispatch_typed pour ce dispatch_id — l'accusé suit le typage d'un dispatch de livraison, il ne le précède pas",
                ));
            }
        }
        "judgment_rendered" => {
            if !journal.requested.contains(&dispatch_id) {
                return Err(rejection(
                    "R8",
                    "dispatch_id",
                    &dispatch_id,
                    "aucun judgment_requested pour ce dispatch_id — le jugement rendu suit la demande, il ne la précède pas",
                ));
            }
        }
        "rollback_decided" => {
            if journal.decided.contains(&dispatch_id) {
                return Err(rejection(
                    "R8",
                    "dispatch_id",
                    &dispatch_id,
                    "un retour n'est décidé qu'une fois — un second rollback_decided pour ce dispatch_id est une seconde décision pour un seul retour",
                ));
            }
        }
        "rollback_executed" => {
            if !journal.decided.contains(&dispatch_id) {
                return Err(rejection(
                    "R8",
                    "dispatch_id",
                    &dispatch_id,
                    "aucun rollback_decided pour ce dispatch_id — la reprise rendue suit la décision, elle ne la précède pas",
                ));
            }
        }
        "correction" => {
            // Le payload nomme l'événement corrigé : « corrige EVT-… ».
            let target = payload
                .split_whitespace()
                .find(|w| w.starts_with("EVT-"))
                .unwrap_or("");
            if target.is_empty() || !journal.event_ids.contains(target) {
                return Err(rejection(
                    "R8",
                    "payload",
                    &payload,
                    "une correction nomme l'événement corrigé (« corrige EVT-AAAAMMJJ-NNN ») et cet événement doit exister au journal",
                ));
            }
        }
        _ => {}
    }

    Ok(ValidDispatch {
        event_id,
        typ,
        dispatch_id,
        actor_from,
        actor_to,
        at,
        design_ref,
        payload,
        proof,
    })
}

/// Inscrit un dispatch validé : le valide, puis assigne `seq` (numéro de
/// ligne = `journal.lines + 1`) et retourne la ligne JSONL à ajouter au
/// journal (append-only). `now_unix` est l'instant d'inscription ; en
/// production, `now_unix()`.
pub fn inscribe(
    dispatch: &Json,
    journal: &Journal,
    designs: &dyn DesignResolver,
    now_unix: i64,
) -> Result<String, Rejection> {
    let valid = validate_dispatch(dispatch, journal, designs, now_unix)?;
    let seq = journal.next_seq();
    let event = Json::Obj(vec![
        ("seq".to_string(), Json::Num(seq.to_string())),
        ("event_id".to_string(), Json::Str(valid.event_id)),
        (
            "type".to_string(),
            Json::Str(valid.typ.clone()),
        ),
        (
            "dispatch_id".to_string(),
            Json::Str(valid.dispatch_id),
        ),
        (
            "actor_from".to_string(),
            Json::Str(valid.actor_from),
        ),
        ("actor_to".to_string(), Json::Str(valid.actor_to)),
        ("at".to_string(), Json::Str(valid.at)),
        (
            "design_ref".to_string(),
            Json::Str(valid.design_ref),
        ),
        ("payload".to_string(), Json::Str(valid.payload)),
        (
            "proof".to_string(),
            Json::Arr(valid.proof.into_iter().map(Json::Str).collect()),
        ),
    ]);
    Ok(event.to_compact())
}

/// Horodatage d'inscription, en ISO 8601 UTC avec offset (+00:00) — même
/// choix que le consignateur R10 (F1-2) : la comparaison se fait en
/// secondes Unix, indépendante de l'offset.
pub fn now_iso() -> String {
    format_iso_utc(now_unix())
}

#[cfg(test)]
mod unit_tests {
    use super::*;

    #[test]
    fn event_id_shape() {
        assert!(valid_event_id_shape("EVT-20261111-001"));
        assert!(!valid_event_id_shape("EVT-20261111-01"));
        assert!(!valid_event_id_shape("G-20261111-001"));
        assert!(!valid_event_id_shape("EVT-20260230-001"));
    }

    #[test]
    fn payload_names_act_rule() {
        assert!(payload_names_act("Ouvrir la PR F1-3"));
        assert!(!payload_names_act("ouvrir"));
        assert!(!payload_names_act(""));
    }

    #[test]
    fn functions_are_thirteen() {
        assert_eq!(FUNCTIONS_13.len(), 13);
        assert!(is_function("judge"));
        assert!(is_function("executor"));
        assert!(!is_function("Nardole"));
        assert!(!is_function("ae7d36d1"));
    }

    #[test]
    fn journal_rebuilds_state() {
        let text = "{\"seq\":1,\"event_id\":\"EVT-20261111-001\",\"type\":\"dispatch_typed\",\"dispatch_id\":\"D-N055-F1-3-DELIVER\",\"actor_from\":\"router\",\"actor_to\":\"executor\",\"at\":\"2026-11-11T01:55:00-05:00\",\"design_ref\":\"design\",\"payload\":\"Ouvrir la PR F1-3\",\"proof\":[]}\n{\"seq\":2,\"event_id\":\"EVT-20261111-002\",\"type\":\"judgment_requested\",\"dispatch_id\":\"D-N055-F1-3-JUDGE\",\"actor_from\":\"router\",\"actor_to\":\"judge\",\"at\":\"2026-11-11T01:56:00-05:00\",\"design_ref\":\"design\",\"payload\":\"Demander le jugement\",\"proof\":[]}\n";
        let journal = Journal::from_jsonl(text).unwrap();
        assert_eq!(journal.lines, 2);
        assert_eq!(journal.next_seq(), 3);
        assert!(journal.typed.contains("D-N055-F1-3-DELIVER"));
        assert!(journal.requested.contains("D-N055-F1-3-JUDGE"));
        assert!(journal.event_ids.contains("EVT-20261111-001"));
    }
}
