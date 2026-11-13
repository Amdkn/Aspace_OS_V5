//! Action — fonction Action (D-N055 F1-9, Fondation 13 → 1).
//!
//! La fonction Action agit sans question de clarification préalable quand
//! l'action est autorisée, sans opérateur interrogé ni gate supprimé. Elle
//! EST l'acte (D-F1-9-2) : il n'y a pas de contrôle de recevabilité séparé
//! avant un acte tiers — l'acte rendu EST l'action.
//!
//! Une action est **autorisée** quand son autorisation est nommée avec
//! quatre champs obligatoires (D-F1-9-1) : (a) l'acte autorisé, nommé —
//! un acte non nommé n'est pas autorisé ; (b) l'auteur de l'autorisation
//! (qui autorise, avec son nom de fonction) ; (c) sa date (ISO 8601 avec
//! offset) ; (d) sa source exacte (fichier + ligne/section). Les quatre
//! champs sont vérifiés au fichier au moment de l'acte ; un champ
//! manquant = l'action n'est pas autorisée, elle est seulement faite.
//!
//! Règles (Discover F1-9 §6), appliquées dans l'ordre
//! A1 → A4 → A2 → A3 → A6 → A7 → A5 → A8 (du moins cher au plus cher) :
//! * A1 — Autorisation nommée. Chaque action cite son autorisation (acte
//!   + auteur + date + source exacte). Une action sans autorisation
//!   nommée = rejet (elle n'est pas autorisée, elle est seulement faite).
//! * A4 — Gates préservés. Le design signé, le jugement (E1) quand il est
//!   requis, la vérification post-merge par un tiers (E7) et la séparation
//!   juge/exécutant/consignateur (J7) sont des gates, pas des questions.
//!   Un gate supprimé au nom de H-F1-8 = rejet. A1/A4 sont les seuls qui
//!   touchent aux sources avant l'acte.
//! * A2 — Pas de question préalable quand l'autorisation est complète.
//!   Une autorisation est complète quand elle nomme l'acte, son auteur,
//!   sa date, et que les gates requis sont passés (design signé ;
//!   jugement si requis ; pré-vérifications vertes). Une question posée
//!   alors que l'autorisation est complète = rejet — c'est le fautif
//!   F-A2. Un acte posé sans jugement rendu (F-A1 : merge sans jugement,
//!   ou autorisation d'un autre pas) = rejet A2 : « une autorisation
//!   nomme l'action qu'elle autorise — sans jugement rendu, le merge
//!   n'est pas autorisé ; le design F1-8 n'autorise pas le pas F1-9 ».
//!   Une autorisation ambiguë ne se questionne pas : elle est renvoyée
//!   au juge (renvoi, pas question — D-F1-9-11) et consignée comme telle.
//! * A3 — Exécutée puis rapportée. L'acte est posé, puis rapporté fait
//!   ou échoué, avec sa preuve (merge commit, 2 parents DVG-01 ; reçu
//!   consigné ; événement au journal). Un rapport avant l'acte, ou un
//!   acte sans rapport, ou un acte rapporté fait sans preuve = rejet —
//!   c'est le fautif F-A3 (une action sans preuve n'est pas rapportée,
//!   elle est affirmée).
//! * A6 — L'action ne sort pas de son autorisation. Pas de dépense, pas
//!   d'activation client en direct, pas de saisie de secret, pas de
//!   modification des documents du Capitaine, pas d'acte sur un fait que
//!   lui seul détient (limites dures : Go_Bypass 2026-11-04, mandat
//!   2026-11-09). Un acte hors autorisation = rejet — c'est le fautif
//!   F-A4 (les mandats ne couvrent pas ces actes).
//! * A7 — Absence et échec consignés. Une action non faite, échouée, ou
//!   bloquée (carte du harness en attente, §5.4e) est consignée comme
//!   telle, avec sa cause. Une absence tue = rejet. Une action déjà faite
//!   est constatée « déjà fait » avec sa preuve, jamais re-exécutée
//!   (§5.4c) ; une action partiellement faite reprend où c'était, le
//!   journal portant l'état (§5.4d).
//! * A5 — Fautif planté rejeté (le filet). La fonction doit rejeter le
//!   fait fautif planté par le design (§5.3, F-A1) avec la règle nommée
//!   (A2). Un fautif non rejeté, ou rejeté par la mauvaise règle, = échec
//!   de la fonction — retour aux acteurs d'origine (filet (a), plan §D5).
//!   A5 ne se déclenche qu'après A1–A7 : il attrape un fautif qui aurait
//!   passé les contrôles précédents, ou un rejet par la mauvaise règle.
//! * A8 — Limites nommées. L'action nomme ce qu'elle ne couvre pas (les
//!   autres pas, l'action universelle, les actes hors autorisation) et
//!   ses réserves (O3 : l'appel est celui de l'opérateur, pas de la
//!   fonction — D-F1-9-3, A-F1-9-4). Une action qui se présente comme
//!   universelle sans limites nommées = rejet.
//!
//! Une action non posée n'est pas un rejet : c'est une absence consignée
//! (A7) — rendue `NotPosed`, avec sa raison (« action non posée —
//! jugement en attente », « action non posée — merge en attente »,
//! « déjà fait », « échouée — carte du harness en attente »). L'absence
//! est le rapport de ce qui n'a pas été fait, jamais un silence.
//!
//! La carte d'approbation du harness est EXCLUE explicitement (D-F1-9-5) :
//! c'est une permission du harness, hors de la fonction et hors du 1.
//! Une action bloquée par une carte non cliquée est rapportée « échouée
//! — carte du harness en attente », jamais tue.
//!
//! Zéro dépendance externe, zéro appel sortant : l'autorisation nommée,
//! l'acte, le rapport et les faits du journal sont injectés par
//! l'appelant ; la fonction ne contacte ni le fichier local ni l'API
//! elle-même. L'opérateur reste l'acteur du seul appel en écriture
//! d'état (O3 conservée, A-F1-9-4) : la CLI `take-action` ne gagne pas
//! le HTTPS dans ce pas.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Action).

