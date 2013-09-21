function checkResize(){
	var box = $(".app-info");
	var h = box.height();
	var w = box.width();
//	console.log("Height: " + h + "Width: " + w);
	setTimeout(checkResize,500);
	$(".upperInfo").css({
		"height":h/3 +'px',
		"width":"100%"
	});
	$(".app-small-icon").css({
		"height":"100%",
		"width":w/4+'px',
		"float":"left"
	});
	$(".app-micro-info").css({
		"width":(3*w/4 - 5) +'px',
		"height": h/4+"px" ,
		"float":"right"
	});
	$(".app-small-icon > img").css({
		"height":"100%"
	});
	$(".app-micro-description").css({
		"min-height": h/2.8+'px',
		"max-height": h/2.8+'px',
		"width" : w +'px',
		"margin-top" : "5px",
		"padding-top":"5px",
		"overflow-y":"auto",
		"margin-bottom":"3px"
		});
	$(".app-info").css({
		
	});
	$("h6").css({
		"margin-bottom":"0px"
	});
	$(".buttons").css({
		"margin-top":"4px"
	});
}
setTimeout(checkResize,500);
