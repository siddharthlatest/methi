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
			selector: '.appbase_external_search',
			grid_view:false
		};

		//Variable js		
		var options = $.extend($this.default_options, options);
		$this.variables = new variables(options.credentials, options.app_name, options.index_document_type, 'client', options.grid_view);
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
			
			//Create Top info			
			var total_info = jQuery('<span>').addClass(obj.abbr + 'total_info').html($this.variables.NO_RESULT_TEXT);
			var list_thumb = jQuery('<img>').attr({src:$this.variables.LIST_THUMB});
			var grid_thumb = jQuery('<img>').attr({src:$this.variables.GRID_THUMB});
			var setting_thumb = jQuery('<img>').attr({src:$this.variables.GRID_THUMB});
			var list_thumb_container = jQuery('<span>').addClass('list_thumb appbase-thumbnail ').attr('title','List view').append(list_thumb);
			var grid_thumb_container = jQuery('<span>').addClass('grid_thumb appbase-thumbnail').attr('title','Grid view').append(grid_thumb);
			var setting_thumb_container = jQuery('<span>').addClass('setting_thumb appbase-thumbnail').attr('title','Filter').append(setting_thumb);
			var thumb_container = jQuery('<span>').addClass('appbase_thumb_container').append(grid_thumb_container).append(list_thumb_container);
			var total_info = jQuery('<span>').addClass(obj.abbr + 'total_info').html($this.variables.NO_RESULT_TEXT);
			var total_info_container = jQuery('<span>').addClass(obj.abbr + 'total_info_container').append(setting_thumb_container).append(total_info);
			if(options.grid_view){
				jQuery(grid_thumb_container).addClass('active');
				total_info_container.append(thumb_container);
			};
			obj.total_info_container = total_info_container;

			//Create Right info		
			//Date Range	
			var date_list = jQuery('<ul>').addClass('appabse_list date_list');
			for(var i =0; i < $this.variables.date.content.length; i++){
				var current_list = $this.variables.date.content[i];
				var single_list = jQuery('<li>').text(current_list.text).data('val',current_list.val);
				date_list.append(single_list);
			}
			var date_label = jQuery('<label>').text($this.variables.date.label);
			var date_list_container = jQuery('<div>').addClass('appbase_block').append(date_label).append(date_list);
			obj.date_list_container = date_list_container;

			//Brand
			var brand_list = jQuery('<ul>').addClass('appabse_list brand_list');
			var single_search = jQuery('<input>').attr({'type':'text','class':'appbase_brand_search','placeholder':$this.variables.brand.placeholder});
			var single_list = jQuery('<li>').append(single_search);
			brand_list.append(single_list);
			var brand_label = jQuery('<label>').text($this.variables.brand.label);
			var brand_list_container = jQuery('<div>').addClass('appbase_block').append(brand_label).append(brand_list);
			obj.brand_list_container = brand_list_container;
			

			var substringMatcher = function(strs) {
			  return function findMatches(q, cb) {
			    var matches, substringRegex;

			    // an array that will be populated with substring matches
			    matches = [];

			    // regex used to determine if a string contains the substring `q`
			    substrRegex = new RegExp(q, 'i');

			    // iterate through the pool of strings and for any string that
			    // contains the substring `q`, add it to the `matches` array
			    $.each(strs, function(i, str) {
			      if (substrRegex.test(str)) {
			        matches.push(str);
			      }
			    });

			    cb(matches);
			  };
			};

			var states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
			  'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii',
			  'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
			  'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
			  'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
			  'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
			  'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
			  'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
			  'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
			];

			jQuery(single_search).typeahead({
			  hint: true,
			  highlight: true,
			  minLength: 0
			},
			{
			  name: 'states',
			  source: substringMatcher(states)
			});
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
				jQuery('.appbase_side_container').height(tt_height);
				//jQuery(modal).find('.' + obj.abbr + 'modal_content').height(modal_height);
				if(win_width < 768){
					jQuery(modal).find('.' + obj.abbr + 'modal_content').css({'margin-top':0, 'max-width':'960px'});
				}
				else{
					jQuery(modal).find('.' + obj.abbr + 'modal_content').css({'margin-top':'50px', 'max-width':'960px'});
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
			
			var side_container = jQuery('<div>').addClass('appbase_side_container_inside').append(obj.date_list_container).append(obj.brand_list_container);
			var side_container_inside = jQuery('<div>').addClass('appbase_side_container').append(side_container);
			jQuery('.twitter-typeahead').prepend(obj.total_info_container).prepend(side_container_inside);

			html_size(obj, modal);

			jQuery(obj.selector).on('keyup', function() {
				var input_val = jQuery(this).val();
				jQuery(modal).find('.' + obj.abbr + 'input').val(input_val);
				jQuery(modal).fadeIn(150);
				jQuery(modal).find('.' + obj.abbr + 'input').typeahead('val', '')
				jQuery(modal).find('.' + obj.abbr + 'input').focus().typeahead('val',input_val).focus();
				jQuery('.appbase_brand_search').typeahead('val','').focus();
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

			//Top row events
			jQuery('.appbase_thumb_container .appbase-thumbnail').click(function(){
				if(!jQuery(this).hasClass('active')){
					jQuery('.appbase_thumb_container .appbase-thumbnail').removeClass('active');
					jQuery(this).addClass('active');
					$this.variables.VIEWFLAG = jQuery(this).hasClass('grid_thumb') ? true:false
					var input_val = jQuery(modal).find('.' + obj.abbr + 'input').eq(1).val();
					jQuery(modal).find('.' + obj.abbr + 'input').typeahead('val','').typeahead('val',input_val).focus();
				}
			});
			jQuery('.setting_thumb').click(function(){
				if(!jQuery('.appbase_side_container').hasClass('active')){
						jQuery('.appbase_side_container').addClass('active').show();
						jQuery('.appbase_brand_search').typeahead('val','').focus();
					}
				else
					jQuery('.appbase_side_container').removeClass('active').hide();
			});

			//Filter events
			jQuery('.date_list li').click(function(){
				var val = jQuery(this).data('val');
				alert(val);
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
				var grid_view = appbase_variables.hasOwnProperty('grid') ? appbase_variables.grid : false;
				appbase.initialize({
					title: 'Blazing fast search1 on your Documentation',
					input_placeholder: 'search here',
					logo: 'images/Appbase.png',
					selector: '.appbase_external_search',
					credentials:appbase_variables.credentials,
					app_name:appbase_variables.app_name,
					index_document_type:appbase_variables.index_document_type,
					grid_view:grid_view
				});
			});
	});