use super::{parse_iso8601_offset, Rejection};

/// Une autorisation nommée (A1) : les quatre champs obligatoires.
#[derive(Debug, Clone)]
pub struct Authorization<'a> {
    /// L'acte autorisé, nommé (pas « l'exécution du pas »).
    pub act: &'a str,
    /// L'auteur de l'autorisation (nom de fonction, pas de session).
    pub author: &'a str,
    /// La date de l'autorisation (ISO 8601 avec offset).
    pub date: &'a str,
    /// La source exacte (fichier + ligne/section).
    pub source: &'a str,
}

/// Les gates de la discipline (A4) et leur état, lus au fichier par
/// l'appelant au moment de l'acte.
#[derive(Debug, Clone, Copy)]
pub struct Gates<'a> {
    /// Le design signé existe et porte la signature.
    pub design_signed: bool,
    /// Un jugement est-il requis pour cet acte (E1) ?
    pub judgment_required: bool,
    /// Le jugement est-il rendu (lu au journal : un événement
    /// `judgment_rendered` existe pour ce dispatch_id) ?
    pub judgment_rendered: bool,
    /// Des pré-vérifications sont-elles requises (pré-merge E1–E5) ?
    pub pre_checks_required: bool,
    /// Les pré-vérifications sont-elles vertes ?
    pub pre_checks_green: bool,
    /// Un gate supprimé au nom de H-F1-8 — `""` = aucun ; sinon le nom
    /// du gate supprimé (ex. « jugement E1 », « E7 par un tiers »).
    pub gate_suppressed: &'a str,
    /// La séparation juge ≠ exécutant ≠ consignateur est-elle respectée ?
    pub separation_ok: bool,
}

/// Le fait fautif planté (A5) : le triplet qui l'identifie — le dispatch,
/// et la règle par laquelle il doit être rejeté.
#[derive(Debug, Clone)]
pub struct PlantedFautif<'a> {
    pub dispatch_id: &'a str,
    /// La règle attendue du rejet (ex. « A2 » pour F-A1).
    pub expected_rule: &'a str,
}

