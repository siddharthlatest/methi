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
			if (app_property.length && app_property[0].split('-')[0] == 'methi') {
				permission(full_data.body.apps[app_property[0]], 'read');
				store_methi(full_data.apps);
				
			} else {
				methi_creation();
			}
		}
	});

	function permission(app_id, method) {
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
							permission_credentials.read = permit.password
						}
						else if(permit.write == true){
							permission_credentials.write = permit.password
						}
					});
					var final_data = {
						'app_id':app_id,
						'permission':permission_credentials
					};
					console.log(final_data);
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
					permission(app_id, 'read');
				}
			});
		}
	}

	function methi_creation() {
		var app_name = 'methi-1234571';
		$.ajax({
			type: "PUT",
			url: 'https://accapi.appbase.io/app/' + app_name,
			dataType: 'json',
			contentType: "application/json",
			success: function(full_data) {
				permission(full_data.body.id, 'write');
			}
		});
	}

	function store_methi(data) {
		var methi_app_credentials = JSON.stringify(data);
		localStorage.setItem('methi', methi_app_credentials);
	}


});