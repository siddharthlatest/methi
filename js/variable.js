function variables(credentials, app_name, index_document_type, method) {
  this.credentials = credentials;
  this.app_name = app_name;
  this.index_document_type = index_document_type;
  this.SIZE = 20;
  this.method = method;
  this.NO_RESULT_TEXT = "No Results found";
  this.INITIAL_TEXT = "Start typing..";
  this.FUZZY_FLAG = false;
  this.image = 'http://www.passionforneedygh.com/wp-content/themes/nobeliumful/styles/images/default-archive.png';
  this.SEARCH_PAYLOAD = {
    "from": 0,
    "size": this.SIZE,
    "fields": ["link"],
    "query": {
      "multi_match": {
        "query": '',
        "fields": [
          "title_simple^2", "title_ngrams", "body"
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
    "size": this.SIZE,
    "fields": ["link"],
    "query": {
      "multi_match": {
        "query": 'ap',
        "fields": [
          "title_simple^2", "body"
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
    var created_url = 'http://scalr.api.appbase.io/' + this.app_name + '/' + this.index_document_type + '/_search';
    return created_url;
  },
  createEngine: function($this, callback, on_fuzzy) {
    var search_payload = this.SEARCH_PAYLOAD;
    var parent_this = this;
    var engine = new Bloodhound({
      name: 'history',
      limit: 100,
      async: true,
      templates: {
        pending: true
      },
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
            "Authorization": "Basic " + btoa(parent_this.credentials)
          };
          settings.contentType = "application/json; charset=UTF-8";
          //console.log(search_payload);
          search_payload.from = 0;
          search_payload.query.multi_match.query = query;
          settings.data = JSON.stringify(search_payload);
          return settings;
        },
        transform: function(response) {
          $this.appbase_increment = response.hits.hits.length;
          if (response.hits.hits.length) {
            parent_this.FUZZY_FLAG = false;
            $this.appbase_total = response.hits.total;

            callback(response.hits.total);

            if (parent_this.method == 'client') {
              var showing_text = parent_this.showing_text(response.hits.hits.length, response.hits.total, jQuery('.appbase_input').eq(1).val(), response.took);
              jQuery(".appbase_total_info").html(showing_text);
            }
            if (parent_this.method == 'appbase') {
              var showing_text = parent_this.showing_text(response.hits.hits.length, response.hits.total, jQuery('.typeahead').eq(1).val(), response.took);
              jQuery("#search-title").html(showing_text);
            }

            return jQuery.map(response.hits.hits, function(hit) {
              return hit;
            });
          } else {
            parent_this.FUZZY_FLAG = true;
            parent_this.fuzzy_call($this, on_fuzzy);

            return response.hits.hits;
            jQuery(".appbase_total_info").text(parent_this.NO_RESULT_TEXT);
          }
        }
      }
    });

    return engine;
  },
  fuzzy_call: function($this, callback) {
    if (this.method == 'client')
      input_value = jQuery('.appbase_input').eq(1).val();
    else if (this.method == 'appbase')
      input_value = jQuery('.typeahead').eq(1).val();
    this.FUZZY_PAYLOAD.from = 0;
    this.FUZZY_PAYLOAD.query.multi_match.query = input_value;
    var request_data = JSON.stringify(this.FUZZY_PAYLOAD);
    var credentials = this.credentials;
    jQuery.ajax({
      type: "POST",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", "Basic " + btoa(credentials));
      },
      'url': this.createURL(),
      dataType: 'json',
      contentType: "application/json",
      data: request_data,
      success: function(response) {
        $this.appbase_total = response.hits.total;
        callback(response, 'fuzzy');
      }
    });
  },
  scroll_xhr: function($this, method, callback) {
    var fuzzy_flag = this.FUZZY_FLAG;
    var scroll_payload = {};
    var fuzzy_payload = this.FUZZY_PAYLOAD;
    var search_payload = this.SEARCH_PAYLOAD;
    $this.appbase_xhr_flag = false;
    var credentials = this.credentials;
    var parent_this = this;
    var input_value = '';
    if (method == 'client')
      input_value = jQuery('.appbase_input').eq(1).val();
    else if (method == 'appbase')
      input_value = jQuery('.typeahead').eq(1).val();

    console.log(parent_this);
    if (fuzzy_flag) {
      scroll_payload = fuzzy_payload;
    } else {
      scroll_payload = search_payload;
    }

    scroll_payload.from = $this.appbase_increment;
    scroll_payload.query.multi_match.query = input_value;
    var request_data = JSON.stringify(scroll_payload);

    jQuery.ajax({
      type: "POST",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", "Basic " + btoa(credentials));
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
  createRecord: function(data) {
    var small_link = jQuery('<span>').addClass('small_link').html(data.highlight.title);
    var small_description = jQuery('<p>').addClass('small_description').html(data.highlight.body.join('...') + '...');
    if (data.fields.link.toString().match(/index.html$/))
      data.fields.link = data.fields.link.toString().slice(0, -10)
    var single_record = jQuery('<a>').attr({
      'class': 'record_link',
      'href': data.fields.link,
      'target': '_blank'
    }).append(small_link).append(small_description);
    return single_record;
  },
  showing_text: function(init_no, total_no, value, time) {
    var count_result = total_no + " results for \"" + value + "\"" + " in " + time + "ms";
    if (this.method == 'client') {
      if (jQuery('.appbase_input').eq(1).val().length)
        return count_result;
      else
        return this.INITIAL_TEXT;
    } else
      return count_result;
  }
}