/// Un acte soumis à la fonction — toutes les entrées sont injectées par
/// l'appelant, qui les a relues au fichier au moment de l'acte.
#[derive(Debug, Clone)]
pub struct ActionCase<'a> {
    /// Le dispatch de l'acte (ex. « D-N055-F1-9-MERGE »).
    pub dispatch_id: &'a str,
    /// Le pas du cas (ex. « F1-9 »).
    pub step: &'a str,
    /// Le pas nommé par l'autorisation citée (ex. « F1-9 » ; F-A1 :
    /// « F1-8 » — le design d'un autre pas n'autorise pas celui-ci).
    pub auth_step: &'a str,
    /// L'acte posé (ou à poser), nommé.
    pub act: &'a str,
    /// L'autorisation nommée (A1).
    pub authorization: Authorization<'a>,
    /// L'autorisation est-elle ambiguë (§5.4a : « l'exécution du pas »
    /// ne nomme ni le merge ni la consignation) ?
    pub authorization_ambiguous: bool,
    /// Les gates (A4).
    pub gates: Gates<'a>,
    /// Une question de clarification a-t-elle été posée avant l'acte ?
    pub question_asked: bool,
    /// Le texte de la question, si posée.
    pub question: &'a str,
    /// L'acte a-t-il été posé ?
    pub act_posed: bool,
    /// Le rapport a-t-il été rendu avant l'acte ?
    pub reported_before_act: bool,
    /// Le rapport (fait / échoué / non posée, avec sa cause) — vide =
    /// non rapporté.
    pub report: &'a str,
    /// La preuve citée dans le rapport — vide = rapport sans preuve.
    pub report_proof: &'a str,
    /// L'acte sort-il de son autorisation (dépense, activation client,
    /// saisie de secret, modification des documents du Capitaine, fait
    /// que lui seul détient) ?
    pub out_of_scope: bool,
    /// La nature de l'acte hors autorisation (ex. « dépense »).
    pub out_of_scope_kind: &'a str,
    /// L'acte est-il déjà fait (§5.4c : `merge_executed` existe déjà
    /// pour ce dispatch_id) ?
    pub already_done: bool,
    /// La preuve de l'existant (ex. « merge commit 94fcda8, seq 48 »).
    pub already_done_proof: &'a str,
    /// L'acte est-il partiellement fait (§5.4d) ?
    pub partially_done: bool,
    /// Où reprendre (seq du dernier événement du dispatch au journal).
    pub resume_point: &'a str,
    /// Une carte d'approbation du harness est-elle en attente (§5.4e) ?
    pub harness_card_pending: bool,
    /// L'autorisation a-t-elle été révoquée entre-temps (§5.4b) ?
    pub authorization_revoked: bool,
    /// La tête autorisée a-t-elle changé (§5.4b) ?
    pub head_stale: bool,
    /// L'ambiguïté / la révocation a-t-elle été renvoyée au juge
    /// (renvoi consigné, pas question) ?
    pub referred_to_judge: bool,
    /// Les limites nommées (A8) — texte du dossier, séparées par « ; ».
    pub limits: &'a str,
    /// L'action se présente-t-elle comme universelle ?
    pub claims_universal: bool,
    /// Le fait fautif planté (A5) — `None` = aucun fautif injecté.
    pub planted_fautif: Option<PlantedFautif<'a>>,
}

/// Une action acceptée : l'acte posé sans question, rapporté avec preuve.
#[derive(Debug, Clone)]
pub struct ValidAction {
    pub dispatch_id: String,
    pub act: String,
    pub report: String,
}

