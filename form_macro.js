var POST_URL = "https://lpoipu7n36.execute-api.us-west-2.amazonaws.com/default/create-freshservice-ticket";

function onSubmit(e) {
  var form = FormApp.getActiveForm();
  var allResponses = form.getResponses();
  var latestResponse = allResponses[allResponses.length - 1];
  var response = latestResponse.getItemResponses();
  var answers = {};

  var description = ""
  for (var i = 0; i < response.length; i++) {
      var question = response[i].getItem().getTitle();
      var answer = response[i].getResponse();
      answers[question] = answer;
      var newline = Utilities.formatString('%s: %s<br><br>', question, answer)
      description += newline
  }
  description = description.slice(0, -8)

  // Data validation
  
  //  First response is within 24 hours of ticket creation
  //  Due by date must be greater than first response
  var due_by_submitted = new Date(answers["When is the project needed?"])
  var fr_due_by = new Date(new Date().getTime() + 60 * 60 * 24 * 1000)
  var due_by = new Date(Math.max(due_by_submitted, fr_due_by))

  var payload = {
    'name' : answers['Contact Info: Name'],
    'email' : answers['Contact Info: Email'],
    'due_by' :  due_by.toISOString(),
    'fr_due_by' : fr_due_by.toISOString(),
    'type' : 'Incident',
    'status' : 2,
    'priority' : parseInt(answers['Priority']),
    'description' : description,
    'subject' : answers['Request: Brief Description or Title'],
    'tags' : [
      'source:google-forms',
      'request',
      ]
  };

  var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload)
  };
  
  UrlFetchApp.fetch(POST_URL, options);
};

function date_test(){
  var t = new Date()
  t.setHours(23,59,59,999)
  Logger.log(t)
}