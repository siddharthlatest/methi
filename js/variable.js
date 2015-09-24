function variables(credentials, app_name, index_document_type, method, grid_view, filter_view, mobile_view) {
  this.credentials = credentials;
  this.app_name = app_name;
  this.index_document_type = index_document_type;
  this.SIZE = 10;
  this.TAG_LENGTH = 10;
  this.TAG_LOAD_SIZE = 1000;
  this.method = method;
  this.NO_RESULT_TEXT = "No Results found";
  this.NO_RESULT_TEXT_TAG = "No results found. Try removing the tags for all results";
  this.INITIAL_TEXT = "Start typing..";
  this.NO_TAG_TEXT = "No tags found.";
  this.TAG_LOAD_TEXT = 'Load more';
  this.FUZZY_FLAG = false;
  this.GridView = grid_view;
  this.FILTER_VIEW = filter_view;
  this.MOBILE_VIEW = mobile_view;
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
  this.IMAGE = 'http://cdn.appbase.io/methi/images/no_image.png';
  this.LIST_THUMB = 'http://cdn.appbase.io/methi/images/list_thumb.png';
  this.GRID_THUMB = 'http://cdn.appbase.io/methi/images/grid_thumb.png';
  this.SEARCH_THUMB = 'http://cdn.appbase.io/methi/images/search.png';
  this.SETTING_THUMB = 'images/settings.png';
  this.METHI_PATH = 'index.html';
  this.VIEWFLAG = this.GridView;
  this.TAGS = [];
  this.SELECTED_TAGS = [];
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
        "title": {
          "fragment_size": 500,
          "no_match_size": 500
        }
      }
    }
  };
  this.BODY_OBJECT = {
    "fragment_size": 100,
    "number_of_fragments": 2,
    "no_match_size": 180
  };
  this.AGG_OBJECT = {
    "tags": {
      "terms": {
        "field": "tags",
        "order": {
          "_count": "desc"
        },
        "size": this.TAG_LENGTH
      }
    }
  };
  this.FILTER_OBJECT = {
    "range": {
      "created_at": {
        "gte": "0"
      }
    }
  };
};

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
          if (parent_this.FILTER_VIEW) {
            parent_this.apply_agg('append');
          }
          parent_this.apply_body();
          search_payload.query.multi_match.query = query;
          settings.data = JSON.stringify(search_payload);
          return settings;
        },
        transform: function(response) {
          $this.appbase_increment = response.hits.hits.length;
          if (response.hits.hits.length) {
            parent_this.FUZZY_FLAG = false;
            $this.appbase_total = response.hits.total;

            if (response.hasOwnProperty('aggregations'))
              parent_this.TAGS = response.aggregations.tags.buckets;
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
            parent_this.no_result();
            return response.hits.hits;
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
    var parent_this = this;
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
        if (response.hasOwnProperty('aggregations'))
          parent_this.TAGS = response.aggregations.tags.buckets;
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
    if (data.highlight.hasOwnProperty('body')) {
      var small_description = jQuery('<p>').addClass('small_description').html(data.highlight.body.join('...') + '...');
    }
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
      var single_record = jQuery('<a>').attr({
        'class': 'record_link modal_grid_view',
        'href': data.fields.link,
        'target': '_blank'
      }).append(record_link_container);
    }
    // List View
    else {
      var single_record = jQuery('<a>').attr({
        'class': 'record_link',
        'href': data.fields.link,
        'target': '_blank'
      }).append(small_link).append(small_description);
    }

    return single_record;
  },
  apply_filter: function(method) {
    if (method == 'append') {
      this.SEARCH_PAYLOAD['filter'] = this.FILTER_OBJECT;
      this.FUZZY_PAYLOAD['filter'] = this.FILTER_OBJECT;
    } else if (method == 'delete') {
      delete this.SEARCH_PAYLOAD['filter'];
      delete this.FUZZY_PAYLOAD['filter'];
    }
  },
  apply_agg: function(method) {
    if (method == 'append') {
      this.SEARCH_PAYLOAD['aggs'] = this.AGG_OBJECT;
      this.FUZZY_PAYLOAD['aggs'] = this.AGG_OBJECT;
    } else if (method == 'delete') {
      if(this.SEARCH_PAYLOAD.hasOwnProperty('aggs')){
        this.SEARCH_PAYLOAD.aggs.tags.terms.size = this.TAG_LENGTH;
        this.FUZZY_PAYLOAD.aggs.tags.terms.size = this.TAG_LENGTH;
      }
      this.AGG_OBJECT.tags.terms.size = this.TAG_LENGTH;
      delete this.SEARCH_PAYLOAD['aggs'];
      delete this.FUZZY_PAYLOAD['aggs'];
    }
  },
  apply_body: function() {
    if (this.VIEWFLAG && this.MOBILE_VIEW) {
      delete this.SEARCH_PAYLOAD.highlight.fields['body'];
      delete this.FUZZY_PAYLOAD.highlight.fields['body'];
    } else {
      this.SEARCH_PAYLOAD.highlight.fields['body'] = this.BODY_OBJECT;
      this.FUZZY_PAYLOAD.highlight.fields['body'] = this.BODY_OBJECT;
    }
  },
  showing_text: function(init_no, total_no, value, time) {
    var count_result = total_no + " results for \"" + value + "\"" + " in " + time + "ms";
    if (this.method == 'client') {
      if (jQuery('.appbase_input').eq(1).val().length)
        return count_result;
      else {
        jQuery('.appbase_side_container_inside').addClass('hide');
        return this.INITIAL_TEXT;
      }
    } else
      return count_result;
  },
  no_result: function() {
    if (this.SELECTED_TAGS.length) {
      var final_text = this.NO_RESULT_TEXT_TAG;
    } else {
      var final_text = this.NO_RESULT_TEXT;
    }
    jQuery(".appbase_total_info").text(final_text);
  },
  set_date: function(val) {
    if (val == '0')
      this.apply_filter('delete');
    else {
      this.apply_filter('append');
      this.SEARCH_PAYLOAD.filter.range.created_at.gte = val;
      this.FUZZY_PAYLOAD.filter.range.created_at.gte = val;
    }
  },
  CREATE_TAG: function(type, data) {
    $this = this;
    var list = $this.SELECTED_TAGS;
    var container = $('.' + type + '_container');
    var tag_value = data.key;
    if (tag_value == $this.TAG_LOAD_TEXT) {
      single_tag = $this.LOAD_BTN();
    } else {
      var doc_count = data.doc_count;
      var checkbox = $('<input>').attr({
        type: 'checkbox',
        name: 'brand',
        class: 'tag_checkbox',
        container: type,
        value: tag_value
      });
      if ($.inArray(tag_value, list) != -1)
        checkbox.prop('checked', true);
      var checkbox_text = $('<span>').text(tag_value);
      var tag_count = $('<span>').addClass('tag_count').text('(' + doc_count + ')');
      var tag_inside_text = $('<span>').addClass('tag_inside_text').text(tag_value);
      var tag_contain = $('<span>').addClass('tag_contain').append(tag_inside_text).append(tag_count);
      var single_tag = $('<label>').append(checkbox).append(tag_contain);

      checkbox.change(function() {
        var checkbox_val = $(this).val();
        var type = $(this).attr('container');
        var check2 = checkbox_val;

        if ($(this).is(':checked')) {
          list.push(check2);
          var tag_text = $('<span>').addClass('tag_text').text(checkbox_val);
          var tag_close = $('<span>').addClass('tag_close').text('x').attr('val', checkbox_val);
          var single_tag = $("<span>").addClass('single_tag').attr('val', checkbox_val).append(tag_text).append(tag_close);
          $(tag_close).click(function() {
            var val = $(this).attr('val');
            $(single_tag).remove();
            list.remove(val);
            $this.SEARCH_WITH_FILTER();
            container.find('.tag_checkbox[value="' + val + '"]').prop('checked', false);
          });
          container.find('.tag_name').append(single_tag);
          $this.SEARCH_WITH_FILTER();
        } else {
          container.find('.single_tag[val="' + checkbox_val + '"]').remove();
          list.remove(check2);
          $this.SEARCH_WITH_FILTER();
        }
        //console.log(list);
      });
    }
    return single_tag;
  },
  LOAD_BTN: function() {
    var $this = this;
    var load_link = $('<a>').addClass('appbase-tag-load').text(this.TAG_LOAD_TEXT);
    load_link.click(function() {
      $this.apply_agg('append');
      $this.SEARCH_PAYLOAD.aggs.tags.terms.size = $this.TAG_LOAD_SIZE;
      $this.FUZZY_PAYLOAD.aggs.tags.terms.size = $this.TAG_LOAD_SIZE;
      var input_val = jQuery('.appbase_input').eq(1).val();
      $this.LOAD_ALL();
    });
    return load_link;
  },
  LOAD_ALL: function() {
    var $this = this;
    var fuzzy_flag = this.FUZZY_FLAG;
    var fuzzy_payload = this.FUZZY_PAYLOAD;
    var search_payload = this.SEARCH_PAYLOAD;
    var credentials = this.credentials;
    var input_value = jQuery('.appbase_input').eq(1).val();
    input_value = input_value.toLowerCase();
    if (!fuzzy_flag) {
      var Load_payload = jQuery.extend({}, search_payload);
    } else {
      var Load_payload = jQuery.extend({}, fuzzy_payload);
    }

    Load_payload.query.multi_match.query = input_value;
    Load_payload.size = 0;
    var request_data = JSON.stringify(Load_payload);

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
        $this.TAG_BIND(full_data.aggregations.tags.buckets);
      }
    });
  },
  TAG_BIND: function(tags) {
    var tags_length = tags.length;
    var tags_ar = tags;
    var $this = this;
    $this.TAGS = tags;
    if (tags_ar.length) {
      if (tags_ar.length == $this.TAG_LENGTH) {
        tags_ar.push({
          'key': $this.TAG_LOAD_TEXT
        });
      }
      jQuery('.appbase_brand_search').html(' ');
      var search_thumb = jQuery('<img>').attr({
        src: $this.SEARCH_THUMB,
        class: 'search_thumb'
      });

      var single_search = jQuery('<input>').attr({
        'type': 'text',
        'class': 'appbase_brand_search',
        'placeholder': $this.brand.placeholder
      });
      jQuery('.appbase_brand_list_container').html('');
      jQuery('.appbase_brand_list_container').append(single_search).append(search_thumb);

      jQuery('.appbase_brand_search').typeahead({
        hint: true,
        highlight: true,
        minLength: 0
      }, {
        name: 'tags',
        limit: 100,
        source: substringMatcher(tags_ar),
        templates: {
          pending: true,
          suggestion: function(data) {
            if (data) {
              //var single_record = $this.variables.createBrand(data);
              var single_record = $this.CREATE_TAG('tag', data);
              return single_record;
            } else
              return;
          }
        }
      });

      jQuery('.appbase_brand_search').typeahead('val', '').focus();
      jQuery('.appbase_input').focus();
      $(window).trigger('resize');
    } else {
      var no_tag = jQuery('<span>').addClass('tag_default').text($this.NO_TAG_TEXT);
      jQuery('.appbase_brand_list_container').html('');
      jQuery('.appbase_brand_list_container').append(no_tag);
    }
  },
  SEARCH_WITH_FILTER: function() {
    var list = this.SELECTED_TAGS;
    if (list.length) {
      this.SEARCH_PAYLOAD['post_filter'] = {
        "terms": {
          "tags": list
        }
      };
      this.FUZZY_PAYLOAD['post_filter'] = {
        "terms": {
          "tags": list
        }
      };
    } else {
      delete this.SEARCH_PAYLOAD['post_filter'];
      delete this.FUZZY_PAYLOAD['post_filter'];
    }
    var input_val = jQuery('.appbase_input').eq(1).val();
    jQuery('.appbase_input').typeahead('val', '').typeahead('val', input_val).focus();

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