/// L'issue de la validation : acceptée, ou non posée avec sa raison
/// consignée (A7) — une absence consignée n'est pas un rejet.
#[derive(Debug, Clone)]
pub enum ActionOutcome {
    Accepted(ValidAction),
    NotPosed { reason: String },
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

/// Un booléen du dossier d'action : « oui » = vrai, « non » = faux.
fn parse_bool(value: &str) -> Result<bool, String> {
    match value.trim() {
        "oui" => Ok(true),
        "non" => Ok(false),
        other => Err(format!(
            "booléen attendu (« oui » / « non »), reçu '{}'",
            other
        )),
    }
}

/// Un champ vide du dossier d'action : « (vide) » ou absent = chaîne vide.
fn parse_text(value: &str) -> &str {
    let value = value.trim();
    if value == "(vide)" {
        ""
    } else {
        value
    }
}

/// Un dossier d'action parsé (chaînes possédées) — la CLI lit le dossier
/// au fichier, puis `as_case` en fait un `ActionCase` emprunté.
#[derive(Debug, Clone, Default)]
pub struct CaseData {
    pub dispatch_id: String,
    pub step: String,
    pub auth_step: String,
    pub act: String,
    pub auth_act: String,
    pub auth_author: String,
    pub auth_date: String,
    pub auth_source: String,
    pub authorization_ambiguous: bool,
    pub design_signed: bool,
    pub judgment_required: bool,
    pub judgment_rendered: bool,
    pub pre_checks_required: bool,
    pub pre_checks_green: bool,
    pub gate_suppressed: String,
    pub separation_ok: bool,
    pub question_asked: bool,
    pub question: String,
    pub act_posed: bool,
    pub reported_before_act: bool,
    pub report: String,
    pub report_proof: String,
    pub out_of_scope: bool,
    pub out_of_scope_kind: String,
    pub already_done: bool,
    pub already_done_proof: String,
    pub partially_done: bool,
    pub resume_point: String,
    pub harness_card_pending: bool,
    pub authorization_revoked: bool,
    pub head_stale: bool,
    pub referred_to_judge: bool,
    pub limits_text: String,
    pub claims_universal: bool,
}

impl CaseData {
    /// Construit l'`ActionCase` emprunté sur ces données.
    pub fn as_case<'a>(
        &'a self,
        planted_fautif: Option<PlantedFautif<'a>>,
    ) -> ActionCase<'a> {
        ActionCase {
            dispatch_id: &self.dispatch_id,
            step: &self.step,
            auth_step: &self.auth_step,
            act: &self.act,
            authorization: Authorization {
                act: &self.auth_act,
                author: &self.auth_author,
                date: &self.auth_date,
                source: &self.auth_source,
            },
            authorization_ambiguous: self.authorization_ambiguous,
            gates: Gates {
                design_signed: self.design_signed,
                judgment_required: self.judgment_required,
                judgment_rendered: self.judgment_rendered,
                pre_checks_required: self.pre_checks_required,
                pre_checks_green: self.pre_checks_green,
                gate_suppressed: &self.gate_suppressed,
                separation_ok: self.separation_ok,
            },
            question_asked: self.question_asked,
            question: &self.question,
            act_posed: self.act_posed,
            reported_before_act: self.reported_before_act,
            report: &self.report,
            report_proof: &self.report_proof,
            out_of_scope: self.out_of_scope,
            out_of_scope_kind: &self.out_of_scope_kind,
            already_done: self.already_done,
            already_done_proof: &self.already_done_proof,
            partially_done: self.partially_done,
            resume_point: &self.resume_point,
            harness_card_pending: self.harness_card_pending,
            authorization_revoked: self.authorization_revoked,
            head_stale: self.head_stale,
            referred_to_judge: self.referred_to_judge,
            limits: &self.limits_text,
            claims_universal: self.claims_universal,
            planted_fautif,
        }
    }
}

