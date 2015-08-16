 $(document).ready(function() {
 	$.ajaxSetup({
      crossDomain: true,
      xhrFields: {
        withCredentials: true
      }
    });

    $.ajax({
      type: "GET",
      url: 'https://accapi.appbase.io/user',
      dataType: 'json',
      contentType: "application/json",
      success: function(full_data) {
      },
      error:function(){
      	window.location.href = "index.html";
      }
    });

 	function body_height() {
 		var window_height = $(window).height();
 		$('body').css('height', window_height);
 	}
 	$(window).resize(function() {
 		body_height();
 	});
 	body_height();
 });