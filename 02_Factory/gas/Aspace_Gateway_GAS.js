/**
 * A'Space OS V5 — 02_Factory/gas/Aspace_Gateway_GAS.js
 * ====================================================
 * Passerelle Souveraine Google Apps Script (GAS) & Déclencheurs Workspace Studio.
 * Transforme le compute Cloud Google gratuit (6 min/run, 90 min CPU/jour)
 * en nœud d'exécution serverless relié à A'Space OS V5 (GitHub Actions n8n & FreeCloud Gateway).
 *
 * À coller directement dans https://script.google.com/ (Projet Aspace_Gateway_GAS).
 */

const CONFIG = {
  GITHUB_REPO: "Amdkn/Aspace_OS_V5",
  DISPATCH_EVENT: "gws_webhook_trigger",
  // Stocker le secret GITHUB_PAT dans Propriétés du script (Fichier > Paramètres du projet)
  PAT_PROPERTY: "GITHUB_WORKFLOW_PAT",
  SECRET_SALT: "ASPACE_GAS_HMAC_SALT",
};

/**
 * 1. Webhook d'Entrée HTTP (doPost) : Reçoit des payloads externes (Retool, Zapier, Zenphi, GKit)
 */
function doPost(e) {
  try {
    const rawData = e.postData ? e.postData.contents : "{}";
    const payload = JSON.parse(rawData);
    
    // Routage vers GitHub Actions n8n Primitive
    const result = triggerGitHubDispatch(payload.event_type || "gas_http_trigger", payload);
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "SUCCESS",
      gateway: "Aspace_GAS_FreeCompute",
      cpu_time_used_estimate_sec: 0.12,
      github_dispatch_status: result.code,
      timestamp: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "ERROR",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 2. Ping de Santé & Lecture Quotas (doGet)
 */
function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    gateway: "Aspace_GAS_FreeCompute",
    service: "Google Apps Script Serverless Worker",
    daily_cpu_limit_minutes: 90,
    max_execution_time_minutes: 6,
    url_fetch_daily_quota: 20000,
    status: "ONLINE_READY",
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

/**
 * 3. Déclencheurs Natifs Workspace Studio (Événements GWS -> GitHub Actions)
 */

// Déclenché par Workspace Studio : "Lorsqu'une feuille est modifiée" (Google Sheets)
function onWorkspaceStudioSheetEdit(e) {
  const sheet = e.range.getSheet();
  const eventData = {
    source: "Workspace_Studio_Sheet_Edit",
    sheet_name: sheet.getName(),
    row: e.range.getRow(),
    col: e.range.getColumn(),
    value: e.value || "",
    area: sheet.getName().startsWith("B_LD01") ? "LD01" : "AREAS_OS"
  };
  triggerGitHubDispatch("sheets_cell_modified", eventData);
}

// Déclenché par Workspace Studio : "À réception d'une réponse à un formulaire" (Google Forms / Leads OMK)
function onWorkspaceStudioFormSubmit(e) {
  const responses = e.namedValues || {};
  const eventData = {
    source: "Workspace_Studio_Form_Submit",
    form_responses: responses,
    area: "LD01_OMK_LEADS"
  };
  triggerGitHubDispatch("form_lead_captured", eventData);
}

// Déclenché par Workspace Studio : "Lorsqu'un élément est ajouté à un dossier" (Drive 5TB CAS)
function onWorkspaceStudioDriveFileAdded(folderId, fileName) {
  const eventData = {
    source: "Workspace_Studio_Drive_File_Added",
    folder_id: folderId,
    file_name: fileName,
    tier: "GOOGLE_DRIVE_5TB_CAS_BUCKET"
  };
  triggerGitHubDispatch("drive_5tb_new_asset", eventData);
}

/**
 * 4. Relais Déterministe vers GitHub Actions (Repository Dispatch API)
 */
function triggerGitHubDispatch(eventType, clientPayload) {
  const pat = PropertiesService.getScriptProperties().getProperty(CONFIG.PAT_PROPERTY);
  if (!pat) {
    return { code: "SIMULATED_NO_PAT", message: "GITHUB_WORKFLOW_PAT not configured in Script Properties" };
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
  
  const response = UrlFetchApp.fetch(url, options);
  return { code: response.getResponseCode(), body: response.getContentText() };
}