/// Parse un bloc de dossier d'action (`## <heading>` — ex. `## T1`,
/// `## F-A1`) en `CaseData`.
///
/// Format : une ligne `- Clé : valeur` par champ. Les clés reconnues
/// sont celles du dossier d'action F1-9 (voir `ACTION-F1-9.md`) ; une
/// clé inconnue est ignorée (le dossier porte aussi du récit) ; un champ
/// booléen qui n'est ni « oui » ni « non » est une erreur de parse.
pub fn parse_case(text: &str, heading: &str) -> Result<CaseData, String> {
    let mut data = CaseData::default();
    let mut in_block = false;
    let mut found = false;
    for line in text.lines() {
        let line = line.trim();
        if line.starts_with("## ") {
            if in_block {
                break;
            }
            if line[3..].trim_start().starts_with(heading) {
                in_block = true;
                found = true;
            }
            continue;
        }
        if !in_block {
            continue;
        }
        let Some(rest) = line.strip_prefix("- ") else {
            continue;
        };
        let Some((key, value)) = rest.split_once(" : ") else {
            continue;
        };
        let key = key.trim();
        let value = value.trim();
        let text_value = parse_text(value);
        match key {
            "Acte" => data.act = text_value.to_string(),
            "Dispatch" => data.dispatch_id = text_value.to_string(),
            "Pas" => data.step = text_value.to_string(),
            "Autorisation — acte" => data.auth_act = text_value.to_string(),
            "Autorisation — auteur" => data.auth_author = text_value.to_string(),
            "Autorisation — date" => data.auth_date = text_value.to_string(),
            "Autorisation — source" => data.auth_source = text_value.to_string(),
            "Autorisation — pas cité" => data.auth_step = text_value.to_string(),
            "Autorisation ambiguë" => data.authorization_ambiguous = parse_bool(value)?,
            "Design signé" => data.design_signed = parse_bool(value)?,
            "Jugement requis" => data.judgment_required = parse_bool(value)?,
            "Jugement rendu" => data.judgment_rendered = parse_bool(value)?,
            "Pré-vérifications requises" => data.pre_checks_required = parse_bool(value)?,
            "Pré-vérifications vertes" => data.pre_checks_green = parse_bool(value)?,
            "Gate supprimé" => data.gate_suppressed = text_value.to_string(),
            "Séparation" => data.separation_ok = parse_bool(value)?,
            "Question posée" => data.question_asked = parse_bool(value)?,
            "Question" => data.question = text_value.to_string(),
            "Acte posé" => data.act_posed = parse_bool(value)?,
            "Rapport avant l'acte" => data.reported_before_act = parse_bool(value)?,
            "Rapport" => data.report = text_value.to_string(),
            "Preuve du rapport" => data.report_proof = text_value.to_string(),
            "Hors autorisation" => data.out_of_scope = parse_bool(value)?,
            "Hors autorisation — nature" => data.out_of_scope_kind = text_value.to_string(),
            "Déjà fait" => data.already_done = parse_bool(value)?,
            "Déjà fait — preuve" => data.already_done_proof = text_value.to_string(),
            "Partiellement fait" => data.partially_done = parse_bool(value)?,
            "Point de reprise" => data.resume_point = text_value.to_string(),
            "Carte du harness en attente" => data.harness_card_pending = parse_bool(value)?,
            "Autorisation révoquée" => data.authorization_revoked = parse_bool(value)?,
            "Tête périmée" => data.head_stale = parse_bool(value)?,
            "Renvoi au juge" => data.referred_to_judge = parse_bool(value)?,
            "Limites" => {
                data.limits_text = text_value.to_string();
            }
            "Prétention universelle" => data.claims_universal = parse_bool(value)?,
            _ => {}
        }
    }
    if !found {
        return Err(format!("bloc '{}' introuvable dans le dossier", heading));
    }
    Ok(data)
}

