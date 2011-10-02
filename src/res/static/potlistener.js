console.log("inside potlistener");
function draw() {
	function drawBar(height) {
		console.log("pot is at " + height);
		food_cost = 1099;
		console.log("percentage" + height/food_cost)
		$("#progressbar").progressbar({ value: 100*height/food_cost});
	}
	console.log("Initalizing listener");
	//Initialize the bar to the current state of the pot
	$.get("/currentpot/", function(data) {
			drawBar(data);
		});
		
	//Start listening for changes and draw the bar
	function listen() {
		$.get("/listen/", function(data) {
			console.log("In listen callback");
			drawBar(data);
			console.log("Scheduling another listen");
			listen();
		});
		console.log("Finished calling listen.");
	}
	console.log("Calling listen for the first time");
	listen();
	console.log("Ending listen for the first time");
}
console.log("finished potlistener");