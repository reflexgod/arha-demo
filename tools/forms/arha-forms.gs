/**
 * Arha Dental Care: website forms -> Google Sheet + email.
 *
 * Setup (once, in the Google account that should own the leads):
 *  1. Create a Google Sheet "Arha website enquiries". Extensions > Apps Script. Paste this file.
 *  2. Project Settings > Script properties:
 *       NOTIFY_TO         email address(es) that receive each enquiry (comma separated)
 *       TURNSTILE_SECRET  Cloudflare Turnstile secret key (leave empty only while testing)
 *  3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Copy the /exec URL
 *     into content/site.yaml -> forms_endpoint, rebuild and redeploy the site.
 *  Re-deploy (Manage deployments > Edit > New version) after any change to this file.
 */
var SHEET_NAME = 'Enquiries';
var FIELDS = ['form', 'name', 'phone', 'email', 'patient', 'treatment', 'when', 'message', 'page'];

function doPost(e) {
  try {
    var p = (e && e.parameter) || {};
    if (p.company) return json_({ ok: true }); // honeypot: pretend success
    if (!p.name || !p.phone || p.consent !== 'yes') return json_({ ok: false, error: 'missing' });
    var props = PropertiesService.getScriptProperties();
    var secret = props.getProperty('TURNSTILE_SECRET');
    if (secret && !turnstileOk_(secret, p['cf-turnstile-response'])) return json_({ ok: false, error: 'spam-check' });

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) sh.appendRow(['Received'].concat(FIELDS));
    var row = [new Date()].concat(FIELDS.map(function (f) { return clean_(p[f]); }));
    sh.appendRow(row);

    var to = props.getProperty('NOTIFY_TO');
    if (to) {
      var body = FIELDS.map(function (f) { return f + ': ' + clean_(p[f]); }).join('\n');
      MailApp.sendEmail({ to: to, subject: 'Website ' + clean_(p.form) + ': ' + clean_(p.name), body: body,
        replyTo: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.email || '') ? p.email : undefined });
    }
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: 'server' });
  }
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
