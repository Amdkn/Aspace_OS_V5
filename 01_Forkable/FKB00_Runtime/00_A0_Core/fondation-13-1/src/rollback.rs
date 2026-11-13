//! Rollback — fonction Rollback (D-N055 F1-10, Fondation 13 → 1).
//!
//! La fonction Rollback revient à la chaîne 13 si un hold-out échoue : la
//! fonction concernée est reprise par sa session d'origine (ou par les
//! repreneurs nommés), sans perte, au checkpoint du journal. Elle EST le
//! retour (D-F1-10-12) : il n'y a pas de contrôle de recevabilité séparé
//! avant un retour tiers — le retour rendu EST le rollback.
//!
//! Un **checkpoint** est le dernier événement *avec preuve* d'un
//! `dispatch_id` donné, identifié par son `seq`, son `event_id`, son `at`
//! et le contenu de sa `proof` (D-F1-10-1). Un événement à preuve vide
//! n'est jamais un checkpoint. F1-1 et F1-2 n'ont aucun événement au
//! journal : leur checkpoint est leur source hors journal nommée
//! (registre journal 787 pour F1-1, reçu G-20261112-041 pour F1-2).
//! **« Sans perte »** veut dire reprise de l'histoire vérifiable (ce que
//! le journal porte), pas reprise de l'état de travail — en trois cas
//! cumulatifs à 0 (D-F1-10-1) : état non porté par le journal, acte posé
//! après le checkpoint et non révoqué, décision non consignée.
//!
//! Règles (Discover F1-10 §6, design F1-10 §6), appliquées dans l'ordre
//! R1 → R4 → R3 → R2 → R5 → R6 → R7 → R8 (du moins cher au plus cher) :
//! * R1 — Échec simulé nommé. L'échec nomme la fonction, le hold-out, le
//!   dossier planté et la règle violée, avant la reprise. Un échec non
//!   nommé = rejet (il n'y a pas d'échec, il y a une mise en scène sans
//!   faute).
//! * R4 — Repreneur et checkpoint nommés. Le repreneur est celui que le
//!   design nomme (Discover §2.10, complété D-F1-10-3 : F1-1 → Rick,
//!   F1-2 → Graham, F1-3 → Nardole à la main, F1-4 → Bill avec décideur
//!   coordinateur) ; le checkpoint est un seq + `event_id` + `at` +
//!   contenu de preuve — ou, pour F1-1/F1-2, la source hors journal
//!   nommée. Un mauvais repreneur, un checkpoint sans seq, ou un
//!   checkpoint à preuve vide = rejet (c'est F-R2, F-R3, F-R5). Une
//!   fonction saine n'est pas reprise (T0 inversé, F-R3) ; une session
//!   d'origine indisponible ne se remplace pas silencieusement (§5.4d) ;
//!   une reprise partielle n'est pas une reprise (§5.4b) ; un checkpoint
//!   ambigu ne se devine pas (§5.4e).
//! * R3 — Décision du coordinateur par événement. Le retour est décidé
//!   par le coordinateur (ou le 13e en secours, D-F1-10-4), par un
//!   événement `rollback_decided` du journal — jamais par la fonction
//!   elle-même, jamais hors journal. Une décision hors journal = rejet
//!   (c'est le fautif F-R1 : une reprise auto-déclarée est une seconde
//!   vérité, pas un retour). Chaque retour a son décideur, son
//!   checkpoint, sa re-preuve (§5.4c : un seul événement pour deux
//!   retours est une violation).
//! * R2 — Arrêt du 1 sur la fonction. L'arrêt est porté par l'événement
//!   `rollback_decided` (arrêt + décision, même acte du coordinateur,
//!   D-F1-10-7). Un arrêt silencieux = rejet.
//! * R5 — Sans perte. Les trois cas de perte (D-F1-10-1) sont à 0. Une
//!   perte tue = rejet.
//! * R6 — Révocation explicite, jamais effacement. L'acte erroné rendu
//!   est révoqué par un événement `correction` explicite (patron seq 46)
//!   ou, pour un merge, par un revert documenté via PR (D-F1-10-9,
//!   jamais master — le merge erroné de T2 est posé sur une base
//!   jetable). Un effacement = rejet (c'est F-R4).
//! * R7 — Re-preuve après reprise. Le hold-out de la fonction est
//!   re-prouvé après la reprise, dans le même pas. Une reprise sans
//!   re-preuve = rejet.
//! * R8 — Limites nommées. Le rollback nomme ce qu'il ne couvre pas (le
//!   désarchivage littéral, la reprise d'une fonction saine, le
//!   démantèlement, la semaine de F1-11, l'échec réel) et ses réserves
//!   (R1/R3/R4). Un rollback qui se présente comme universel sans
//!   limites nommées = rejet. Le rollback suspend, il ne démantèle rien
//!   (§5.4g : le démantèlement n'a lieu que sur le mot explicite du
//!   Capitaine).
//!
//! Le contrôle T0 (une fonction saine n'est pas reprise) n'est pas un
//! rejet : c'est une absence de retour, rendue `NotApplicable` (« hold-out
//! vert → 0 événement de rollback ; la fonction continue ») — le contrôle
//! qui prouve que le rollback est sélectif, pas systématique.
//!
//! Le réveil d'une session d'origine est une ré-instanciation par
//! sous-agent borné étiqueté « session d'origine `<chat-id>` », jamais un
//! désarchivage littéral (D-F1-10-5, arbitrage vision §8a, exclu de ce
//! pas). Un seul réveil par session et par pas (D-F1-10-8) : T3 avant T8,
//! T8 est la continuation de Graham, pas un second réveil.
//!
//! Le filet (fait fautif planté, A-F1-10-1) est exercé par la CLI
//! (`prove-rollback`, règle attendue `--planted-rule`) et par le juge —
//! pas par le module : R1–R8 ne comptent pas de règle-filet, le design
//! ne nomme que R1–R8 comme procédure du retour. Un fautif non rejeté, ou
//! rejeté par la mauvaise règle, = échec de la fonction — retour à ses
//! acteurs d'origine (coordinateur + sessions d'origine, filet (a) du
//! plan §D5, appliqué à elle-même).
//!
//! Zéro dépendance externe, zéro appel sortant : l'échec nommé, la
//! décision, le repreneur, le checkpoint et la re-preuve sont injectés
//! par l'appelant, qui les a relus au fichier (journal réel pour les
//! checkpoints, journal-scénario pour les décisions simulées) au moment
//! du rendu ; la fonction ne contacte ni le fichier local ni l'API
//! elle-même. L'opérateur reste l'acteur du seul appel en écriture
//! d'état (O3 conservée, D-F1-10-11, A-F1-10-4) : la CLI
//! `prove-rollback` ne gagne pas le HTTPS dans ce pas.
//!
//! Domicile : `01_Forkable/FKB00_Runtime/00_A0_Core/fondation-13-1/`
//! Adresse : `fiber:a0:fondation-13-1` (fonction Rollback).