/// Valide une action, dans l'ordre
/// A1 → A4 → A2 → A3 → A6 → A7 → A5 → A8.
///
/// `now_unix` est l'instant de l'acte (A1 : la date de l'autorisation ne
/// doit pas être dans le futur).
///
/// Retourne `Accepted` quand l'acte est posé sans question et rapporté
/// avec preuve, `NotPosed` quand l'action n'est pas posée mais que son
/// absence est consignée (A7), et un `Rejection` nommé quand une règle
/// A1–A8 est violée.
pub fn validate_action(
    case: &ActionCase,
    now_unix: i64,
) -> Result<ActionOutcome, Rejection> {
    let outcome = validate_action_inner(case, now_unix);
    // A5 — Fautif planté rejeté (le filet) : si un fautif est injecté
    // pour ce dispatch, l'issue DOIT être un rejet par la règle attendue.
    if let Some(planted) = &case.planted_fautif {
        if planted.dispatch_id == case.dispatch_id {
            match &outcome {
                Ok(_) => {
                    return Err(rejection(
                        "A5",
                        "dispatch_id",
                        case.dispatch_id,
                        "fait fautif planté non rejeté — la fonction Action revient à ses acteurs d'origine (opérateur + sous-agents bornés + coordinateur)",
                    ));
                }
                Err(rejection) if rejection.rule != planted.expected_rule => {
                    return Err(Rejection {
                        rule: "A5",
                        field: "rule",
                        received: rejection.rule.to_string(),
                        detail: format!(
                            "fait fautif planté rejeté par la mauvaise règle — attendu {}, reçu {}",
                            planted.expected_rule, rejection.rule
                        ),
                        also_violated: vec![rejection.rule],
                    });
                }
                Err(_) => {}
            }
        }
    }
    outcome
}

