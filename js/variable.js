function variables(credentials, app_name, index_document_type, method) {
  this.credentials = credentials;
  this.app_name = app_name;
  this.index_document_type = index_document_type;
  this.SIZE = 20;
  this.method = method;
  this.SEARCH_PAYLOAD = {
    "from": 0,
    "size": this.SIZE,
    "fields": ["link"],
    "query": {
      "multi_match": {
        "query": '',
        "fields": [
          "title^3", "body"
        ],
        "operator": "and"
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
  this.FUZZY_PAYLOAD = {
    "from": 0,
    "size": 10,
    "fields": ["link"],
    "query": {
      "multi_match": {
        "query": 'ap',
        "fields": [
          "title^3", "body"
        ],
        "operator": "and",
        "fuzziness": "AUTO"
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
}

variables.prototype = {
  constructor: variables,
  createURL: function() {
    var created_url = 'http://' + this.credentials + '@scalr.api.appbase.io/' + this.app_name + '/' + this.index_document_type + '/_search';
    return created_url;
  },
  createEngine: function($this, callback, on_fuzzy) {
    var search_payload = this.SEARCH_PAYLOAD;
    var parent_this = this;
    var $engine_this = this;
    var engine = new Bloodhound({
      name: 'history',
      limit: 100,
      datumTokenizer: function(datum) {
        return Bloodhound.tokenizers.whitespace(datum);
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {

        url: this.createURL(),
        rateLimitWait: 300,
        prepare: function(query, settings) {
          settings.type = "POST";
          settings.xhrFields = {
            withCredentials: true
          };
          settings.headers = {
            "Authorization": "Basic " + btoa(this.credentials)
          };
          settings.contentType = "application/json; charset=UTF-8";
          //console.log(search_payload);
          search_payload.query.multi_match.query = query;
          settings.data = JSON.stringify(search_payload);
          return settings;
        },
        transform: function(response) {
          if (response.hits.hits.length) {
            $this.appbase_total = response.hits.total;
            
            callback(response.hits.total);
            
            if(parent_this.method == 'client'){
              var showing_text = $engine_this.showing_text(response.hits.hits.length, response.hits.total, $('.appbase_input').eq(1).val(), response.took);
              $(".appbase_total_info").html(showing_text);
            }
            if(parent_this.method == 'appbase'){
              var showing_text = $engine_this.showing_text(response.hits.hits.length, response.hits.total, $('.typeahead').eq(1).val(), response.took);
              $("#search-title").html(showing_text);
            }

            return $.map(response.hits.hits, function(hit) {
              return hit;
            });
          } else {
            
            parent_this.fuzzy_call(on_fuzzy);

            return response.hits.hits;
            $(".appbase_total_info").text("No Results found");
          }
        }
      }
    });

    return engine;
  },
  fuzzy_call:function(callback){
    var request_data = JSON.stringify(this.FUZZY_PAYLOAD);            
    $.ajax({
        type: "POST",
        beforeSend: function(request) {
          request.setRequestHeader("Authorization", "Basic " + btoa(this.credentials));
        },
        'url':this.createURL(),
        dataType: 'json',
        contentType: "application/json",
        data: request_data,
        success: function(response) {
           callback(response, 'fuzzy');
        }
      });
  },
  scroll_xhr: function($this, method, callback) {
    $this.appbase_xhr_flag = false;
    var input_value = '';
    if(method == 'client')
      input_value = $('.appbase_input').eq(1).val();
    else if(method == 'appbase')
      input_value = $('.typeahead').eq(1).val();

    $this.search_payload.query.multi_match.query = input_value;
    $this.search_payload.from = $this.appbase_increment;
    var request_data = JSON.stringify($this.search_payload);

    $.ajax({
      type: "POST",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", "Basic " + btoa(this.credentials));
      },
      'url': this.createURL(),
      dataType: 'json',
      contentType: "application/json",
      data: request_data,
      success: function(full_data) {
        callback(full_data);
      }
    });
  },
  showing_text: function(init_no, total_no, value, time) {
    return 'Showing 1-' + init_no + ' of ' + total_no + " for \"" + value + "\"" + "- in " + time + "ms"
  }
}