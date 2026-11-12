/**
 * Arha Dental Care: website forms -> Google Sheet + email (+ Drive for referral attachments).
 *
 * Setup (once, in the Google account that should own the leads):
 *  1. Create a Google Sheet "Arha website enquiries". Extensions > Apps Script. Paste this file.
 *  2. Project Settings > Script properties:
 *       NOTIFY_TO            email address(es) that receive each enquiry (comma separated)
 *       TURNSTILE_SECRET     Cloudflare Turnstile secret key (leave empty only while testing)
 *       REFERRALS_FOLDER_ID  ID of a private Drive folder for referral attachments (the part after /folders/ in its URL)
 *       SHEET_ID             ID of the "Arha website enquiries" Sheet (the part after /d/ in its URL). Used by ss_();
 *                            falls back to the spreadsheet the script is bound to.
 *       XRAY_FOLDER_ID       ID of a private Drive folder for X-rays sent by international patients (falls back to
 *                            REFERRALS_FOLDER_ID if empty)
 *  3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Copy the /exec URL
 *     into content/site.yaml -> forms_endpoint, rebuild and redeploy the site.
 *     The first run asks for Sheets, Gmail (MailApp), Drive and external-request permissions.
 *  Re-deploy (Manage deployments > Edit > New version) after any change to this file.
 *
 * Referrals and X-ray uploads carry patient health data. Keep the Sheet and the folder private (never "anyone with the link"),
 * and at launch move both to an account the clinic owns.
 */
var SHEET_NAME = 'Enquiries';
var FIELDS = ['form', 'name', 'phone', 'email', 'concern', 'treatment', 'message', 'marketing', 'page'];
var REF_SHEET = 'Referrals';
var REF_FIELDS = ['name', 'practice', 'practice_address', 'email', 'phone', 'registration', 'patient_name', 'patient_dob',
  'patient_phone', 'patient_email', 'treatment', 'urgent', 'purpose', 'complaint', 'history', 'self_treat', 'message', 'page'];
var MAX_FILES = 3;
var MAX_BYTES = 4 * 1024 * 1024;
var FILE_TYPES = { 'application/pdf': 1, 'image/jpeg': 1, 'image/png': 1 };
var XRAY_SHEET = 'International uploads';
var XRAY_FIELDS = ['name', 'email', 'phone', 'country', 'message', 'marketing', 'page'];
var XRAY_MAX_BYTES = 10 * 1024 * 1024;
var XRAY_TYPES = { 'application/pdf': 1, 'image/jpeg': 1, 'image/png': 1, 'application/zip': 1,
  'application/x-zip-compressed': 1, 'application/dicom': 1 };

function doPost(e) {
  try {
    var p = (e && e.parameter) || {};
    if (p.company) return json_({ ok: true }); // honeypot: pretend success
    if (!p.name || !p.phone || p.consent !== 'yes') return json_({ ok: false, error: 'missing' });
    var props = PropertiesService.getScriptProperties();
    var secret = props.getProperty('TURNSTILE_SECRET');
    if (secret && !turnstileOk_(secret, p['cf-turnstile-response'])) return json_({ ok: false, error: 'spam-check' });
    if (p.form === 'referral') return referral_(p, props);
    if (p.form === 'xray') return xray_(p, props);

    var sh = sheet_(SHEET_NAME, ['Received'].concat(FIELDS));
    sh.appendRow([new Date()].concat(FIELDS.map(function (f) { return clean_(p[f]); })));
    notify_(props, 'Website ' + clean_(p.form) + ': ' + clean_(p.name),
      FIELDS.map(function (f) { return f + ': ' + clean_(p[f]); }).join('\n'), p.email);
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: 'server' });
  }
}