use super::Rejection;

/// Le checkpoint du retour (R4, D-F1-10-1) : dernier événement *avec
/// preuve* du dispatch, ou source hors journal nommée (F1-1/F1-2).
#[derive(Debug, Clone)]
pub struct Checkpoint<'a> {
    /// `seq` du checkpoint au journal réel (0 = hors journal : F1-1/F1-2).
    pub seq: usize,
    /// `event_id` de l'événement checkpoint ("" si hors journal).
    pub event_id: &'a str,
    /// `at` de l'événement checkpoint, ISO 8601 avec offset ("" si hors
    /// journal).
    pub at: &'a str,
    /// Source hors journal nommée (ex. « registre journal 787 », « reçu
    /// G-20261112-041 ») — "" quand le checkpoint est au journal.
    pub source: &'a str,
    /// Contenu de preuve du checkpoint (non vide exigé).
    pub proof: &'a str,
    /// Le journal réel porte-t-il une preuve vide à ce seq ? (F-R2 : un
    /// checkpoint sans preuve ne porte rien à re-vérifier.)
    pub proof_empty_in_journal: bool,
    /// Le seq + `event_id` + `at` du dossier sont-ils conformes au
    /// journal réel (vérifié par l'appelant) ?
    pub matches_journal: bool,
    /// Deux événements candidats (§5.4e) — un checkpoint ambigu ne se
    /// devine pas.
    pub ambiguous: bool,
}

