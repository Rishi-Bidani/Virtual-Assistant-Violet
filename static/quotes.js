// function getQuote() {
// 	fetch("../jokeTest/quotes.json")
// 		.then(function (response) {
// 			return response.json();
// 		})
// 		.then(function (data) {
// 			var index = Math.floor(Math.random() * 1000);
// 			console.log(data[index]);
// 			// console.log(data[index]["author"]);
// 			if (data[index]["author"] == null) {
// 				data[index]["author"] = "Anonymous";
// 			}
// 			document.getElementById("quote-text").innerHTML = data[index]["text"];
// 			document.getElementById("quote-author").innerHTML = data[index]["author"];
// 			setInterval(getQuote, 1000);
// 		});
// }

function getQuote() {
	//Works in LIVE SERVER
	$.getJSON("../static/quotes.json", function (data) {
		var index = Math.floor(Math.random() * 1000);
		var string_index = "quote" + index;
		if (data[string_index]["author"] == null) {
			data[string_index]["author"] = "Anonymous";
		}
		$("#quote-text").text(data[string_index]["text"]); // The quote display HTML ELEMENT must have ID = "quote-text"
		$("#quote-author").text("-" + data[string_index]["author"]); //  | Author display must have id = "quote-author"
	});
}

$(document).ready(function () {
	getQuote();
	setInterval(getQuote, 36000000);
	// setInterval(getQuote, 1000);
});
// getQuote();
