//! Mémoire — fonction Mémoriser (D-N055 F1-7, Fondation 13 → 1).
//!
//! La fonction Mémoriser cite un fait des 13 mémoires, sans Graham comme
//! session séparée. Elle EST la citation (D-F1-7-7) : il n'y a pas de
//! contrôle de recevabilité séparé avant un acte tiers — la citation
//! rendue EST l'acte. Un fait = (énoncé, source exacte, date, statut) —
//! les 4 champs, tous obligatoires, tous vérifiés contre la source au
//! fichier au moment de la citation ; la source est le chemin exact +
//! la ligne, relue quand la citation est rendue, jamais reprise de
//! l'inventaire F1-0 (texte tronqué à 200 car., pointeur possiblement
//! périmé) ni d'un résultat de recherche antérieur ; la date est celle
//! que porte la source (avec son fuseau quand elle en a un), ou
//! « inconnue », jamais inférée ; le statut est l'un des six
//! (`vérifié` / `consigné` / `périmé` / `contredit` / `absent` /
//! `à venir`) et il est justifié par la source ; les corroborations et
//! les contradictions sont listées, une par ligne, avec leurs dates et
//! statuts ; chaque limite est nommée (« ce que cette citation ne
//! prouve pas ») ; jamais de texte repris de l'inventaire tronqué comme
//! si c'était le fait entier (D-F1-7-1).
//!
//! Règles (Discover F1-7 §3.7), appliquées dans l'ordre
//! M1 → M7 → M2 → M3 → M4 → M5 → M6 → M8 (du moins cher au plus cher) :
//! * M1 — en-tête complet (fonction, date de la citation, fait demandé,
//!   mécanisme) + section Citation portant les 4 champs + les quatre
//!   sections (Vérification au fichier, Corroborations et contradictions,
//!   Ce que cette citation ne prouve pas, Ce que la fonction n'a pas fait).
//! * M7 — la mémoire ne juge pas : la section « Ce que la fonction n'a
//!   pas fait » est présente et non vide, et aucun marqueur de jugement
//!   non nié (« verdict », « tranche », « consigne un reçu », « écrit au
//!   registre », « corrige silencieusement ») n'apparaît dans le dossier.
//! * M2 — source exacte = source vérifiée : la source existe et la ligne
//!   relue au fichier porte l'énoncé (sauf statut `absent` : la source
//!   n'existe pas et l'absence est nommée dans la Vérification —
//!   condition 4 de D-F1-7-2, une absence tue vaut un échec).
//! * M3 — date portée par la source : la date citée est celle que porte
//!   la ligne relue, ou celle du fichier (note quotidienne), ou
//!   « inconnue » — jamais inférée.
//! * M4 — statut sourcé : l'un des six, justifié — `contredit` exige des
//!   corroborations ; `absent` exige une source absente ; `à venir`
//!   exige une date après la citation ; `périmé` exige une date avant la
//!   citation et le déplacement nommé dans la Vérification.
//! * M5 — contradiction portée : si une corroboration relue porte une
//!   date différente de la date citée, le statut est `contredit` et la
//!   version divergente est listée — jamais une version choisie
//!   silencieusement.
//! * M6 — fautif planté rejeté : la citation n'est pas le fait fautif
//!   planté (énoncé, source, date) injecté par l'appelant. Le fautif
//!   F-X1 (date 2027-10-08 au lieu de 2027-10-09) est rejeté M3 avant
//!   d'atteindre M6 — M6 est le filet qui attrape un fautif qui aurait
//!   passé M1–M5.
//! * M8 — limites nommées : la section « Ce que cette citation ne
//!   prouve pas » est présente et non vide.
//!
//! M2/M3 sont les seuls qui touchent au fichier au moment de la citation
//! (D-F1-7-7) : la ligne source et la date de la source sont injectées
//! par l'appelant, qui les a relues au fichier. La recherche sémantique
//! n'est pas le mécanisme (A-F1-7-5) : elle reste un outil d'exploration
//! du producteur, jamais la source de citation du mécanisme — le mécanisme
//! lit un index re-compilé et relit la source au fichier.
//!
//! Une citation mal formée est rejetée avec sa règle nommée — jamais
//! corrigée silencieusement, jamais citée quand même (D-F1-7-6 : une
//! mémoire qui cite une date qu'elle n'a pas vérifiée n'est pas une
//! mémoire, c'est une rumeur datée).
//!
//! Zéro dépendance externe, zéro appel sortant : la ligne source, la date
//! de la source, les corroborations et le fautif planté sont injectés par
//! l'appelant ; la fonction ne contacte ni le fichier local ni l'API
//! elle-même.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Mémoriser).