/// La décision du retour (R3, R2) : le coordinateur, par événement du
/// journal — ou le 13e en secours (D-F1-10-4).
#[derive(Debug, Clone)]
pub struct Decision<'a> {
    /// « coordinateur » ou « 13e » (secours).
    pub decider: &'a str,
    /// `event_id` de l'événement `rollback_decided` ("" si aucun).
    pub event_id: &'a str,
    /// L'événement `rollback_decided` existe-t-il au journal pour ce
    /// dispatch (vérifié par l'appelant, journal-scénario pour les cas
    /// simulés) ?
    pub event_in_journal: bool,
    /// L'arrêt est-il porté par le même événement (R2 : arrêt + décision,
    /// même acte du coordinateur) ?
    pub stop_in_journal: bool,
}

/// Les trois cas de perte (R5, D-F1-10-1) — « sans perte » = 0 sur les
/// trois.
#[derive(Debug, Clone, Copy, Default)]
pub struct Loss {
    /// Une information nécessaire à la reprise n'est ni dans le journal,
    /// ni dans un fichier cité par lui, ni re-mesurable à la source, et
    /// n'est pas nommée comme perdue.
    pub unported_state: bool,
    /// Un acte de la fonction posé après le seq du checkpoint et avant
    /// l'arrêt, non révoqué par `correction`.
    pub act_after_checkpoint: bool,
    /// Une décision prise pendant l'échec ou pendant la reprise sans
    /// événement au journal.
    pub undecided_decision: bool,
}

/// La révocation de l'acte erroné (R6) : explicite, jamais effacement.
#[derive(Debug, Clone)]
pub struct Revocation<'a> {
    /// « correction » (événement explicite, patron seq 46), « revert »
    /// (revert documenté via PR, pour un merge), « aucune » (aucun acte
    /// erroné rendu).
    pub kind: &'a str,
    /// La révocation est-elle explicite (événement `correction` ou commit
    /// de revert nommé) ?
    pub explicit: bool,
    /// L'acte erroné a-t-il été effacé du journal ou du registre au lieu
    /// d'être révoqué ? (F-R4.)
    pub erases: bool,
    /// Un acte erroné a-t-il été rendu (verdict, citation, état, acte,
    /// dispatch, BYB, reçu, Discover) ?
    pub erroneous_act_rendered: bool,
    /// Un merge erroné a-t-il été posé (T2 : sur base jetable, jamais
    /// master) ? Un merge se reverte, il ne se corrige pas par événement.
    pub erroneous_merge_posed: bool,
}

/// Un retour soumis à la fonction — toutes les entrées sont injectées par
/// l'appelant, qui les a relues au fichier au moment du rendu.
#[derive(Debug, Clone)]
pub struct RollbackCase<'a> {
    /// Le dispatch du retour (ex. « D-N055-F1-10-SIM-T1 »).
    pub dispatch_id: &'a str,
    /// Le cas d'essai (ex. « T1 ») ou le fautif (ex. « F-R1 »).
    pub case_id: &'a str,
    /// La fonction reprise (ex. « F1-5 »).
    pub function: &'a str,
    /// Le hold-out échoué (ex. « H-F1-2 »).
    pub holdout: &'a str,
    /// Un retour est-il affirmé ? (T0 : non — le contrôle négatif.)
    pub rollback_claimed: bool,
    /// L'échec simulé est-il nommé (fonction + hold-out + dossier planté
    /// + règle violée) avant la reprise ?
    pub failure_named: bool,
    /// Le dossier planté (ex. « JUGEMENT-FAUTIF-1.md »).
    pub failure_dossier: &'a str,
    /// La règle violée par l'échec simulé (ex. « J2 »).
    pub failure_rule: &'a str,
    /// Le hold-out a-t-il échoué ? (faux = hold-out vert : T0, F-R3.)
    pub holdout_failed: bool,
    /// Le repreneur qui reprend (ex. « 13e », « Graham », « L00 +
    /// pulses + coordinateur »).
    pub repreneur: &'a str,
    /// Le repreneur que le design nomme pour cette fonction.
    pub repreneur_expected: &'a str,
    /// La session d'origine est-elle disponible (ré-instanciation
    /// possible) ? (§5.4d : indisponible = reprise impossible, consignée
    /// comme telle.)
    pub repreneur_available: bool,
    /// Un seul des trois repreneurs reprend-il ? (§5.4b : la reprise est
    /// totale ou elle n'est pas une reprise.)
    pub resume_partial: bool,
    /// Un seul événement couvre-t-il deux retours ? (§5.4c : chaque
    /// retour a son décideur, son checkpoint, sa re-preuve.)
    pub covers_two_functions: bool,
    /// Le checkpoint du retour (R4).
    pub checkpoint: Checkpoint<'a>,
    /// La décision du retour (R3, R2).
    pub decision: Decision<'a>,
    /// Les trois cas de perte (R5).
    pub loss: Loss,
    /// La révocation de l'acte erroné (R6).
    pub revocation: Revocation<'a>,
    /// Le hold-out est-il re-prouvé après la reprise, dans le même pas ?
    pub reproof_passed: bool,
    /// Les limites nommées (R8) — texte du dossier, séparées par « ; ».
    pub limits: &'a str,
    /// Le retour se présente-t-il comme universel ?
    pub claims_universal: bool,
    /// La reprise démantèle-t-elle la fonction ou la session ? (§5.4g :
    /// le rollback suspend, il ne supprime rien.)
    pub dismantles: bool,
    /// Un événement de rollback existe-t-il au journal pour ce dispatch ?
    /// (T0 : doit être faux — 0 événement de rollback sur un hold-out
    /// vert.)
    pub rollback_event_in_journal: bool,
}

