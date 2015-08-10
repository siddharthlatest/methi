var appbase_total = 0;
var appbase_increment = 20;
var appbase_xhr_flag = true;
var url = 'http://qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5@scalr.api.appbase.io/1/article/_search';
var search_payload = {
                 "size": "20",
                 "fields": ["link"],
                  "query": {
                    "multi_match": {
                      "query": {},
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
var engine = new Bloodhound({
       name: 'history',
       limit: 100,
       datumTokenizer: function (datum) { return Bloodhound.tokenizers.whitespace(datum); },
       queryTokenizer: Bloodhound.tokenizers.whitespace,
       remote: {

           url: url,
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
               search_payload = search_payload;
              search_payload.query.multi_match.query = query;
                // search_payload = {
                //   "size": "120",
                //   "fields": ["title","link"],
                //    "query": {
                //      "match": {
                //         "_all": {
                //            "query": query
                //         }
                //      }
                //    },
                //    "highlight": {
                //      "fields": {
                //        "title": {
                //          "fragment_size": 100,
                //          "number_of_fragments": 3
                //        }
                //      }
                //    }
                // };
               settings.data = JSON.stringify(search_payload);
               return settings;
           },
           transform: function(response) {
             console.log(response);
               if(response.hits.hits.length > 0) {
                 console.log(response.hits.total);
                appbase_total = response.hits.total; 
                 $("#search-title").html(response.hits.total+ " Results found" + " <sub>(in " + parseInt(response.took) + "ms)</sub>");
                 return $.map(response.hits.hits, function (hit) {
                     return hit;
                 });
               }
               else{
                 $("#search-title").text("No Results found");
               }
           }
       }
   });

$('.typeahead').typeahead({
  minLength: 2,
  highlight: true
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

$(window).scroll(function() {
   if($(window).scrollTop() + $(window).height() == $(document).height()) {
       if (appbase_total != 0 && appbase_total > appbase_increment && appbase_xhr_flag) {
      scroll_xhr();
    }
   }
});
function scroll_xhr(){
          appbase_xhr_flag = false;
          search_payload.query.multi_match.query = $('.typeahead').eq(1).val();
          search_payload.from = appbase_increment;
          $.ajax({
            type: "POST",
                  beforeSend: function (request)
                  {
                      request.setRequestHeader("Authorization", "Basic " + btoa("qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5"));
                  },
            url: url,
            dataType:'json',
              contentType:"application/json",
            data:  JSON.stringify(search_payload),
            success: function(full_data){
              var hits = full_data.hits.hits;
            appbase_increment += hits.length;
              $(".appbase_total_info").html('Showing 1-'+appbase_increment+' of '+appbase_total + " for \""+$('.appbase_input').eq(1).val()+"\"");
              
              for(var i=0; i< hits.length; i++)
              {
                var data = hits[i];
                // var small_link = $('<span>').addClass('small_link').text(data.highlight.title);
                // var small_description = $('<p>').addClass('small_description').text(data.highlight.body.join('...')+'...');
                // var single_record = $('<a>').attr({'class':'record_link'}).append(small_link).append(small_description);

                // //var single_record = '<div><a cla href="'+ data.fields.link +'">' + data.highlight.title + '</a><p> ' + data.highlight.body.join('...') + '...</p></div>';
                //   var tt_record = $('<div>').addClass('tt-suggestion tt-selectable').html(single_record);
                  
                  var single_record_in = '<div><h4><a href="'+ data.fields.link +'">' + data.highlight.title + '</a></h4><p> ' + data.highlight.body.join('...') + '...</p></div>'
                  $('.tt-menu .tt-dataset.tt-dataset-my-dataset').append(single_record_in);
                }
                appbase_xhr_flag = true;
            }
          });
        }
          
      

$('.typeahead').on('keyup',function(){
  search_grow('show');
});


$('.overlay').click(function(){
  search_grow('hide');
});

function search_grow(method){
  if(method == 'show'){
    $('.overlay').show('fast');
    $('.search-box-container').addClass('search-box-container-grow');
    $('#search-title').fadeIn('slow');
  }
  else if(method == 'hide'){
    $('#search-title').fadeOut(1);
    $('.search-box-container').removeClass('search-box-container-grow');
    $('.overlay').fadeOut('slow');
  }
}