use super::Rejection;

/// Les six statuts qu'une citation peut porter (D-F1-7-1, Discover §5.1).
pub const STATUSES: [&str; 6] = [
    "vérifié",
    "consigné",
    "périmé",
    "contredit",
    "absent",
    "à venir",
];

/// Une corroboration (ou contradiction) relue au fichier par l'appelant :
/// (source exacte, date du fait dans cette source, statut).
pub type Corroboration<'a> = (&'a str, &'a str, &'a str);

/// Ce que l'appelant a vérifié au fichier au moment de la citation.
/// M2/M3 sont les seuls contrôles qui touchent au fichier — tout est
/// injecté ici, la fonction ne lit rien elle-même.
pub struct CitationEvidence<'a> {
    /// La source citée existe-t-elle au fichier ?
    pub source_exists: bool,
    /// La ligne source, relue au fichier au moment de la citation.
    pub source_line_text: &'a str,
    /// La date que porte la source : celle de la ligne, ou celle du
    /// fichier (note quotidienne) quand la ligne n'en porte pas.
    pub source_date: &'a str,
    /// Les corroborations (et contradictions) relues au fichier.
    pub corroborations: &'a [Corroboration<'a>],
    /// Le fait fautif planté (énoncé, source, date), lu dans le dossier
    /// fautif par l'appelant. `None` = aucun fautif injecté (M6 passe).
    pub planted_fautif: Option<(&'a str, &'a str, &'a str)>,
}

/// Une citation acceptée : ses 4 champs, vérifiés au fichier.
#[derive(Debug)]
pub struct ValidCitation {
    /// L'énoncé, tel que la source le porte.
    pub statement: String,
    /// La source exacte (chemin + ligne).
    pub source: String,
    /// La date portée par la source (ou « inconnue »).
    pub date: String,
    /// Le statut, l'un des six.
    pub status: String,
}

/// Le préfixe `AAAA-MM-JJ` d'une date, quand elle en porte un.
fn date_prefix(date: &str) -> Option<&str> {
    let bytes = date.as_bytes();
    if bytes.len() >= 10
        && bytes[4] == b'-'
        && bytes[7] == b'-'
        && bytes[..4].iter().all(|b| b.is_ascii_digit())
        && bytes[5..7].iter().all(|b| b.is_ascii_digit())
        && bytes[8..10].iter().all(|b| b.is_ascii_digit())
    {
        Some(&date[..10])
    } else {
        None
    }
}

/// La section `## ...` dont le titre contient `keyword` (patron F1-6).
fn section_named<'a>(text: &'a str, keyword: &str) -> &'a str {
    let mut start: Option<usize> = None;
    let mut end = text.len();
    let mut pos = 0usize;
    for line in text.split_inclusive('\n') {
        if line.starts_with("## ") {
            if start.is_some() {
                end = pos;
                break;
            }
            if line[3..].contains(keyword) {
                start = Some(pos);
            }
        }
        pos += line.len();
    }
    match start {
        Some(s) => &text[s..end],
        None => "",
    }
}

/// Le champ `**Nom :** valeur` dans une section (première ligne qui
/// commence par le marqueur) — la valeur est le reste de la ligne.
fn field_in<'a>(section: &'a str, marker: &str) -> Option<&'a str> {
    for line in section.lines() {
        if let Some(rest) = line.strip_prefix(marker) {
            return Some(rest.trim());
        }
    }
    None
}

