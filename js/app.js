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
		$this.url = 'http://qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5@scalr.api.appbase.io/1/article/_search';
		$this.appbase_total = 0;
		$this.appbase_increment = 20;
		$this.size = $this.appbase_increment;
		$this.appbase_xhr_flag = true;
		$this.search_payload = {
						"from":0,	
		                 "size": $this.size,
		                 "fields": ["link"],
		                  "query": {
		                    "multi_match": {
		                      "query": 'ap',
		                      "fields": [
		                        "title^3", "body"
		                      ]
		                    }
		                  },
		                  "highlight": {
		                    "fields": {
		                      "body": {
		                        "fragment_size": 100,
		                        "number_of_fragments": 2,
		                        "no_match_size": 180
		                      },
		                      "title": {
		                        "fragment_size": 500,
		                        "no_match_size": 500
		                      }
		                    }
		                  }
		               };
		    $.ajaxSetup({
			    crossDomain: true,
			    xhrFields: {
			        withCredentials: true
			    }
			});           
		    //Initialize Variables End
		    
		    //Bloodhound Start
		    var engine = new Bloodhound({
		       name: 'history',
		       limit: 100,
		       datumTokenizer: function (datum) { return Bloodhound.tokenizers.whitespace(datum); },
		       queryTokenizer: Bloodhound.tokenizers.whitespace,
		       remote: {

		           url: $this.url,
		          //  url: 'http://localhost:9200/digitalocean/article/_search',
		           // he time interval in milliseconds that will be used by rateLimitBy. Defaults to 300
		           rateLimitWait: 300,
		            // Function that provides a hook to allow you to prepare the settings object passed to transport when a request is about to be made.
		            // The function signature should be prepare(query, settings), where query is the query #search was called with
		            // and settings is the default settings object created internally by the Bloodhound instance. The prepare function should return a settings object.
		           prepare: function (query, settings) {

		               settings.type = "POST";
		               settings.xhrFields= {
		                 withCredentials: true
		               };
		               settings.headers = {
		                 "Authorization": "Basic " + btoa("qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5")
		               };
		               settings.contentType = "application/json; charset=UTF-8";
		            	$this.search_payload.query.multi_match.query = query;
		               settings.data = JSON.stringify($this.search_payload);
		               return settings;
		           },
		           transform: function(response) {
		             console.log(response);
		               if(response.hits.hits.length > 0) {
		                 console.log(response.hits.total);
		                 $this.appbase_total = response.hits.total;
		                 $('.appbase_title').html(response.hits.total+ " Results found" + " <sub>(in " + parseInt(response.took) + "ms)</sub>");
		                 return $.map(response.hits.hits, function (hit) {
		                     return hit;
		                 });
		               }
		               else{
		                 $(".appbase_title").text("No Results found");
		               }
		           }
		       }
		   });
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

				
				var css = '.appbase_modal{display:none;position:fixed;margin:0 auto;z-index:998;width:100%;height:100%;top:0;left:0;background:0 0}.appbase_input,.appbase_modal_content{display:block;width:100%;background-color:#fff;box-sizing:border-box}.appbase_modal_content{position:relative;max-width:960px;margin:50px auto 0;padding:20px;border-radius:5px;z-index:1000}.appbase_search_box{position:relative}.appbase_input{color:#555;background-image:none;border:1px solid #ccc;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,.075);box-shadow:inset 0 1px 1px rgba(0,0,0,.075);-webkit-transition:border-color ease-in-out .15s,-webkit-box-shadow ease-in-out .15s;-o-transition:border-color ease-in-out .15s,box-shadow ease-in-out .15s;transition:border-color ease-in-out .15s,box-shadow ease-in-out .15s;height:46px;padding:10px 16px;font-size:18px;line-height:1.3333333;border-radius:6px}.appbase_logo{position:absolute;width:15%;margin:auto;top:5px;right:10px}.appbase_overlay{display:none;position:fixed;width:100%;height:100%;top:0;left:0;z-index:999;background:rgba(0,0,0,.5)}.twitter-typeahead{width:100%}.twitter-typeahead .tt-menu{position:relative!important;overflow:auto;height:200px}';

			    head = document.head || document.getElementsByTagName('head')[0],
			    style = document.createElement('style');
				style.type = 'text/css';
				if (style.styleSheet){
				  style.styleSheet.cssText = css;
				} else {
				  style.appendChild(document.createTextNode(css));
				}
				head.appendChild(style);
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



//Working css

// .appbase_modal{
//         display: none;
//         position: fixed;
//         margin: 0 auto;
//         z-index: 998;
//         width: 100%;
//         height: 100%;
//         top: 0;
//         left: 0;
//         background: transparent;
//       }
//       .appbase_modal_content{
//         position: relative;
//         margin: 0 auto;
//         display: block;
//         background-color: #fff;
//         width: 100%;
//         max-width: 960px;
//         margin: 50px auto 0 auto;
//         padding: 20px;
//         border-radius: 5px;
//         z-index: 1000;
//          box-sizing: border-box;
//       }
//       .appbase_search_box{
//         position: relative;
//       }
//       .appbase_input{
//         display: block;
//         width: 100%;
//         color: #555;
//         background-color: #fff;
//         background-image: none;
//         border: 1px solid #ccc;
//         border-radius: 4px;
//         -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075);
//         box-shadow: inset 0 1px 1px rgba(0,0,0,.075);
//         -webkit-transition: border-color ease-in-out .15s,-webkit-box-shadow ease-in-out .15s;
//         -o-transition: border-color ease-in-out .15s,box-shadow ease-in-out .15s;
//         transition: border-color ease-in-out .15s,box-shadow ease-in-out .15s;
//         height: 46px;
//         padding: 10px 16px;
//         font-size: 18px;
//         line-height: 1.3333333;
//         border-radius: 6px;
//         box-sizing: border-box;
//       }
//       .appbase_logo{
//           position: absolute;
//           width: 15%;
//           margin: auto;
//           top: 5px;
//           right: 10px;
//       }
//       .appbase_overlay{
//         display: none;
//         position: fixed;
//         width: 100%;
//         height: 100%;
//         top: 0;
//         left: 0;
//         z-index: 999;
//         background: rgba(0,0,0,0.50);
//       }
//       .twitter-typeahead{
//         width: 100%
//       }
//       .twitter-typeahead .tt-menu{
//         position: relative !important;
//         overflow: auto;
//         height: 200px
//       }