console.log("inside potlistener");
function draw() {
	var ctx = document.getElementById('canvas').getContext('2d');
	function drawBar(height) {
		food_cost = 1000;
		full_bar_height = 300;
		multiplier = full_bar_height/food_cost;
		height *= multiplier;
		ctx.clearRect(0,0, canvas.width, canvas.height);
		ctx.fillStyle = "rgb(100,100,100)";
		ctx.fillRect(0,300-height,10,height);
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