function referral_(p, props) {
  if (!p.patient_name || !p.history) return json_({ ok: false, error: 'missing' });
  var links = [];
  var folderId = props.getProperty('REFERRALS_FOLDER_ID');
  for (var i = 1; i <= MAX_FILES; i++) {
    var data = p['file' + i + '_data'];
    if (!data) continue;
    var type = String(p['file' + i + '_type'] || '');
    if (!FILE_TYPES[type]) return json_({ ok: false, error: 'file-type' });
    var bytes = Utilities.base64Decode(data);
    if (bytes.length > MAX_BYTES) return json_({ ok: false, error: 'file-size' });
    if (!folderId) { links.push('(file not saved: REFERRALS_FOLDER_ID is not set)'); continue; }
    var safeName = String(p['file' + i + '_name'] || ('file' + i)).replace(/[^\w.\- ]/g, '_').slice(0, 100);
    var stamp = Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyyy-MM-dd HHmm');
    var blob = Utilities.newBlob(bytes, type, stamp + ' ' + clean_(p.patient_name).slice(0, 40) + ' - ' + safeName);
    links.push(DriveApp.getFolderById(folderId).createFile(blob).getUrl()); // inherits the folder's (private) sharing
  }
  var sh = sheet_(REF_SHEET, ['Received'].concat(REF_FIELDS, ['files']));
  sh.appendRow([new Date()].concat(REF_FIELDS.map(function (f) { return clean_(p[f]); }), [links.join('\n')]));
  // The email carries only who referred whom and a pointer to the Sheet; clinical details stay in the Sheet.
  notify_(props, 'New referral from ' + clean_(p.name) + (p.urgent === 'Urgent' ? ' (URGENT)' : ''),
    'Referring dentist: ' + clean_(p.name) + ', ' + clean_(p.practice) + '\nPhone: ' + clean_(p.phone) + '\nEmail: ' + clean_(p.email) +
    '\nReferral for: ' + clean_(p.treatment) + '\nUrgency: ' + clean_(p.urgent) + '\nFiles: ' + links.length +
    '\n\nFull details are in the "' + REF_SHEET + '" tab: ' + ss_().getUrl(), p.email);
  return json_({ ok: true });
}

// International patients' X-rays, scans or photos -> private Drive folder + sheet row. The email says only who sent
// how many files and points to the Sheet: no clinical details, no message text.
function xray_(p, props) {
  if (!p.email || !p.file1_data) return json_({ ok: false, error: 'missing' });
  var folderId = props.getProperty('XRAY_FOLDER_ID') || props.getProperty('REFERRALS_FOLDER_ID');
  var links = [];
  for (var i = 1; i <= MAX_FILES; i++) {
    var data = p['file' + i + '_data'];
    if (!data) continue;
    var type = String(p['file' + i + '_type'] || '');
    if (!XRAY_TYPES[type]) return json_({ ok: false, error: 'file-type' });
    var bytes = Utilities.base64Decode(data);
    if (bytes.length > XRAY_MAX_BYTES) return json_({ ok: false, error: 'file-size' });
    if (!folderId) { links.push('(file not saved: XRAY_FOLDER_ID is not set)'); continue; }
    var safeName = String(p['file' + i + '_name'] || ('file' + i)).replace(/[^\w.\- ]/g, '_').slice(0, 100);
    var stamp = Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyyy-MM-dd HHmm');
    var blob = Utilities.newBlob(bytes, type, stamp + ' ' + clean_(p.name).slice(0, 40) + ' - ' + safeName);
    links.push(DriveApp.getFolderById(folderId).createFile(blob).getUrl()); // inherits the folder's (private) sharing
  }
  var sh = sheet_(XRAY_SHEET, ['Received'].concat(XRAY_FIELDS, ['files']));
  sh.appendRow([new Date()].concat(XRAY_FIELDS.map(function (f) { return clean_(p[f]); }), [links.join('\n')]));
  notify_(props, 'International patient upload: ' + clean_(p.name),
    'From: ' + clean_(p.name) + ' (' + clean_(p.country) + ')\nPhone: ' + clean_(p.phone) + '\nEmail: ' + clean_(p.email) +
    '\nFiles: ' + links.length + '\n\nDetails and file links are in the "' + XRAY_SHEET + '" tab: ' +
    ss_().getUrl(), p.email);
  return json_({ ok: true });
}

// The leads spreadsheet: SHEET_ID from Script properties (works for a standalone script too), else the bound one.
function ss_() {
  var id = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function sheet_(name, header) {
  var ss = ss_();
  var sh = ss.getSheetByName(name) || ss.insertSheet(name);
  if (sh.getLastRow() === 0) sh.appendRow(header);
  return sh;
}

function notify_(props, subject, body, replyTo) {
  var to = props.getProperty('NOTIFY_TO');
  if (!to) return;
  MailApp.sendEmail({ to: to, subject: subject, body: body,
    replyTo: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(replyTo || '') ? replyTo : undefined });
}

function turnstileOk_(secret, token) {
  if (!token) return false;
  var r = UrlFetchApp.fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'post', payload: { secret: secret, response: token }, muteHttpExceptions: true });
  try { return JSON.parse(r.getContentText()).success === true; } catch (e) { return false; }
}

function clean_(v) {
  v = String(v == null ? '' : v).slice(0, 2000);
  return /^[=+\-@]/.test(v) ? "'" + v : v; // stop spreadsheet formula injection
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