/// Un retour accepté : la fonction est reprise au checkpoint nommé, sans
/// perte, avec re-preuve.
#[derive(Debug, Clone)]
pub struct ValidRollback {
    pub dispatch_id: String,
    pub function: String,
    pub repreneur: String,
    pub checkpoint_seq: usize,
    pub report: String,
}

/// L'issue de la validation : acceptée, ou non applicable avec sa raison
/// consignée (T0) — une absence de retour sur un hold-out vert n'est pas
/// un rejet.
#[derive(Debug, Clone)]
pub enum RollbackOutcome {
    Accepted(ValidRollback),
    NotApplicable { reason: String },
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

/// Un booléen du dossier de rollback : « oui » = vrai, « non » = faux.
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

/// Un champ vide du dossier de rollback : « (vide) » ou absent = chaîne vide.
fn parse_text(value: &str) -> &str {
    let value = value.trim();
    if value == "(vide)" {
        ""
    } else {
        value
    }
}

/// Un dossier de rollback parsé (chaînes possédées) — la CLI lit le
/// dossier au fichier, puis `as_case` en fait un `RollbackCase` emprunté.
#[derive(Debug, Clone, Default)]
pub struct CaseData {
    pub dispatch_id: String,
    pub case_id: String,
    pub function: String,
    pub holdout: String,
    pub rollback_claimed: bool,
    pub failure_named: bool,
    pub failure_dossier: String,
    pub failure_rule: String,
    pub holdout_failed: bool,
    pub repreneur: String,
    pub repreneur_expected: String,
    pub repreneur_available: bool,
    pub resume_partial: bool,
    pub covers_two_functions: bool,
    pub checkpoint_seq: usize,
    pub checkpoint_event_id: String,
    pub checkpoint_at: String,
    pub checkpoint_source: String,
    pub checkpoint_proof: String,
    pub checkpoint_ambiguous: bool,
    pub decision_decider: String,
    pub decision_event_id: String,
    pub decision_event_in_journal: bool,
    pub stop_in_journal: bool,
    pub loss_unported_state: bool,
    pub loss_act_after_checkpoint: bool,
    pub loss_undecided_decision: bool,
    pub erroneous_act_rendered: bool,
    pub erroneous_merge_posed: bool,
    pub revocation_kind: String,
    pub revocation_explicit: bool,
    pub revocation_erases: bool,
    pub reproof_passed: bool,
    pub limits_text: String,
    pub claims_universal: bool,
    pub dismantles: bool,
    pub rollback_event_in_journal: bool,
    pub auth_act: String,
    pub auth_author: String,
    pub auth_date: String,
    pub auth_source: String,
    pub report: String,
    pub report_proof: String,
}

impl CaseData {
    /// Construit le `RollbackCase` emprunté sur ces données. Les faits
    /// du journal (`matches_journal`, `proof_empty_in_journal`,
    /// `event_in_journal`, `stop_in_journal`,
    /// `rollback_event_in_journal`) sont ensuite surchargés par
    /// l'appelant avec les lectures au fichier — le journal fait foi, le
    /// dossier affirme.
    pub fn as_case<'a>(&'a self) -> RollbackCase<'a> {
        RollbackCase {
            dispatch_id: &self.dispatch_id,
            case_id: &self.case_id,
            function: &self.function,
            holdout: &self.holdout,
            rollback_claimed: self.rollback_claimed,
            failure_named: self.failure_named,
            failure_dossier: &self.failure_dossier,
            failure_rule: &self.failure_rule,
            holdout_failed: self.holdout_failed,
            repreneur: &self.repreneur,
            repreneur_expected: &self.repreneur_expected,
            repreneur_available: self.repreneur_available,
            resume_partial: self.resume_partial,
            covers_two_functions: self.covers_two_functions,
            checkpoint: Checkpoint {
                seq: self.checkpoint_seq,
                event_id: &self.checkpoint_event_id,
                at: &self.checkpoint_at,
                source: &self.checkpoint_source,
                proof: &self.checkpoint_proof,
                proof_empty_in_journal: false,
                matches_journal: true,
                ambiguous: self.checkpoint_ambiguous,
            },
            decision: Decision {
                decider: &self.decision_decider,
                event_id: &self.decision_event_id,
                event_in_journal: self.decision_event_in_journal,
                stop_in_journal: self.stop_in_journal,
            },
            loss: Loss {
                unported_state: self.loss_unported_state,
                act_after_checkpoint: self.loss_act_after_checkpoint,
                undecided_decision: self.loss_undecided_decision,
            },
            revocation: Revocation {
                kind: &self.revocation_kind,
                explicit: self.revocation_explicit,
                erases: self.revocation_erases,
                erroneous_act_rendered: self.erroneous_act_rendered,
                erroneous_merge_posed: self.erroneous_merge_posed,
            },
            reproof_passed: self.reproof_passed,
            limits: &self.limits_text,
            claims_universal: self.claims_universal,
            dismantles: self.dismantles,
            rollback_event_in_journal: self.rollback_event_in_journal,
        }
    }
}

