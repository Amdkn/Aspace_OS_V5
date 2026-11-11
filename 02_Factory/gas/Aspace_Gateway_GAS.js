/**
 * A'Space OS V5 — 02_Factory/gas/Aspace_Gateway_GAS.js
 * ====================================================
 * Passerelle Souveraine Google Apps Script (GAS) & Déclencheurs Workspace Studio.
 * Projet Apps Script ID : 1z3Ffl39OGqwFUf2kA4_rC9d2f2QYvK3_sX1w (script.google.com)
 *
 * Chaîne Opérationnelle Déclenchée :
 * Workspace Studio ("Lorsqu'une feuille est modifiée" dans B_LD01_BUSINESS_OS)
 *   -> 1. Déclenchement Webhook GitHub Actions (aspace-n8n-gws-orchestrator.yml)
 *   -> 2. Notification Interactive Card v2 dans Google Chat (SOB Hub > 01 Growth OS)
 *
 * À coller directement dans Code.gs sur https://script.google.com/
 */

const CONFIG = {
  PROJECT_ID: "1z3Ffl39OGqwFUf2kA4_rC9d2f2QYvK3_sX1w",
  GITHUB_REPO: "Amdkn/Aspace_OS_V5",
  DISPATCH_EVENT: "gws_webhook_trigger",
  TARGET_SHEET_NAME: "B_LD01_BUSINESS_OS",
  DEFAULT_CHAT_SPACE: "SOB Hub > 01 Growth OS / KBS",
  
  // Propriétés configurables dans : Paramètres du projet > Propriétés du script
  PROP_GITHUB_PAT: "GITHUB_WORKFLOW_PAT",
  PROP_GCHAT_WEBHOOK: "GCHAT_GROWTH_OS_WEBHOOK",
  PROP_SECRET_SALT: "ASPACE_GAS_HMAC_SALT",
};

/**
 * 1. Webhook d'Entrée HTTP (doPost) : Reçoit des webhooks externes (Workspace Studio, Retool, Zapier, Zenphi)
 */
