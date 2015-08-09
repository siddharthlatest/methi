var appbase_app = function(){
	var $this = this;
	return {
		initialize:initialize
	};

	function initialize(options){
		
		//Initialize Variables Start
		$this.default_options = {
			title:'Blazing fast search on your Documentation',
			input_placeholder:'search here',
			logo:'images/Appbase.png',
			abbr:'appbase_',
			selector:'.appbase_external_search'
		};
		$this.variables = variables();
		$this.url = $this.variables.URL;
		$this.appbase_total = 0;
		$this.appbase_increment = 20;
		$this.size = $this.appbase_increment;
		$this.appbase_xhr_flag = true;
		$this.search_payload = $this.variables.SEARCH_PAYLOAD;
		    $.ajaxSetup({
			    crossDomain: true,
			    xhrFields: {
			        withCredentials: true
			    }
			});           
		    //Initialize Variables End
		    
		    //Bloodhound Start
		    engine = new Bloodhound(variables().ENGINE());
			//Bloodhound End

			//Fire CreateHtml
			var options = $.extend($this.default_options, options);
			createHtml(options);

			//CreateHtml Start
			function createHtml(obj){
				var abbr = obj.abbr;
				var title = $('<h1>').addClass(abbr+'title').html(obj.title);
				var	input_box = $('<input>').addClass(abbr+'input').attr({'type':'text', 'placeholder':obj.input_placeholder});
				var	app_logo = $('<img>').addClass(abbr+'logo').attr({'src':obj.logo});
				var	search_box = $('<div>').addClass(abbr+'search_box').append(input_box).append(app_logo);
				var	search_box_container = $('<div>').addClass(abbr+'search_box').append(search_box);
				var	modal_content = $('<div>').addClass(abbr+'modal_content').append(title).append(search_box_container);
				var overlay = $('<div>').addClass(abbr+'overlay');
				var	modal = $('<div>').addClass(abbr+'modal').append(modal_content).append(overlay);
				$('body').append(modal);

				html_events(obj, modal, overlay);	
			};

			function html_size(obj, modal){
				function appbase_resize(){
					var win_height = $(window).height();
					var modal_height = win_height - 150;
					var tt_height = modal_height - $('.'+obj.abbr+'title').height()+$('.'+obj.abbr+'input').height()
					$(modal).find('.'+obj.abbr+'modal_content').height(modal_height);
					$(modal).find('.tt-open').height(tt_height);
					
				}
				$(window).resize(appbase_resize());
				appbase_resize();
			}

			function html_events(obj, modal, overlay){
				$(modal).find('.'+obj.abbr+'input').typeahead({
				  minLength: 2,
				  highlight: true,
				  limit: 100,
				  change:function(){
				  	alert('changed');
				  }
				},
				{
				  name: 'my-dataset',
				  limit: 100,
				  source: engine.ttAdapter(),
				  templates: {
				      suggestion: function(data){
				      	console.log(data);
				        // return '<div><h4><a href="https://www.digitalocean.com/community/tutorials/'+ data.fields.link + '">' + data.fields.title + '</a></h4><p> ' + "Abhi ke liye yeh hi body se kaam chala  lo baad mein kuch aur daal denge beta - Yo - I am loving this typing" + '</p></div>';
				        return '<div><h4><a href="'+ data.fields.link +'">' + data.highlight.title + '</a></h4><p> ' + data.highlight.body.join('...') + '...</p></div>';
				      }
				  }
				});
				html_size(obj, modal);

				$(obj.selector).on('keyup',function(){
					var input_val = $(this).val();
					$(modal).find('.'+obj.abbr+'input').val(input_val);
					$(modal).show();
					$(overlay).show();
					$(modal).find('.'+obj.abbr+'input').focus();
				});
				$(overlay).on('click',function(){
					$(modal).hide();
					$(overlay).hide();
				});

				$('.tt-menu').on('scroll', function() {
			        if($(this).scrollTop() + $(this).innerHeight() >= this.scrollHeight) {
			        	if($this.appbase_total != 0 && $this.appbase_total > $this.appbase_increment && $this.appbase_xhr_flag){
			        		scroll_xhr();
			        	}
			        }
			    });

				
				function scroll_xhr(){
					$this.appbase_xhr_flag = false;
					$this.search_payload.query.multi_match.query = $('.'+obj.abbr+'input').eq(1).val();
					$this.search_payload.from = $this.appbase_increment;
					$.ajax({
					  type: "POST",
			            beforeSend: function (request)
			            {
			                request.setRequestHeader("Authorization", "Basic " + btoa("qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5"));
			            },
					  url: $this.url,
					  dataType:'json',
				      contentType:"application/json",
					  data:  JSON.stringify($this.search_payload),
					  success: function(full_data){
					  	alert('success');
					  	var hits = full_data.hits.hits;
						$this.appbase_increment += hits.length;
					  	
					  	for(var i=0; i< hits.length; i++)
					  	{
					  		var data = hits[i];
					  		var single_record = '<div><h4><a href="'+ data.fields.link +'">' + data.highlight.title + '</a></h4><p> ' + data.highlight.body.join('...') + '...</p></div>';
				      		var tt_record = $('<div>').addClass('tt-suggestion tt-selectable').html(single_record);
				      		$('.tt-menu .tt-dataset.tt-dataset-my-dataset').append(tt_record);
				      	}
				      	$this.appbase_xhr_flag = true;
					  }
					});
				}
					
			}
			//CreateHtml End

		               

	}
}

var Loader = function () { }
Loader.prototype = {
    require: function (scripts, callback) {
        this.loadCount      = 0;
        this.totalRequired  = scripts.length;
        this.callback       = callback;

        for (var i = 0; i < scripts.length; i++) {
        	var split_name = scripts[i].split('.');
        	if(split_name[split_name.length-1] == 'js')
            	this.writeScript(scripts[i]);
            if(split_name[split_name.length-1] == 'css')
            	this.writeStylesheet(scripts[i]);
        }
    },
    loaded: function (evt) {
        this.loadCount++;

        if (this.loadCount == this.totalRequired && typeof this.callback == 'function') this.callback.call();
    },
    writeScript: function (src) {
        var self = this;
        var s = document.createElement('script');
        s.type = "text/javascript";
        s.async = true;
        s.src = src;
        s.addEventListener('load', function (e) { self.loaded(e); }, false);
        var head = document.getElementsByTagName('head')[0];
        head.appendChild(s);
    },
    writeStylesheet: function (src) {
        var self = this;
        var s = document.createElement('link');
        s.type = "text/css";
        s.rel = "stylesheet";
        s.href = src;
        s.addEventListener('load', function (e) { self.loaded(e); }, false);
        var head = document.getElementsByTagName('head')[0];
        head.appendChild(s);
    }
}

var jquery_js = new Loader();
jquery_js.require([
    "css/client.css",
    "https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"], 
    function() {
		var typeahead_js = new Loader();
		typeahead_js.require([
		    "http://cdnjs.cloudflare.com/ajax/libs/typeahead.js/0.11.1/typeahead.bundle.min.js",
		    "js/variable.js"], 
		    function() {
		    	 var appbase = new appbase_app();
			      appbase.initialize({
			        title:'Blazing fast search1 on your Documentation',
			        input_placeholder:'search here',
			        logo:'images/Appbase.png',
			        selector:'.appbase_external_search'
			      });
		    });    	
    });
