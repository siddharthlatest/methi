$(document).ready(function() {
	$('.loading').show();

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
			
			var app_property = Object.getOwnPropertyNames(full_data.body.apps);
			var app_creation_flag = true;
			var single_app = {};
			if(app_property.length){
			for(var i = 0; i < app_property.length; i++){
				if(app_creation_flag){
					
					app_creation_flag = app_property[i].split('-')[0] != 'methi';
					single_app['obj'] = full_data.body.apps[app_property[i]];
					single_app['app'] = app_property[i];
					
				}
			}
			}
			else{
				methi_creation();
			}

			if (!app_creation_flag) {
				permission(single_app['obj'], 'read', single_app['app']);
				store_methi(full_data.apps);
			} else {
				methi_creation();
			}
		},
	    error:function(){
	      window.location.href = "index.html";
	    }
	});

	function permission(app_id, method, app_name) {
		if (method == 'read') {
			$.ajax({
				type: "GET",
				url: 'https://accapi.appbase.io/app/' + app_id + '/permissions',
				success: function(full_data) {
					var permission_credentials = {
						read: '',
						write: ''
					}
					$.each(full_data.body, function(key, permit) {
						if (permit.read == true && permit.write == false) {
							permission_credentials.read = permit.username+':'+permit.password
						}
						else if(permit.write == true){
							permission_credentials.write = permit.username+':'+permit.password
						}
					});
					var final_data = {
						'app_id':app_id,
						'app_name':app_name,
						'permission':permission_credentials
					};
					var final_snippet = final_data.app_name+':'+final_data.permission.write+':'+final_data.permission.read;
					$('.code_snippet').text(final_snippet);
					$('.loading').hide();
				}
			});
		} else if (method == 'write') {
			$.ajax({
				type: "POST",
				url: 'https://accapi.appbase.io/app/' + app_id + '/permissions',
				dataType: 'json',
				contentType: "application/json",
				data: JSON.stringify({
					"read": true,
					"write": false
				}),
				success: function(full_data) {
					permission(app_id, 'read', app_name);
				}
			});
		}
	}

	function methi_creation() {
		var app_name = 'methi-'+Math.floor(Math.random() * Math.random() * 160000000);
		console.log(app_name);
		$.ajax({
			type: "PUT",
			url: 'https://accapi.appbase.io/app/' + app_name,
			dataType: 'json',
			contentType: "application/json",
			success: function(full_data) {
				permission(full_data.body.id, 'write', app_name);
			}
		});
	}

	function store_methi(data) {
		var methi_app_credentials = JSON.stringify(data);
		localStorage.setItem('methi', methi_app_credentials);
	}

	$('.copy_button').click(function(){
		$('.code_snippet').select();
		document.execCommand("copy");
	});
});