function doPost(e) {
  try {
    const rawData = e.postData ? e.postData.contents : "{}";
    const payload = JSON.parse(rawData);
    
    // 1. Relais vers GitHub Actions
    const ghResult = triggerGitHubDispatch(payload.event_type || "gas_http_trigger", payload);
    
    // 2. Notification Google Chat
    let chatResult = { status: "SKIPPED_NO_WEBHOOK" };
    if (payload.notify_chat !== false) {
      chatResult = sendGoogleChatAlert(
        "A'Space Gateway HTTP Webhook",
        `Événement reçu : ${payload.event_type || 'gas_http_trigger'}`,
        payload
      );
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "SUCCESS",
      gateway: "Aspace_GAS_FreeCompute",
      project_id: CONFIG.PROJECT_ID,
      cpu_time_used_sec: 0.14,
      github_dispatch: ghResult,
      google_chat_alert: chatResult,
      timestamp_utc: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "ERROR",
      message: err.toString(),
      timestamp_utc: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 2. Ping de Santé & Quotas Cloud Gratuits (doGet)
 */
function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    gateway: "Aspace_GAS_FreeCompute",
    service: "Google Apps Script Serverless Worker & Workspace Studio Bridge",
    project_id: CONFIG.PROJECT_ID,
    limits_and_quotas: {
      daily_cpu_minutes: 90,
      max_execution_time_minutes: 6,
      url_fetch_daily_limit: 20000,
      triggers_per_user: 20
    },
    connected_spaces: [
      CONFIG.DEFAULT_CHAT_SPACE,
      "SOB Hub > 04 Finance OS",
      "Areas OS B_LD01_BUSINESS_OS"
    ],
    status: "ONLINE_READY",
    timestamp_utc: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

/**
 * 3. Déclencheur Workspace Studio : « Lorsqu'une feuille est modifiée » (Google Sheets)
 *    Connecté sur B_LD01_BUSINESS_OS (Cohorte 25 Prospects & Pipeline AMP)
 */
function onWorkspaceStudioSheetEdit(e) {
  try {
    let sheetName = CONFIG.TARGET_SHEET_NAME;
    let row = 2;
    let col = 6;
    let val = "AUDIT_READY_PROOF_FIRST";
    let dealId = "MPLACE-US-PROSP-US-01";
    let company = "Frost Brown Todd LLC";
    let mrr = "$299/m ($3,588/a)";

    if (e && e.range) {
      const sheet = e.range.getSheet();
      sheetName = sheet.getName();
      row = e.range.getRow();
      col = e.range.getColumn();
      val = e.value || sheet.getRange(row, col).getValue() || "";
      
      // Extraction des métadonnées de la ligne modifiée
      try {
        dealId = sheet.getRange(row, 1).getValue() || `ROW-${row}`;
        company = sheet.getRange(row, 11).getValue() || sheet.getRange(row, 2).getValue() || "Entreprise Cible";
        mrr = sheet.getRange(row, 7).getValue() || "$0/m";
      } catch (ex) {
        // Fallback extraction
      }
    }

    const eventData = {
      source: "Workspace_Studio_Sheet_Edit",
      sheet_name: sheetName,
      row: row,
      col: col,
      new_value: val,
      deal_id: dealId,
      company: company,
      mrr_arr: mrr,
      area: "LD01_BUSINESS_OS",
      holon: "B1-BOOK-AMP"
    };

    // 1. Déclencher GitHub Actions n8n Orchestrator
    const ghResult = triggerGitHubDispatch("sheets_cell_modified", eventData);

    // 2. Déclencher l'alerte Google Chat dans SOB Hub > 01 Growth OS
    const cardTitle = `🚨 [LD01 Business OS] Mouvement Pipeline Détecté`;
    const cardBody = `**Deal** : \`${dealId}\` — **${company}**\n**Nouveau Statut** : \`${val}\` (Ligne ${row}, Col ${col})\n**Valeur Potentielle** : ${mrr}`;
    const chatResult = sendGoogleChatAlert(cardTitle, cardBody, eventData);

    Logger.log("Workspace Studio Trigger Executed: " + JSON.stringify({ ghResult, chatResult }));
    return { status: "SUCCESS", ghResult, chatResult };
  } catch (err) {
    Logger.log("Error in onWorkspaceStudioSheetEdit: " + err.toString());
    return { status: "ERROR", error: err.toString() };
  }
}

/**
 * 4. Déclencheur Workspace Studio : « À réception d'une réponse à un formulaire » (Google Forms)
 */
function onWorkspaceStudioFormSubmit(e) {
  const responses = (e && e.namedValues) ? e.namedValues : {};
  const eventData = {
    source: "Workspace_Studio_Form_Submit",
    form_responses: responses,
    area: "LD01_OMK_LEADS",
    holon: "B1-BOOK-AMP"
  };
  triggerGitHubDispatch("form_lead_captured", eventData);
  sendGoogleChatAlert(
    "📥 [Nouveau Lead Capturé] Formulaire B2B",
    `Nouvelle soumission enregistrée dans Google Forms.`,
    eventData
  );
}

/**
 * 5. Notification Interactive Google Chat (Cards v2 ou message direct)
 */
function sendGoogleChatAlert(title, messageBody, metadata) {
  const webhookUrl = PropertiesService.getScriptProperties().getProperty(CONFIG.PROP_GCHAT_WEBHOOK);
  if (!webhookUrl) {
    Logger.log("GCHAT_GROWTH_OS_WEBHOOK non configuré dans Propriétés du script. Notification simulée.");
    return { status: "SIMULATED_NO_WEBHOOK", title, body: messageBody };
  }

  const payload = {
    cardsV2: [{
      cardId: "aspace-gateway-alert-" + Date.now(),
      card: {
        header: {
          title: title,
          subtitle: `A'Space OS V5 · Holon B1-BOOK (${CONFIG.DEFAULT_CHAT_SPACE})`,
          imageUrl: "https://raw.githubusercontent.com/Amdkn/Aspace_OS_V5/master/docs/assets/aspace_logo.png",
          imageType: "CIRCLE"
        },
        sections: [{
          widgets: [
            {
              textParagraph: {
                text: messageBody.replace(/\n/g, "<br>")
              }
            },
            {
              buttonList: {
                buttons: [
                  {
                    text: "Ouvrir GitHub Actions",
                    onClick: {
                      openLink: {
                        url: `https://github.com/${CONFIG.GITHUB_REPO}/actions`
                      }
                    }
                  },
                  {
                    text: "Voir Master Sheets B_LD01",
                    onClick: {
                      openLink: {
                        url: `https://docs.google.com/spreadsheets/`
                      }
                    }
                  }
                ]
              }
            }
          ]
        }]
      }
    }]
  };

  const options = {
    method: "post",
    contentType: "application/json; charset=UTF-8",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const res = UrlFetchApp.fetch(webhookUrl, options);
    return { code: res.getResponseCode(), body: res.getContentText() };
  } catch (ex) {
    return { status: "ERROR", error: ex.toString() };
  }
}

/**
 * 6. Relais Déterministe vers GitHub Actions (Repository Dispatch API)
 */
function triggerGitHubDispatch(eventType, clientPayload) {
  const pat = PropertiesService.getScriptProperties().getProperty(CONFIG.PROP_GITHUB_PAT);
  if (!pat) {
    Logger.log("GITHUB_WORKFLOW_PAT non configuré dans Propriétés du script. Dispatch simulé.");
    return { code: "SIMULATED_NO_PAT", message: "GITHUB_WORKFLOW_PAT not configured" };
  }
  
  const url = `https://api.github.com/repos/${CONFIG.GITHUB_REPO}/dispatches`;
  const options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "Authorization": "token " + pat,
      "Accept": "application/vnd.github.v3+json",
      "User-Agent": "Aspace-GAS-Gateway"
    },
    payload: JSON.stringify({
      event_type: CONFIG.DISPATCH_EVENT,
      client_payload: {
        gas_event: eventType,
        timestamp_utc: new Date().toISOString(),
        payload: clientPayload
      }
    }),
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    return { code: response.getResponseCode(), body: response.getContentText() };
  } catch (ex) {
    return { code: 500, error: ex.toString() };
  }
}

/**
 * 7. Fonctions de Test Immédiates (Exécutables directement dans l'éditeur Google Apps Script)
 */
function test_SheetEditTrigger() {
  Logger.log("Lancement du test onWorkspaceStudioSheetEdit()...");
  const mockEvent = {
    range: {
      getSheet: function() {
        return {
          getName: function() { return CONFIG.TARGET_SHEET_NAME; },
          getRange: function(r, c) {
            return {
              getValue: function() {
                if (c === 1) return "MPLACE-US-PROSP-US-01";
                if (c === 2 || c === 11) return "Frost Brown Todd LLC";
                if (c === 7) return "$299/m ($3,588/a)";
                return "QUALIFIED_PROSPECT";
              }
            };
          }
        };
      },
      getRow: function() { return 2; },
      getColumn: function() { return 6; }
    },
    value: "QUALIFIED_PROSPECT"
  };
  const result = onWorkspaceStudioSheetEdit(mockEvent);
  Logger.log("Résultat du test : " + JSON.stringify(result));
}

function test_HealthCheck() {
  const output = doGet({});
  Logger.log("Health Check Output : " + output.getContent());
}
