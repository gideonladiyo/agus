/**
 * Cara Pasang (Tanpa Perlu Google Cloud Service Account):
 * 1. Buka Google Sheet: https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/edit#gid=501567643
 * 2. Klik menu Extensions > Apps Script
 * 3. Paste kode di bawah ini ke Code.gs, lalu Save (Ctrl+S)
 * 4. Klik Deploy > New deployment > Pilih type: "Web app"
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 5. Klik Deploy, salin Web App URL-nya, lalu masukkan ke file .env:
 *    WZ_APPS_SCRIPT_URL=https://script.google.com/macros/s/XXXX/exec
 */

function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    var targetGid = Number(payload.gid || 501567643);
    var updates = payload.updates || {};

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheets().filter(function(s) {
      return s.getSheetId() === targetGid;
    })[0];

    if (!sheet) {
      return ContentService.createTextOutput(
        JSON.stringify({ status: "error", message: "Sheet gid " + targetGid + " not found" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    Object.keys(updates).forEach(function(cellA1) {
      var val = updates[cellA1];
      var range = sheet.getRange(cellA1);
      if (typeof val === "string" && val.indexOf("=") === 0) {
        range.setFormula(val);
      } else {
        range.setValue(val);
      }
    });

    SpreadsheetApp.flush();

    return ContentService.createTextOutput(
      JSON.stringify({ status: "ok", updated: Object.keys(updates).length })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: String(err) })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
