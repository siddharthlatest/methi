function variables(credentials, app_name, index_document_type) {
  this.credentials = credentials;
  this.app_name = app_name;
  this.index_document_type = index_document_type;
  this.SIZE = 20;
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
  // this.FUZZY_PAYLOAD = {
  //   "from": 0,
  //   "size": 10,
  //   "fields": ["link"],
  //   "query": {
  //     "multi_match": {
  //       "query": search_query,
  //       "fields": [
  //         "title^3", "body"
  //       ],
  //       "operator": "and",
  //       "fuzziness": "AUTO"
  //     }
  //   },
  //   "highlight": {
  //     "fields": {
  //       "body": {
  //         "fragment_size": 100,
  //         "number_of_fragments": 2,
  //         "no_match_size": 180
  //       },
  //       "title": {
  //         "fragment_size": 500,
  //         "no_match_size": 500
  //       }
  //     }
  //   }
  // };
}

variables.prototype = {
  constructor: variables,
  createURL: function() {
    var created_url = 'http://' + this.credentials + '@scalr.api.appbase.io/' + this.app_name + '/' + this.index_document_type + '/_search';
    return created_url;
  },
  createEngine: function(callback) {
    var search_payload = this.SEARCH_PAYLOAD;
    var $this = this;
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
            "Authorization": "Basic " + btoa("qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5")
          };
          settings.contentType = "application/json; charset=UTF-8";
          console.log(search_payload);
          search_payload.query.multi_match.query = query;
          settings.data = JSON.stringify(search_payload);
          return settings;
        },
        transform: function(response) {
          if (response.hits.hits.length) {
            //$this.appbase_total = response.hits.total;
            if (typeof callback != 'undefined')
            callback(response.hits.total);
            var showing_text = $this.showing_text(response.hits.hits.length, response.hits.total, $('.appbase_input').eq(1).val(), response.took);
            $(".appbase_total_info").html(showing_text);
            return $.map(response.hits.hits, function(hit) {
              return hit;
            });
          } else {
            return response.hits.hits;
            $(".appbase_total_info").text("No Results found");
          }
        }
      }
    });

    return engine;
  },
  scroll_xhr: function($this, method, callback) {
    $this.appbase_xhr_flag = false;
    var input_value = method == 'client' ? $('.appbase_input').eq(1).val() : $('.typeahead').eq(1).val();
    $this.search_payload.query.multi_match.query = input_value;
    $this.search_payload.from = $this.appbase_increment;
    $.ajax({
      type: "POST",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", "Basic " + btoa("qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5"));
      },
      'url': this.createURL(),
      dataType: 'json',
      contentType: "application/json",
      data: JSON.stringify($this.search_payload),
      success: function(full_data) {
        callback(full_data);
      }
    });
  },
  showing_text: function(init_no, total_no, value, time) {
    return 'Showing 1-' + init_no + ' of ' + total_no + " for \"" + value + "\"" + "- in " + time + "ms"
  }
}