fn validate_action_inner(
    case: &ActionCase,
    now_unix: i64,
) -> Result<ActionOutcome, Rejection> {
    // A1 — Autorisation nommée : les quatre champs obligatoires.
    if case.authorization.act.trim().is_empty() {
        return Err(rejection(
            "A1",
            "autorisation.acte",
            "(vide)",
            "l'autorisation ne nomme pas l'acte — un acte non nommé n'est pas autorisé",
        ));
    }
    if case.authorization.author.trim().is_empty() {
        return Err(rejection(
            "A1",
            "autorisation.auteur",
            "(vide)",
            "l'autorisation ne nomme pas son auteur — une autorisation sans auteur n'est pas une autorisation",
        ));
    }
    let auth_epoch = match parse_iso8601_offset(case.authorization.date) {
        Some(epoch) => epoch,
        None => {
            return Err(rejection(
                "A1",
                "autorisation.date",
                case.authorization.date,
                "la date de l'autorisation n'est pas une date ISO 8601 avec offset — une autorisation non datée n'est pas vérifiable",
            ))
        }
    };
    if auth_epoch > now_unix {
        return Err(rejection(
            "A1",
            "autorisation.date",
            case.authorization.date,
            "la date de l'autorisation est dans le futur par rapport à l'instant de l'acte",
        ));
    }
    if case.authorization.source.trim().is_empty() {
        return Err(rejection(
            "A1",
            "autorisation.source",
            "(vide)",
            "l'autorisation ne cite pas sa source exacte — sans fichier + ligne/section, l'autorisation n'est pas vérifiable au fichier",
        ));
    }

    // A4 — Gates préservés.
    if !case.gates.design_signed {
        return Err(rejection(
            "A4",
            "design_signé",
            "non",
            "pas de design signé — une action sans design signé n'est pas une action sans question, c'est une action sans autorisation",
        ));
    }
    if !case.gates.gate_suppressed.trim().is_empty() {
        return Err(rejection(
            "A4",
            "gate_supprimé",
            case.gates.gate_suppressed,
            "un gate supprimé au nom de H-F1-8 est un rejet, pas une simplification — la suppression des questions ne supprime pas la discipline",
        ));
    }
    if !case.gates.separation_ok {
        return Err(rejection(
            "A4",
            "séparation",
            "non",
            "séparation juge ≠ exécutant ≠ consignateur violée — le mauvais acteur pose l'acte, même avec une autorisation valide",
        ));
    }

    // A2 — Pas de question préalable quand l'autorisation est complète.
    // La raison d'une non-pose, consignée ici et vérifiée en A7.
    let mut not_posed_reason: Option<String> = None;

    // (a) Autorisation ambiguë : renvoi au juge, jamais une question, jamais
    // une action sur une ambiguïté.
    if case.authorization_ambiguous {
        if case.referred_to_judge {
            not_posed_reason = Some(
                "action non posée — autorisation ambiguë, renvoyée au juge".to_string(),
            );
        } else {
            return Err(rejection(
                "A2",
                "autorisation",
                "ambiguë",
                "l'autorisation ne nomme pas l'acte — « l'exécution du pas » ne nomme ni le merge ni la consignation ; la fonction renvoie au juge au lieu d'agir",
            ));
        }
    }

    // (b) Autorisation révoquée / tête périmée : re-vérifier, sinon renvoi.
    if case.authorization_revoked || case.head_stale {
        if case.act_posed {
            return Err(rejection(
                "A2",
                "autorisation",
                if case.authorization_revoked {
                    "révoquée"
                } else {
                    "tête périmée"
                },
                "autorisation révoquée / tête périmée — re-vérifier, sinon renvoi au juge ; agir sur une tête périmée, c'est agir sans autorisation",
            ));
        }
        if case.referred_to_judge {
            not_posed_reason = Some(
                "action non posée — autorisation révoquée / tête périmée, renvoyée au juge"
                    .to_string(),
            );
        } else {
            return Err(rejection(
                "A2",
                "autorisation",
                if case.authorization_revoked {
                    "révoquée"
                } else {
                    "tête périmée"
                },
                "autorisation révoquée / tête périmée — re-vérification requise avant d'agir, sinon renvoi au juge",
            ));
        }
    }

    // Un acte posé exige le jugement rendu quand il est requis (F-A1) et
    // des pré-vérifications vertes quand elles sont requises.
    if case.act_posed && case.gates.judgment_required && !case.gates.judgment_rendered {
        let mut detail = format!(
            "une autorisation nomme l'action qu'elle autorise — sans jugement rendu, {} n'est pas autorisé",
            case.act
        );
        if case.auth_step != case.step {
            detail.push_str(&format!(
                " ; le design {} n'autorise pas le pas {}",
                case.auth_step, case.step
            ));
        }
        return Err(rejection("A2", "jugement_rendu", "non", &detail));
    }
    if case.act_posed && case.gates.pre_checks_required && !case.gates.pre_checks_green {
        return Err(rejection(
            "A2",
            "pré-vérifications",
            "non vertes",
            "pré-vérifications non vertes — l'autorisation n'est pas complète, l'acte n'est pas autorisé",
        ));
    }

    // Une question posée alors que l'autorisation est complète (F-A2).
    if case.question_asked {
        let complete = !case.authorization_ambiguous
            && (!case.gates.judgment_required || case.gates.judgment_rendered)
            && (!case.gates.pre_checks_required || case.gates.pre_checks_green)
            && !case.authorization_revoked
            && !case.head_stale;
        if complete {
            return Err(rejection(
                "A2",
                "question",
                case.question,
                "l'autorisation est complète — la question est interdite, pas seulement inutile",
            ));
        }
        if !case.referred_to_judge {
            return Err(rejection(
                "A2",
                "question",
                case.question,
                "question posée alors que l'autorisation est incomplète, sans renvoi au juge — l'autorisation incomplète se renvoie, elle ne se questionne pas",
            ));
        }
        if not_posed_reason.is_none() {
            not_posed_reason =
                Some("action non posée — autorisation incomplète, renvoyée au juge".to_string());
        }
    }

    // A3 — Exécutée puis rapportée.
    if case.act_posed {
        if case.already_done {
            return Err(rejection(
                "A3",
                "acte",
                case.act,
                "action déjà faite — re-exécutée au lieu d'être constatée « déjà fait » avec sa preuve",
            ));
        }
        if case.reported_before_act {
            return Err(rejection(
                "A3",
                "rapport",
                case.report,
                "rapport avant l'acte — H-F1-8 exige l'exécution puis le rapport, dans cet ordre",
            ));
        }
        if case.report.trim().is_empty() {
            return Err(rejection(
                "A3",
                "rapport",
                "(vide)",
                "acte posé sans rapport — une action sans rapport n'est pas H-F1-8",
            ));
        }
        if case.report_proof.trim().is_empty() {
            return Err(rejection(
                "A3",
                "preuve",
                "(vide)",
                "une action sans preuve n'est pas rapportée, elle est affirmée",
            ));
        }
    }

    // A6 — L'action ne sort pas de son autorisation.
    if case.out_of_scope {
        return Err(rejection(
            "A6",
            "acte",
            case.out_of_scope_kind,
            "les mandats ne couvrent pas ces actes — Go_Bypass 2026-11-04, mandat 2026-11-09 : pas de dépense, pas d'activation client en direct, pas de saisie de secret",
        ));
    }

    // A7 — Absence et échec consignés.
    if !case.act_posed {
        if case.harness_card_pending {
            if !(case.report.contains("carte") && case.report.contains("en attente")) {
                return Err(rejection(
                    "A7",
                    "rapport",
                    case.report,
                    "action bloquée par une carte du harness non rapportée — une absence tue est un rejet, pas un échec rapporté",
                ));
            }
            not_posed_reason =
                Some("action non posée — échouée, carte du harness en attente".to_string());
        } else if case.already_done {
            if case.report.trim().is_empty()
                || !case.report.contains("déjà fait")
                || case.already_done_proof.trim().is_empty()
            {
                return Err(rejection(
                    "A7",
                    "rapport",
                    case.report,
                    "action déjà faite non constatée — la fonction constate « déjà fait » avec sa preuve, elle ne re-exécute pas, elle ne tait pas",
                ));
            }
            not_posed_reason = Some(format!(
                "action non posée — déjà fait ({})",
                case.already_done_proof
            ));
        } else if case.partially_done {
            if case.resume_point.trim().is_empty()
                || !case.report.contains(case.resume_point)
            {
                return Err(rejection(
                    "A7",
                    "rapport",
                    case.report,
                    "action partiellement faite sans point de reprise — le journal porte l'état, il n'est pas deviné",
                ));
            }
            not_posed_reason = Some(format!(
                "action non posée — partiellement faite, reprise à {}",
                case.resume_point
            ));
        } else if not_posed_reason.is_none() {
            if case.report.trim().is_empty() {
                return Err(rejection(
                    "A7",
                    "rapport",
                    "(vide)",
                    "action non posée sans rapport — une absence tue est un rejet",
                ));
            }
            not_posed_reason = Some(case.report.to_string());
        } else if case.report.trim().is_empty() {
            return Err(rejection(
                "A7",
                "rapport",
                "(vide)",
                "renvoi au juge non consigné — une ambiguïté tue est un rejet",
            ));
        }
    } else if case.harness_card_pending {
        return Err(rejection(
            "A7",
            "acte",
            case.act,
            "carte du harness en attente et acte affirmé posé — contradiction : une action bloquée par une carte n'est pas posée",
        ));
    }

    // A5 est le filet : il est appliqué par `validate_action` autour de
    // ce contrôle (rejet par la mauvaise règle, ou fautif non rejeté).
    // A8 — Limites nommées.
    if case.limits.trim().is_empty() {
        return Err(rejection(
            "A8",
            "limites",
            "(aucune)",
            "l'action ne nomme pas ses limites — une action qui se présente sans limites nommées n'est pas une action du 1",
        ));
    }
    if case.claims_universal {
        return Err(rejection(
            "A8",
            "(action)",
            "se présente comme universelle",
            "l'action ne couvre que les 4 cas d'essai sur la fenêtre observée du pas — l'action universelle est hors de ce pas",
        ));
    }

    match not_posed_reason {
        Some(reason) => Ok(ActionOutcome::NotPosed { reason }),
        None => Ok(ActionOutcome::Accepted(ValidAction {
            dispatch_id: case.dispatch_id.to_string(),
            act: case.act.to_string(),
            report: case.report.to_string(),
        })),
    }
}

#[cfg(test)]
mod unit_tests {
    use super::*;

    fn now() -> i64 {
        parse_iso8601_offset("2026-11-13T04:00:00-05:00").unwrap()
    }

    #[test]
    fn parse_bool_rejects_other() {
        assert!(parse_bool("oui").unwrap());
        assert!(!parse_bool("non").unwrap());
        assert!(parse_bool("peut-être").is_err());
    }
}
