var appbase_app = function() {
	var $this = this;
	return {
		initialize: initialize
	};

	function initialize(options) {

		//Initialize Variables Start
		$this.default_options = {
			title: 'Blazing fast search on your Documentation',
			input_placeholder: 'search here',
			logo: 'images/Appbase.png',
			abbr: 'appbase_',
			selector: '.appbase_external_search'
		};

		//Variable js		
		var options = $.extend($this.default_options, options);
		$this.variables = new variables(options.credentials, options.app_name, options.index_document_type, 'client');
		$this.url = $this.variables.createURL();
		$this.appbase_total = 0;
		$this.appbase_increment = $this.variables.SIZE;
		$this.size = $this.appbase_increment;
		$this.appbase_xhr_flag = true;
		$this.search_payload = $this.variables.SEARCH_PAYLOAD;
		$.ajaxSetup({
			crossDomain: true,
			xhrFields: {
				withCredentials: true
			}
		});
		function scroll_callback(full_data, method, initialize) {
			var hits = full_data.hits.hits;
			if(method == 'fuzzy')
			{
				jQuery('.tt-menu .tt-dataset.tt-dataset-my-dataset').html('');
				jQuery(".appbase_total_info").html($this.variables.showing_text($this.appbase_increment, $this.appbase_total, jQuery('.appbase_input').eq(1).val(), full_data.took));
	        }
			if(hits.length){
				$this.appbase_increment += hits.length;
		        for (var i = 0; i < hits.length; i++) {
	              var data = hits[i];
	              var single_record = $this.variables.createRecord(data);

	              //var single_record = '<div><a cla href="'+ data.fields.link +'">' + data.highlight.title + '</a><p> ' + data.highlight.body.join('...') + '...</p></div>';
	              
	              var tt_record = jQuery('<div>').addClass('tt-suggestion tt-selectable').html(single_record);
	              jQuery('.tt-menu .tt-dataset.tt-dataset-my-dataset').append(tt_record);
	            }
            	$this.appbase_xhr_flag = true;
			}
			else{
				jQuery(".appbase_total_info").html($this.variables.NO_RESULT_TEXT);
				jQuery('.tt-menu .tt-dataset.tt-dataset-my-dataset').html('');
			}

			if(initialize == 'initialize'){
				$this.appbase_total = full_data.hits.total;
				jQuery(".appbase_total_info").html($this.variables.showing_text($this.appbase_increment, full_data.hits.total , jQuery('.appbase_input').eq(1).val(), full_data.took));
	        }
		}
		//Initialize Variables End

		//Bloodhound Start
		$this.engine = $this.variables.createEngine($this, function(length){
			$this.appbase_total = length;
			if(length)
				$this.appbase_xhr_flag = true;
			else
		    	$this.appbase_xhr_flag = false;
		}, scroll_callback);
		//Bloodhound End

		//Fire CreateHtml
		createHtml(options);

		//CreateHtml Start
		function createHtml(obj) {
			var abbr = obj.abbr;
			var title = jQuery('<h1>').addClass(abbr + 'title').html(obj.title);
			var input_box = jQuery('<input>').addClass(abbr + 'input').attr({
				'type': 'text',
				'placeholder': obj.input_placeholder
			});
			var app_logo = jQuery('<img>').addClass(abbr + 'logo').attr({
				'src': obj.logo
			});
			var search_box = jQuery('<div>').addClass(abbr + 'search_box').append(input_box).append(app_logo);
			var search_box_container = jQuery('<div>').addClass(abbr + 'search_box').append(search_box);
			var modal_content = jQuery('<div>').addClass(abbr + 'modal_content').append(search_box_container);
			var overlay = jQuery('<div>').addClass(abbr + 'overlay');
			var modal = jQuery('<div>').addClass(abbr + 'modal').append(modal_content).append(overlay);
			jQuery('body').append(modal);

			//Bind events with html
			html_events(obj, modal, overlay);
		};

		function html_size(obj, modal) {
			function appbase_resize() {
				var win_height = jQuery(window).height();
				var win_width = jQuery(window).width();
				var modal_height = win_width < 768 ? win_height : win_height - 150;
				var tt_height = modal_height - jQuery('.' + obj.abbr + 'input').height() - 50;
				jQuery('.tt-menu').height(tt_height);
				jQuery(modal).find('.' + obj.abbr + 'modal_content').height(modal_height);
				if(win_width < 768){
					jQuery(modal).find('.' + obj.abbr + 'modal_content').css({'margin-top':0, 'max-width':'768px'});
				}
				else{
					jQuery(modal).find('.' + obj.abbr + 'modal_content').css('margin-top','50px');
				}
			}
			jQuery(window).resize(function() {
				appbase_resize();
			});
			appbase_resize();
		}
		function close_modal(){
			jQuery('.appbase_modal').fadeOut(150);
			jQuery('.appbase_overlay').fadeOut(150);
			jQuery('html,body').css('overflow','auto');
		}
		function html_events(obj, modal, overlay) {
			jQuery(modal).find('.' + obj.abbr + 'input').typeahead({
				minLength: 1,
				highlight: true,
				limit: 100,
				change: function() {
					alert('changed');
				}
			}, {
				name: 'my-dataset',
				limit: 100,
				source: $this.engine.ttAdapter(),
				templates: {
					pending:true,
					suggestion: function(data) {
						if(data)
						{
							var single_record = $this.variables.createRecord(data);
							return single_record;
						}
						else
							return;
					}
				}
			});

			jQuery(modal).find('.' + obj.abbr + 'input').on('keyup',function(){
				if(jQuery(this).val().length == 0)
					jQuery('.appbase_total_info').text($this.variables.INITIAL_TEXT);
			});

			jQuery(modal).find('.' + obj.abbr + 'input').bind('typeahead:select', function(ev, suggestion) {
				ev.preventDefault();
				console.log('Selection: ' + suggestion);
			});

			var total_info = jQuery('<span>').addClass(obj.abbr + 'total_info').html($this.variables.NO_RESULT_TEXT);
			var toggle_view = jQuery('<a>').addClass(obj.abbr + 'toggle_view').html('view');			
			var total_info_container = jQuery('<span>').addClass(obj.abbr + 'total_info_container').append(total_info).append(toggle_view);
			jQuery('.tt-menu').prepend(total_info_container);

			html_size(obj, modal);

			jQuery(obj.selector).on('keyup', function() {
				var input_val = jQuery(this).val();
				jQuery(modal).find('.' + obj.abbr + 'input').val(input_val);
				jQuery(modal).fadeIn(150);
				jQuery(modal).find('.' + obj.abbr + 'input').typeahead('val', '')
				jQuery(modal).find('.' + obj.abbr + 'input').focus().typeahead('val',input_val).focus();
				jQuery(overlay).show();
				jQuery(modal).find('.' + obj.abbr + 'input').focus();
				jQuery(this).val('');
				jQuery('html,body').css('overflow','hidden');
			});
			jQuery(document).keyup(function(e) {
				if (e.keyCode == 27) {
					close_modal()
				}
			});
			jQuery(overlay).on('click', function() {
				close_modal();
			});

			jQuery('.tt-menu').on('scroll', function() {
				if (jQuery(this).scrollTop() + jQuery(this).innerHeight() >= this.scrollHeight) {
					if ($this.appbase_total != 0 && $this.appbase_total > $this.appbase_increment && $this.appbase_xhr_flag) {
						$this.variables.scroll_xhr($this,'client', scroll_callback);
					}
				}
			});
			jQuery('.'+obj.abbr + 'logo').click(function(){
				close_modal();
			});
			jQuery(toggle_view).click(function(){
				$this.variables.VIEWFLAG = $this.variables.VIEWFLAG ? false:true;
				var input_val = jQuery(modal).find('.' + obj.abbr + 'input').eq(1).val();
				jQuery(modal).find('.' + obj.abbr + 'input').typeahead('val','').typeahead('val',input_val).focus();
			});

		}
		//CreateHtml End



	}
}

