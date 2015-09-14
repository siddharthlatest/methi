function variables(credentials, app_name, index_document_type, method, grid_view, filter_view) {
  this.credentials = credentials;
  this.app_name = app_name;
  this.index_document_type = index_document_type;
  this.SIZE = 20;
  this.method = method;
  this.NO_RESULT_TEXT = "No Results found";
  this.INITIAL_TEXT = "Start typing..";
  this.FUZZY_FLAG = false;
  this.GridView = grid_view;
  this.FILTER_VIEW = filter_view;
  this.date = {
    label: 'Date Range',
    content: [{
      text: 'Any time',
      val: '0'
    }, {
      text: 'Past 24 Hours',
      val: 'now-1d'
    }, {
      text: 'Past week',
      val: 'now-1w'
    }, {
      text: 'Past month',
      val: 'now-1M'
    }, {
      text: 'Past year',
      val: 'now-1y'
    }]
  };
  this.brand = {
      label: 'Tags',
      placeholder: 'Search..',
      fetch: []
    }
    //this.IMAGE = 'http://d152j5tfobgaot.cloudfront.net/wp-content/uploads/2015/08/yourstory-the-road-to-reinvention-josh-linkner-280x140.jpg';
    //this.IMAGE = 'http://www2.pictures.zimbio.com/gi/Alia+Bhatt+Alia+Bhatt+Portrait+Session+3ukI6nYTRwLl.jpg';
  this.IMAGE = 'http://d152j5tfobgaot.cloudfront.net/wp-content/uploads/2015/01/YourStory_Transparent-1.png';
  this.LIST_THUMB = 'images/list_thumb.png';
  this.GRID_THUMB = 'images/grid_thumb.png';
  this.SEARCH_THUMB = 'images/search.png';
  this.VIEWFLAG = this.GridView;
  this.SEARCH_PAYLOAD = {
    "from": 0,
    "size": this.SIZE,
    "fields": ["link", "image_url"],
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
    "fields": ["link", "image_url"],
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
  if (this.FILTER_VIEW) {
    this.SEARCH_PAYLOAD['filter'] = {
      "range": {
        "created_at": {
          "gte": "0"
        }
      }
    };
    this.FUZZY_PAYLOAD['filter'] = {
      "range": {
        "created_at": {
          "gte": "0"
        }
      }
    }
  }
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
          query = query.toLowerCase();
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
    input_value = input_value.toLowerCase();
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

    input_value = input_value.toLowerCase();
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

    // Grid View 
    if (this.VIEWFLAG) {
      if (data.fields.hasOwnProperty('image_url') && data.fields.image_url[0] != 'None')
        var image_url = data.fields.image_url[0];
      else
        var image_url = this.IMAGE;
      var small_info_container = jQuery('<div>').addClass('small_info_container').append(small_link).append(small_description);
      var record_img = jQuery('<img>').addClass('record_img').attr({
        'src': image_url,
        'alt': data.highlight.title,
        'onerror': 'this.onerror = null; this.src="' + this.IMAGE + '"'
      });
      var record_img_container = jQuery('<span>').addClass('record_img_container').append(record_img);
      var record_link_container = jQuery('<div>').addClass('record_link_container').append(record_img_container).append(small_info_container);
      if (data.fields.link.toString().match(/index.html$/))
        data.fields.link = data.fields.link.toString().slice(0, -10)
      var single_record = jQuery('<a>').attr({
        'class': 'record_link modal_grid_view',
        'href': "http://" + data.fields.link,
        'target': '_blank'
      }).append(record_link_container);
    }
    // List View
    else {
      if (data.fields.link.toString().match(/index.html$/))
        data.fields.link = data.fields.link.toString().slice(0, -10)
      var single_record = jQuery('<a>').attr({
        'class': 'record_link',
        'href': data.fields.link,
        'target': '_blank'
      }).append(small_link).append(small_description);
    }

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
  },
  set_date: function(val) {
    this.SEARCH_PAYLOAD.filter.range.created_at.gte = val;
    this.FUZZY_PAYLOAD.filter.range.created_at.gte = val;
  },
  createBrand: function(data) {
    var $parent_this = this;
    var checkbox = jQuery('<input>').attr({
      type: 'checkbox',
      name: 'brand',
      value: data
    });
    if (jQuery.inArray(data, $parent_this.brand.fetch) != -1)
      checkbox.prop('checked', true);
    var checkbox_text = jQuery('<span>').text(data);
    var single_tag = jQuery('<label>').append(checkbox).append(checkbox_text);

    checkbox.change(function() {
      if (jQuery(this).is(':checked'))
        $parent_this.brand.fetch.push(jQuery(this).val());
      else {
        $parent_this.brand.fetch.remove(jQuery(this).val());
      }
      console.log($parent_this.brand.fetch);
    });
    return single_tag;
  }
}
Array.prototype.remove = function() {
  var what, a = arguments,
    L = a.length,
    ax;
  while (L && this.length) {
    what = a[--L];
    while ((ax = this.indexOf(what)) !== -1) {
      this.splice(ax, 1);
    }
  }
  return this;
};
