var hook = require('hooks');

hook.before("Question > Questions collection > Create a new question", function(transaction) {
  // Configure the location header to be the correct URI (localhost)
  transaction.expected.headers["Location"] = "http://localhost:8000/questions/2";
});

hook.before("Question > Questions collection > List all questions", function(transaction) {
  // Let's ignore the link header, it depends on multiple pages of questions
  delete transaction.expected.headers["Link"];
});