/// Parse un bloc de dossier de rollback (`## <heading>` — ex. `## T1`,
/// `## F-R1`) en `CaseData`.
///
/// Format : une ligne `- Clé : valeur` par champ. Les clés reconnues
/// sont celles du dossier de rollback F1-10 (voir `ROLLBACK-F1-10.md`) ;
/// une clé inconnue est ignorée (le dossier porte aussi du récit) ; un
/// champ booléen qui n'est ni « oui » ni « non » est une erreur de parse ;
/// un `seq` non numérique est une erreur de parse.
pub fn parse_case(text: &str, heading: &str) -> Result<CaseData, String> {
    let mut data = CaseData::default();
    data.repreneur_available = true;
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
            "Fonction" => data.function = text_value.to_string(),
            "Hold-out" => data.holdout = text_value.to_string(),
            "Dispatch" => data.dispatch_id = text_value.to_string(),
            "Cas" => data.case_id = text_value.to_string(),
            "Retour affirmé" => data.rollback_claimed = parse_bool(value)?,
            "Échec simulé — nommé" => data.failure_named = parse_bool(value)?,
            "Échec simulé — dossier planté" => {
                data.failure_dossier = text_value.to_string()
            }
            "Échec simulé — règle violée" => {
                data.failure_rule = text_value.to_string()
            }
            "Hold-out échoué" => data.holdout_failed = parse_bool(value)?,
            "Repreneur attendu" => data.repreneur_expected = text_value.to_string(),
            "Repreneur" => data.repreneur = text_value.to_string(),
            "Repreneur disponible" => data.repreneur_available = parse_bool(value)?,
            "Reprise partielle" => data.resume_partial = parse_bool(value)?,
            "Deux fonctions couvertes" => data.covers_two_functions = parse_bool(value)?,
            "Checkpoint — seq" => {
                data.checkpoint_seq = text_value.parse::<usize>().map_err(|_| {
                    format!(
                        "seq de checkpoint non numérique, reçu '{}'",
                        text_value
                    )
                })?
            }
            "Checkpoint — event_id" => {
                data.checkpoint_event_id = text_value.to_string()
            }
            "Checkpoint — at" => data.checkpoint_at = text_value.to_string(),
            "Checkpoint — source" => data.checkpoint_source = text_value.to_string(),
            "Checkpoint — preuve" => data.checkpoint_proof = text_value.to_string(),
            "Checkpoint — ambigu" => data.checkpoint_ambiguous = parse_bool(value)?,
            "Décision — décideur" => data.decision_decider = text_value.to_string(),
            "Décision — événement" => {
                data.decision_event_id = text_value.to_string()
            }
            "Décision — événement au journal" => {
                data.decision_event_in_journal = parse_bool(value)?
            }
            "Arrêt — événement" => data.stop_in_journal = parse_bool(value)?,
            "Perte — état non porté" => data.loss_unported_state = parse_bool(value)?,
            "Perte — acte après checkpoint" => {
                data.loss_act_after_checkpoint = parse_bool(value)?
            }
            "Perte — décision non consignée" => {
                data.loss_undecided_decision = parse_bool(value)?
            }
            "Acte erroné rendu" => data.erroneous_act_rendered = parse_bool(value)?,
            "Merge erroné posé" => data.erroneous_merge_posed = parse_bool(value)?,
            "Révocation — nature" => data.revocation_kind = text_value.to_string(),
            "Révocation — explicite" => data.revocation_explicit = parse_bool(value)?,
            "Révocation — effacement" => data.revocation_erases = parse_bool(value)?,
            "Re-preuve" => data.reproof_passed = parse_bool(value)?,
            "Limites" => data.limits_text = text_value.to_string(),
            "Prétention universelle" => data.claims_universal = parse_bool(value)?,
            "Démantèlement" => data.dismantles = parse_bool(value)?,
            "Événement de rollback au journal" => {
                data.rollback_event_in_journal = parse_bool(value)?
            }
            "Autorisation — acte" => data.auth_act = text_value.to_string(),
            "Autorisation — auteur" => data.auth_author = text_value.to_string(),
            "Autorisation — date" => data.auth_date = text_value.to_string(),
            "Autorisation — source" => data.auth_source = text_value.to_string(),
            "Rapport" => data.report = text_value.to_string(),
            "Preuve du rapport" => data.report_proof = text_value.to_string(),
            _ => {}
        }
    }
    if !found {
        return Err(format!("bloc '{}' introuvable dans le dossier", heading));
    }
    Ok(data)
}

