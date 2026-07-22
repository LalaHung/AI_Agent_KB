function getSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Grades");
  if (!sheet) {
    sheet = ss.insertSheet("Grades");
    sheet.appendRow(["id", "student_id", "name", "subject", "score", "exam_date", "remarks", "created_at"]);
    // format headers
    sheet.getRange("A1:H1").setFontWeight("bold").setBackground("#e0e0e0");
  }
  return sheet;
}

function doGet(e) {
  try {
    var sheet = getSheet();
    var data = sheet.getDataRange().getValues();
    var headers = data[0];
    var jsonArray = [];
    
    for (var i = 1; i < data.length; i++) {
      var row = data[i];
      var record = {};
      for (var j = 0; j < headers.length; j++) {
        var value = row[j];
        if (value instanceof Date) {
          // Format date as YYYY-MM-DD
          var year = value.getFullYear();
          var month = ('0' + (value.getMonth() + 1)).slice(-2);
          var date = ('0' + value.getDate()).slice(-2);
          // If it is the exam_date column, keep it short
          if (headers[j] === "exam_date") {
            value = year + "-" + month + "-" + date;
          } else {
            value = value.toISOString();
          }
        }
        record[headers[j]] = value;
      }
      jsonArray.push(record);
    }
    
    // Sort by created_at descending
    jsonArray.sort(function(a, b) {
      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    });

    return ContentService.createTextOutput(JSON.stringify(jsonArray))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    var postData = JSON.parse(e.postData.contents);
    var action = postData.action;
    var sheet = getSheet();
    var data = sheet.getDataRange().getValues();
    var headers = data[0];
    
    if (action === "create") {
      var id = Utilities.getUuid();
      var student_id = postData.student_id;
      var name = postData.name;
      var subject = postData.subject;
      var score = Number(postData.score);
      var exam_date = postData.exam_date; // YYYY-MM-DD string
      var remarks = postData.remarks || "";
      var created_at = new Date().toISOString();
      
      sheet.appendRow([id, student_id, name, subject, score, exam_date, remarks, created_at]);
      return ContentService.createTextOutput(JSON.stringify({ status: "success", data: { id: id } }))
        .setMimeType(ContentService.MimeType.JSON);
        
    } else if (action === "update") {
      var id = postData.id;
      var rowIndex = -1;
      
      // Find row index (1-based)
      for (var i = 1; i < data.length; i++) {
        if (data[i][0] === id) {
          rowIndex = i + 1;
          break;
        }
      }
      
      if (rowIndex === -1) {
        return ContentService.createTextOutput(JSON.stringify({ status: "error", message: "Record not found" }))
          .setMimeType(ContentService.MimeType.JSON);
      }
      
      // Update fields
      sheet.getRange(rowIndex, 2).setValue(postData.student_id);
      sheet.getRange(rowIndex, 3).setValue(postData.name);
      sheet.getRange(rowIndex, 4).setValue(postData.subject);
      sheet.getRange(rowIndex, 5).setValue(Number(postData.score));
      sheet.getRange(rowIndex, 6).setValue(postData.exam_date);
      sheet.getRange(rowIndex, 7).setValue(postData.remarks || "");
      
      return ContentService.createTextOutput(JSON.stringify({ status: "success" }))
        .setMimeType(ContentService.MimeType.JSON);
        
    } else if (action === "delete") {
      var id = postData.id;
      var rowIndex = -1;
      
      for (var i = 1; i < data.length; i++) {
        if (data[i][0] === id) {
          rowIndex = i + 1;
          break;
        }
      }
      
      if (rowIndex === -1) {
        return ContentService.createTextOutput(JSON.stringify({ status: "error", message: "Record not found" }))
          .setMimeType(ContentService.MimeType.JSON);
      }
      
      sheet.deleteRow(rowIndex);
      return ContentService.createTextOutput(JSON.stringify({ status: "success" }))
        .setMimeType(ContentService.MimeType.JSON);
        
    } else {
      return ContentService.createTextOutput(JSON.stringify({ status: "error", message: "Invalid action" }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
