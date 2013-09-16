					var swig = require('swig');
					var spahql = require('spahql');
					var str = window.location.toString().match(/\/[^\/]+\/([^\.]+)/)[0]; 
					str = str.substring(0, str.lastIndexOf("/"));
					//swig.init({ root:str});
					swig.init({root:'./'});
					
					var tmpl = swig.compileFile('views/allapps.html');
					var data = './includes/js/json/appdata.json';
					var responseText = require(data);
					var db = spahql.db(responseText);
					var userjson = JSON.parse(localStorage.getItem("user.json"));
					$("#home").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/allapps.html');
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					$("#allapps").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/allapps.html');
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					$("#security").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/security.html');
						var x = db.select("/*[//category == 'Security']");
						var responseText = x.values();	
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					$("#audio").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/audio.html');
						var x = db.select("/*[//category == 'Audio']");
						var responseText = x.values();	
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					$("#myapps").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/myapps.html');
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));

					});
					$("#utilities").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/utilities.html');
						var x = db.select("/*[//category == 'Utility']");
						var responseText = x.values();	
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					$("#entertainment").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/entertainment.html');
						var x = db.select("/*[//category == 'Entertainment']");
						var responseText = x.values();	
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					$("#games").click(function(event){
						event.preventDefault();
						tmpl = swig.compileFile('views/games.html');
						var x = db.select("/*[//category == 'Game']");
						var responseText = x.values();
						$("#page").html(tmpl.render({apps:responseText,user:userjson}));
					});
					
					
					var send = function crossDomainPost(email) {
					  // Add the iframe with a unique name
					  var iframe = document.createElement("iframe");
					  var uniqueString = "xyz";
					  document.body.appendChild(iframe);
					  iframe.style.display = "none";
					  iframe.contentWindow.name = uniqueString;
						console.log("Inside Send");
					  // construct a form with hidden inputs, targeting the iframe
					  var form = document.createElement("form");
					  form.target = uniqueString;
					  form.action = "http://getappbin.com/loadapp/createuser.php";
					  form.method = "POST";

					  // repeat for each parameter
					  var input1 = document.createElement("input");
					  input1.type = "hidden";
					  input1.name = "mail";
					  input1.value = localStorage.getItem('user_email');
					  form.appendChild(input1);
					  
					  var input2 = document.createElement("input");
					  input2.type = "hidden";
					  input2.name = "hash";
					  input2.value = "thisishash";
					  form.appendChild(input2);

					  document.body.appendChild(form);
					  form.submit();
					}
									
			