var Loader = function() {}
Loader.prototype = {
	require: function(scripts, callback) {
		this.loadCount = 0;
		this.totalRequired = scripts.length;
		this.callback = callback;

		for (var i = 0; i < scripts.length; i++) {
			var split_name = scripts[i].split('.');
			if (split_name[split_name.length - 1] == 'js')
				this.writeScript(scripts[i]);
			if (split_name[split_name.length - 1] == 'css')
				this.writeStylesheet(scripts[i]);
		}
	},
	loaded: function(evt) {
		this.loadCount++;

		if (this.loadCount == this.totalRequired && typeof this.callback == 'function') this.callback.call();
	},
	writeScript: function(src) {
		var self = this;
		var s = document.createElement('script');
		s.type = "text/javascript";
		s.async = true;
		s.src = src;
		s.addEventListener('load', function(e) {
			self.loaded(e);
		}, false);
		var head = document.getElementsByTagName('head')[0];
		head.appendChild(s);
	},
	writeStylesheet: function(src) {
		var self = this;
		var s = document.createElement('link');
		s.type = "text/css";
		s.rel = "stylesheet";
		s.href = src;
		s.addEventListener('load', function(e) {
			self.loaded(e);
		}, false);
		var head = document.getElementsByTagName('head')[0];
		head.appendChild(s);
	}
}

function meta_head(){
	var meta = document.createElement('meta');
	//meta.httpEquiv = "X-UA-Compatible";
	meta.content = "width=device-width, initial-scale=1";
	meta.name = 'viewport';
	document.getElementsByTagName('head')[0].appendChild(meta);
}
meta_head();
var jquery_js = new Loader();
jquery_js.require([
		"css/client.css",
		"https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"
	],
	function() {
		var typeahead_js = new Loader();
		typeahead_js.require([
				"js/typeahead.bundle.js",
				"js/variable.js"
			],
			function() {
				var appbase = new appbase_app();
				appbase.initialize({
					title: 'Blazing fast search1 on your Documentation',
					input_placeholder: 'search here',
					logo: 'images/Appbase.png',
					selector: '.appbase_external_search',
					credentials:appbase_variables.credentials,
					app_name:appbase_variables.app_name,
					index_document_type:appbase_variables.index_document_type
				});
			});
	});