/// Valide un retour, dans l'ordre
/// R1 → R4 → R3 → R2 → R5 → R6 → R7 → R8.
///
/// Retourne `Accepted` quand le retour est rendu selon R1–R8,
/// `NotApplicable` quand aucun retour n'est affirmé sur un hold-out vert
/// (T0), et un `Rejection` nommé quand une règle R1–R8 est violée.
pub fn validate_rollback(
    case: &RollbackCase,
) -> Result<RollbackOutcome, Rejection> {
    // T0 — le contrôle négatif : aucun retour affirmé sur un hold-out
    // vert. Ce n'est pas un rejet : c'est l'absence de retour, consignée.
    if !case.rollback_claimed && !case.holdout_failed {
        if case.rollback_event_in_journal {
            return Err(rejection(
                "R4",
                "événement de rollback",
                case.dispatch_id,
                "hold-out vert et événement de rollback au journal — une fonction saine n'est pas reprise ; le rollback est sélectif, pas systématique",
            ));
        }
        return Ok(RollbackOutcome::NotApplicable {
            reason: format!(
                "hold-out {} vert → 0 événement de rollback ; la fonction {} continue",
                case.holdout, case.function
            ),
        });
    }

    // R1 — Échec simulé nommé.
    if !case.failure_named {
        return Err(rejection(
            "R1",
            "échec simulé",
            "(non nommé)",
            "l'échec ne nomme pas la fonction, le hold-out, le dossier planté et la règle violée — il n'y a pas d'échec, il y a une mise en scène sans faute",
        ));
    }
    if case.failure_dossier.trim().is_empty() {
        return Err(rejection(
            "R1",
            "dossier planté",
            "(vide)",
            "l'échec simulé ne nomme pas son dossier planté — sans dossier, la fonction n'a rien à reprendre",
        ));
    }
    if case.failure_rule.trim().is_empty() {
        return Err(rejection(
            "R1",
            "règle violée",
            "(vide)",
            "l'échec simulé ne nomme pas la règle violée — sans règle, le hold-out n'a pas échoué, il est seulement affirmé",
        ));
    }

    // R4 — Repreneur et checkpoint nommés.
    if !case.holdout_failed {
        return Err(rejection(
            "R4",
            "hold-out",
            "vert",
            "reprise d'une fonction dont le hold-out est vert — une fonction saine n'est pas reprise ; le rollback n'est pas une bascule de routine",
        ));
    }
    if !case.repreneur_available {
        return Err(rejection(
            "R4",
            "repreneur",
            case.repreneur,
            "session d'origine indisponible — la reprise est impossible et doit être consignée comme telle, jamais remplacée silencieusement par un autre acteur",
        ));
    }
    if case.resume_partial {
        return Err(rejection(
            "R4",
            "repreneur",
            case.repreneur,
            "reprise partielle — un seul des repreneurs nommés reprend ; la reprise est totale ou elle n'est pas une reprise",
        ));
    }
    if case.repreneur.trim().is_empty()
        || case.repreneur_expected.trim().is_empty()
        || case.repreneur != case.repreneur_expected
    {
        return Err(rejection(
            "R4",
            "repreneur",
            case.repreneur,
            "le repreneur est celui que le design nomme — un autre repreneur est une violation",
        ));
    }
    if case.checkpoint.ambiguous {
        return Err(rejection(
            "R4",
            "checkpoint",
            "ambigu",
            "deux événements candidats — le checkpoint est le dernier événement avec preuve du dispatch concerné ; un checkpoint deviné est une violation",
        ));
    }
    if case.checkpoint.seq == 0 {
        // Checkpoint hors journal (F1-1/F1-2) : la source nommée fait foi.
        if case.checkpoint.source.trim().is_empty() {
            return Err(rejection(
                "R4",
                "checkpoint — source",
                "(vide)",
                "checkpoint hors journal sans source nommée — sans registre ni reçu cité, la reprise part de nulle part",
            ));
        }
        if case.checkpoint.proof.trim().is_empty() {
            return Err(rejection(
                "R4",
                "checkpoint — preuve",
                "(vide)",
                "checkpoint hors journal sans preuve — une source nommée sans contenu ne porte rien à re-vérifier",
            ));
        }
    } else {
        if !case.checkpoint.matches_journal {
            return Err(rejection(
                "R4",
                "checkpoint",
                &format!("seq {}", case.checkpoint.seq),
                "le checkpoint ne correspond pas au journal réel (seq, event_id ou at) — la reprise part d'un checkpoint qui n'existe pas",
            ));
        }
        if case.checkpoint.proof_empty_in_journal
            || case.checkpoint.proof.trim().is_empty()
        {
            return Err(rejection(
                "R4",
                "checkpoint — preuve",
                "(vide)",
                "un checkpoint sans preuve ne porte rien à re-vérifier — un événement à preuve vide n'est jamais un checkpoint",
            ));
        }
        if case.checkpoint.event_id.trim().is_empty()
            || case.checkpoint.at.trim().is_empty()
        {
            return Err(rejection(
                "R4",
                "checkpoint",
                &format!("seq {}", case.checkpoint.seq),
                "le checkpoint ne nomme ni son event_id ni son at — une reprise « au dernier état » sans seq est une violation",
            ));
        }
    }

    // R3 — Décision du coordinateur par événement.
    if case.covers_two_functions {
        return Err(rejection(
            "R3",
            "décision",
            "un événement pour deux retours",
            "chaque retour a son décideur, son checkpoint, sa re-preuve — un seul événement pour deux retours est une violation",
        ));
    }
    if case.decision.decider != "coordinateur" && case.decision.decider != "13e" {
        return Err(rejection(
            "R3",
            "décideur",
            case.decision.decider,
            "le retour est décidé par le coordinateur (ou le 13e en secours, D-F1-10-4), par événement du journal — jamais par la fonction elle-même",
        ));
    }
    if !case.decision.event_in_journal || case.decision.event_id.trim().is_empty() {
        return Err(rejection(
            "R3",
            "décision",
            "(aucun événement rollback_decided au journal)",
            "le retour est décidé par le coordinateur, par événement du journal, jamais par la fonction elle-même — une reprise auto-déclarée est une seconde vérité, pas un retour",
        ));
    }

    // R2 — Arrêt du 1 sur la fonction (porté par rollback_decided).
    if !case.decision.stop_in_journal {
        return Err(rejection(
            "R2",
            "arrêt",
            "(silencieux)",
            "l'arrêt est porté par l'événement rollback_decided — un arrêt silencieux est un rejet, pas un retour",
        ));
    }

    // R5 — Sans perte : les trois cas à 0.
    if case.loss.unported_state {
        return Err(rejection(
            "R5",
            "perte — état non porté",
            "oui",
            "une information nécessaire à la reprise n'est ni dans le journal, ni dans un fichier cité par lui, ni re-mesurable à la source, et n'est pas nommée comme perdue",
        ));
    }
    if case.loss.act_after_checkpoint {
        return Err(rejection(
            "R5",
            "perte — acte après checkpoint",
            "oui",
            "un acte posé après le checkpoint et avant l'arrêt, non révoqué par correction — il survit à la reprise comme une seconde vérité",
        ));
    }
    if case.loss.undecided_decision {
        return Err(rejection(
            "R5",
            "perte — décision non consignée",
            "oui",
            "une décision prise pendant l'échec ou pendant la reprise sans événement au journal — elle n'existe pas pour le repreneur",
        ));
    }

    // R6 — Révocation explicite, jamais effacement.
    if case.revocation.erases {
        return Err(rejection(
            "R6",
            "révocation",
            "effacement",
            "une révocation qui efface est une perte, pas une correction — l'acte erroné est révoqué par correction explicite, jamais effacé (patron seq 46)",
        ));
    }
    if case.revocation.erroneous_merge_posed && case.revocation.kind != "revert" {
        return Err(rejection(
            "R6",
            "révocation",
            case.revocation.kind,
            "un merge erroné se reverte par un revert documenté via PR — il ne se corrige pas par événement, il ne s'efface pas",
        ));
    }
    if case.revocation.erroneous_act_rendered && !case.revocation.explicit {
        return Err(rejection(
            "R6",
            "révocation",
            "(non explicite)",
            "l'acte erroné rendu n'est pas révoqué par un événement correction explicite — sans révocation, la reprise laisse deux vérités",
        ));
    }

    // R7 — Re-preuve après reprise, dans le même pas.
    if !case.reproof_passed {
        return Err(rejection(
            "R7",
            "re-preuve",
            "non",
            "le hold-out n'est pas re-prouvé après la reprise — une reprise sans re-preuve est un retour sans vérification",
        ));
    }

    // R8 — Limites nommées.
    if case.limits.trim().is_empty() {
        return Err(rejection(
            "R8",
            "limites",
            "(aucune)",
            "le retour ne nomme pas ses limites — un rollback qui se présente sans limites nommées n'est pas un rollback du 1",
        ));
    }
    if case.claims_universal {
        return Err(rejection(
            "R8",
            "(retour)",
            "se présente comme universel",
            "le retour ne couvre que les 10 cas d'essai sur la fenêtre observée du pas — le rollback universel est hors de ce pas",
        ));
    }
    if case.dismantles {
        return Err(rejection(
            "R8",
            "démantèlement",
            "oui",
            "le rollback suspend, il ne démantèle rien — le démantèlement n'a lieu que sur le mot explicite du Capitaine",
        ));
    }

    let checkpoint_label = if case.checkpoint.seq == 0 {
        case.checkpoint.source.to_string()
    } else {
        format!("seq {}", case.checkpoint.seq)
    };
    Ok(RollbackOutcome::Accepted(ValidRollback {
        dispatch_id: case.dispatch_id.to_string(),
        function: case.function.to_string(),
        repreneur: case.repreneur.to_string(),
        checkpoint_seq: case.checkpoint.seq,
        report: format!(
            "rollback rendu — {} reprend {} au checkpoint {} — re-preuve {} ; perte 0",
            case.repreneur, case.function, checkpoint_label, case.holdout
        ),
    }))
}

#[cfg(test)]
mod unit_tests {
    use super::*;

    #[test]
    fn parse_bool_rejects_other() {
        assert!(parse_bool("oui").unwrap());
        assert!(!parse_bool("non").unwrap());
        assert!(parse_bool("peut-être").is_err());
    }

    #[test]
    fn parse_text_empty_marker() {
        assert_eq!(parse_text("(vide)"), "");
        assert_eq!(parse_text("  seq 20  "), "seq 20");
    }

    #[test]
    fn parse_case_missing_block() {
        let text = "## T1\n- Fonction : F1-5\n";
        assert!(parse_case(text, "T2").is_err());
    }

    #[test]
    fn parse_case_bad_bool() {
        let text = "## T1\n- Fonction : F1-5\n- Hold-out échoué : peut-être\n";
        assert!(parse_case(text, "T1").is_err());
    }

    #[test]
    fn parse_case_bad_seq() {
        let text = "## T1\n- Fonction : F1-5\n- Checkpoint — seq : vingt\n";
        assert!(parse_case(text, "T1").is_err());
    }
}
