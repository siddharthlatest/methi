var yash = function createuser(mail){

         var querystring = require('querystring');
         var http = require('http');

         var post_domain = 'http://getappbin.com/';
         var post_port = 80;
         var post_path = 'loadapp/createuser.php';

         var post_data = querystring.stringify({
         'hash' : 'thisishash',
         'email': mail
         });
		console.log("inside yash");
         var post_options = {
			 host: post_domain,
			 port: post_port,
			 path: post_path,
			 method: 'POST', 
			 headers: {
			   'Content-Type': 'application/x-www-form-urlencoded',
			   'Content-Length': post_data.length
			 }
         };

         var post_req = http.request(post_options, function(res) {
			 res.setEncoding('utf8');
			 res.on('data', function (chunk) {
			 console.log('Response: ' + chunk);
			 });
         });

         // write parameters to post body
         post_req.write(post_data);
         post_req.end();

};