/// La négation est limitée à la ligne du marqueur (patron F1-5/F1-6) :
/// un marqueur précédé sur sa ligne de « ne », « ni », « pas », « aucun »,
/// « rien », « sans » ou « jamais » est une dénégation, pas un acte.
fn denied_before(text: &str, idx: usize) -> bool {
    let line_start = text[..idx].rfind('\n').map(|i| i + 1).unwrap_or(0);
    let before = &text[line_start..idx];
    before.contains("Aucun")
        || before.contains("aucun")
        || before.contains("ne ")
        || before.contains("Ni ")
        || before.contains("ni ")
        || before.contains("pas ")
        || before.contains("rien")
        || before.contains("Rien")
        || before.contains("sans ")
        || before.contains("jamais")
}

/// Les espaces collapsés (un seul espace entre les mots) — la comparaison
/// d'un énoncé à sa ligne source ne dépend pas de la mise en forme.
fn normalize(text: &str) -> String {
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// Les marqueurs d'un jugement rendu par la mémoire (M7). La mémoire
/// porte la contradiction, elle ne tranche pas (D-F1-7-11d).
const JUDGMENT_MARKERS: [&str; 5] = [
    "verdict",
    "tranche",
    "consigne un reçu",
    "écrit au registre",
    "corrige silencieusement",
];

/// Les marqueurs d'un déplacement de source (M4, statut `périmé`) :
/// le pointeur a bougé, la citation le signale et re-résout.
const MOVED_MARKERS: [&str; 4] = ["périmé", "bougée", "re-résol", "déplacée"];

/// M1 — en-tête complet + section Citation portant les 4 champs + les
/// quatre sections de la forme §3.6. Retourne les 4 champs extraits.
fn m1_citation_fields(citation: &str) -> Result<(String, String, String, String), Rejection> {
    for (marker, detail) in [
        ("**Fonction :**", "fonction"),
        ("**Date de la citation :**", "date de la citation"),
        ("**Fait demandé :**", "fait demandé"),
        ("**Mécanisme :**", "mécanisme"),
    ] {
        if !citation.contains(marker) {
            return Err(Rejection::new(
                "M1",
                "en-tête",
                "absent",
                &format!("en-tête incomplet : {} manquant", detail),
            ));
        }
    }
    let section = section_named(citation, "Citation");
    if section.is_empty() {
        return Err(Rejection::new(
            "M1",
            "citation",
            "section Citation absente",
            "la forme §3.6 exige l'en-tête, la citation et les quatre sections",
        ));
    }
    let statement = field_in(section, "**Énoncé :**").ok_or_else(|| {
        Rejection::new(
            "M1",
            "énoncé",
            "absent",
            "champ « Énoncé » manquant dans la section Citation",
        )
    })?;
    let source = field_in(section, "**Source :**").ok_or_else(|| {
        Rejection::new(
            "M1",
            "source",
            "absent",
            "champ « Source » manquant dans la section Citation",
        )
    })?;
    let date = field_in(section, "**Date :**").ok_or_else(|| {
        Rejection::new(
            "M1",
            "date",
            "absent",
            "champ « Date » manquant dans la section Citation",
        )
    })?;
    let status = field_in(section, "**Statut :**").ok_or_else(|| {
        Rejection::new(
            "M1",
            "statut",
            "absent",
            "champ « Statut » manquant dans la section Citation",
        )
    })?;
    for (keyword, name) in [
        ("Vérification au fichier", "Vérification au fichier"),
        (
            "Corroborations et contradictions",
            "Corroborations et contradictions",
        ),
        (
            "Ce que cette citation ne prouve pas",
            "Ce que cette citation ne prouve pas",
        ),
        (
            "Ce que la fonction n'a pas fait",
            "Ce que la fonction n'a pas fait",
        ),
    ] {
        if section_named(citation, keyword).is_empty() {
            return Err(Rejection::new(
                "M1",
                "section",
                name,
                &format!("section « {name} » absente — la forme §3.6 exige les quatre sections"),
            ));
        }
    }
    Ok((
        statement.to_string(),
        source.to_string(),
        date.to_string(),
        status.to_string(),
    ))
}

/// La date de la citation (ISO entre backticks sur la ligne
/// « Date de la citation ») — sert aux comparaisons M4.
fn citation_iso(citation: &str) -> Option<String> {
    for line in citation.lines() {
        if line.starts_with("**Date de la citation :**") {
            let mut in_tick = false;
            let mut iso = String::new();
            for ch in line.chars() {
                if ch == '`' {
                    if in_tick {
                        return Some(iso);
                    }
                    in_tick = true;
                } else if in_tick {
                    iso.push(ch);
                }
            }
        }
    }
    None
}

/// M7 — la mémoire ne juge pas.
fn m7_no_judgment(citation: &str) -> Result<(), Rejection> {
    let section = section_named(citation, "Ce que la fonction n'a pas fait");
    let body_lines = section
        .lines()
        .skip(1)
        .filter(|l| !l.trim().is_empty())
        .count();
    if body_lines == 0 {
        return Err(Rejection::new(
            "M7",
            "ce que la fonction n'a pas fait",
            "section vide",
            "section « Ce que la fonction n'a pas fait » vide — la mémoire doit dire ce qu'elle n'a pas fait",
        ));
    }
    // Insensible à la casse : un « Verdict » avec capitale est un verdict
    // (leçon F1-5 : le module ne doit pas laisser passer une capitale).
    let lowered = citation.to_lowercase();
    for marker in JUDGMENT_MARKERS {
        let mut search_from = 0usize;
        while let Some(rel) = lowered[search_from..].find(marker) {
            let idx = search_from + rel;
            if !denied_before(&lowered, idx) {
                return Err(Rejection::new(
                    "M7",
                    "jugement",
                    marker,
                    "marqueur de jugement non nié — la mémoire porte la contradiction, elle ne tranche pas",
                ));
            }
            search_from = idx + marker.len();
        }
    }
    Ok(())
}

/// M2 — source exacte = source vérifiée.
fn m2_source_verified(
    statement: &str,
    source: &str,
    status: &str,
    citation: &str,
    evidence: &CitationEvidence,
) -> Result<(), Rejection> {
    if status == "absent" {
        if evidence.source_exists {
            return Err(Rejection::new(
                "M2",
                "source",
                source,
                "statut « absent » mais la source existe — l'absence consignée est fausse",
            ));
        }
        let verification = section_named(citation, "Vérification au fichier");
        if !(verification.contains("absent")
            || verification.contains("0 octet")
            || verification.contains("perdue"))
        {
            return Err(Rejection::new(
                "M2",
                "vérification",
                "absence non nommée",
                "statut « absent » mais l'absence n'est pas nommée dans la Vérification — une absence tue vaut un échec",
            ));
        }
        return Ok(());
    }
    if !evidence.source_exists {
        return Err(Rejection::new(
            "M2",
            "source",
            source,
            "la source citée n'existe pas — la fonction ne retrouve pas un fait dans une mémoire perdue",
        ));
    }
    let line = normalize(evidence.source_line_text);
    let stmt = normalize(statement);
    if !line.contains(&stmt) {
        return Err(Rejection::new(
            "M2",
            "énoncé",
            &stmt,
            "l'énoncé n'est pas celui que porte la ligne source relue — un énoncé altéré n'est pas une preuve",
        ));
    }
    Ok(())
}

/// M3 — date portée par la source.
fn m3_date_from_source(date: &str, evidence: &CitationEvidence) -> Result<(), Rejection> {
    if date == "inconnue" {
        return Ok(());
    }
    if evidence.source_line_text.contains(date)
        || evidence.source_date == date
        || evidence.source_date.contains(date)
    {
        return Ok(());
    }
    Err(Rejection::new(
        "M3",
        "date",
        date,
        &format!(
            "la date citée n'est pas celle que porte la source (la source porte {}) — une mémoire qui cite une date qu'elle n'a pas vérifiée n'est pas une mémoire, c'est une rumeur datée",
            evidence.source_date
        ),
    ))
}

/// M4 — statut sourcé, justifié.
fn m4_status_justified(
    date: &str,
    status: &str,
    citation: &str,
    evidence: &CitationEvidence,
) -> Result<(), Rejection> {
    if !STATUSES.contains(&status) {
        return Err(Rejection::new(
            "M4",
            "statut",
            status,
            "le statut n'est pas l'un des six portés par la source (vérifié / consigné / périmé / contredit / absent / à venir)",
        ));
    }
    match status {
        "contredit" => {
            if evidence.corroborations.is_empty() {
                return Err(Rejection::new(
                    "M4",
                    "statut",
                    "contredit",
                    "statut « contredit » sans corroboration listée — une contradiction sans version nommée n'est pas portée",
                ));
            }
        }
        "absent" => {
            if evidence.source_exists {
                return Err(Rejection::new(
                    "M4",
                    "source",
                    "existe",
                    "statut « absent » mais la source existe — l'absence consignée est fausse",
                ));
            }
        }
        "à venir" | "périmé" => {
            let cited = date_prefix(date).ok_or_else(|| {
                Rejection::new(
                    "M4",
                    "date",
                    date,
                    &format!(
                        "statut « {status} » mais la date citée n'est pas datée — un statut temporel exige une date"
                    ),
                )
            })?;
            let at = citation_iso(citation).ok_or_else(|| {
                Rejection::new(
                    "M4",
                    "date de la citation",
                    "absente",
                    "date de la citation absente de l'en-tête — un statut temporel exige une date de citation",
                )
            })?;
            let today = date_prefix(&at).ok_or_else(|| {
                Rejection::new(
                    "M4",
                    "date de la citation",
                    &at,
                    "date de la citation non datée — un statut temporel exige une date de citation",
                )
            })?;
            if status == "à venir" && cited <= today {
                return Err(Rejection::new(
                    "M4",
                    "date",
                    cited,
                    &format!(
                        "statut « à venir » mais la date citée n'est pas après la citation ({today}) — un fait déjà advenu n'est pas à venir"
                    ),
                ));
            }
            if status == "périmé" && cited >= today {
                return Err(Rejection::new(
                    "M4",
                    "date",
                    cited,
                    &format!(
                        "statut « périmé » mais la date citée n'est pas avant la citation ({today})"
                    ),
                ));
            }
            if status == "périmé" {
                let verification = section_named(citation, "Vérification au fichier");
                if !MOVED_MARKERS.iter().any(|m| verification.contains(m)) {
                    return Err(Rejection::new(
                        "M4",
                        "vérification",
                        "déplacement non nommé",
                        "statut « périmé » mais le déplacement n'est pas nommé dans la Vérification — une source bougée se signale, elle ne se tait pas",
                    ));
                }
            }
        }
        _ => {}
    }
    Ok(())
}

/// M5 — contradiction portée.
fn m5_contradiction_carried(
    date: &str,
    status: &str,
    citation: &str,
    evidence: &CitationEvidence,
) -> Result<(), Rejection> {
    let section = section_named(citation, "Corroborations et contradictions");
    let mut diverging: Vec<&str> = Vec::new();
    for (_, corr_date, _) in evidence.corroborations {
        if *corr_date != date {
            diverging.push(corr_date);
        }
    }
    if diverging.is_empty() {
        return Ok(());
    }
    if status != "contredit" {
        return Err(Rejection::new(
            "M5",
            "statut",
            status,
            &format!(
                "corroboration divergente ({}) mais statut « {status} » — une version choisie sans nommer l'autre est une contradiction lissée, pas une citation",
                diverging.join(", ")
            ),
        ));
    }
    for d in diverging {
        if !section.contains(d) {
            return Err(Rejection::new(
                "M5",
                "corroborations",
                d,
                "version divergente non listée dans les Corroborations — la contradiction doit être portée, pas écrasée",
            ));
        }
    }
    Ok(())
}

/// M6 — fautif planté rejeté.
fn m6_planted_rejected(
    statement: &str,
    source: &str,
    date: &str,
    evidence: &CitationEvidence,
) -> Result<(), Rejection> {
    if let Some((f_stmt, f_src, f_date)) = evidence.planted_fautif {
        if statement == f_stmt && source == f_src && date == f_date {
            return Err(Rejection::new(
                "M6",
                "fait cité",
                "fautif planté",
                "le fait cité est le fait fautif planté — une mémoire qui cite le fautif n'est pas une mémoire",
            ));
        }
    }
    Ok(())
}

/// M8 — limites nommées.
fn m8_limits_named(citation: &str) -> Result<(), Rejection> {
    let section = section_named(citation, "Ce que cette citation ne prouve pas");
    let body: String = section
        .lines()
        .skip(1)
        .filter(|l| !l.trim().is_empty())
        .collect::<Vec<_>>()
        .join("\n");
    if body.trim().is_empty() {
        return Err(Rejection::new(
            "M8",
            "limites",
            "section vide",
            "section « Ce que cette citation ne prouve pas » vide — chaque limite doit être nommée",
        ));
    }
    Ok(())
}

/// Valide une citation selon M1 → M7 → M2 → M3 → M4 → M5 → M6 → M8.
/// La citation rendue EST l'acte (D-F1-7-7) : accepter, c'est citer.
pub fn validate_citation(
    citation: &str,
    evidence: &CitationEvidence,
) -> Result<ValidCitation, Rejection> {
    let (statement, source, date, status) = m1_citation_fields(citation)?;
    m7_no_judgment(citation)?;
    m2_source_verified(&statement, &source, &status, citation, evidence)?;
    m3_date_from_source(&date, evidence)?;
    m4_status_justified(&date, &status, citation, evidence)?;
    m5_contradiction_carried(&date, &status, citation, evidence)?;
    m6_planted_rejected(&statement, &source, &date, evidence)?;
    m8_limits_named(citation)?;
    Ok(ValidCitation {
        statement,
        source,
        date,
        status,
    })
}

/// Les 14 types du journal (A-F1-10-3) : les 12 du routeur (les 7 du
/// design F1-3 + `closure_pulse` légalisé A-F1-5-3 + `merge_executed`
/// légalisé A-F1-6-4 + `fact_recalled` légalisé A-F1-7-3) + `vision_held`
/// (11e, émis par le routeur au rendu d'un état de vision — preuve : les
/// lectures datées + les comparaisons rejouables + les divergences
/// portées avec statut) + `action_taken` (12e, émis par le routeur au
/// rendu d'un acte — preuve : autorisation nommée + acte posé + rapport
/// fait/échoué) + `rollback_decided` (13e, émis par le coordinateur — ou
/// le 13e en secours — au moment de la décision ; preuve : fonction +
/// hold-out + échec simulé nommé + repreneur + checkpoint seq + `event_id`
/// + `at`) + `rollback_executed` (14e, émis par le routeur au rendu de la
/// reprise ; preuve : repreneur + checkpoint + révocation + résultat de
/// la re-preuve) + `proof_rendered` (15e, émis par l'opérateur au rendu
/// de la preuve finale ; preuve : les 10 conditions du Discover §8,
/// vérifiées une à une). Même ordre que `router::EVENT_TYPES`,
/// `fact_recalled`, `vision_held`, `action_taken`, `rollback_decided`,
/// `rollback_executed` et `proof_rendered` insérés à leur place
/// alphabétique.
pub const JOURNAL_EVENT_TYPES: [&str; 15] = [
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
