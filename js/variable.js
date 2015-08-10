function variables() {

  var default_variable = {
    URL: 'http://qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5@scalr.api.appbase.io/1/article/_search',
    SIZE: 20,
    SEARCH_PAYLOAD: CreateSearchPayload,
    ENGINE: CreateEngine,
    appbase_total:0
  };
  return default_variable;

  function CreateSearchPayload() {
    return {
      "from": 0,
      "size": default_variable.SIZE,
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
  }

  function CreateEngine(callback) {
    var engineInside = {
      name: 'history',
      limit: 100,
      datumTokenizer: function(datum) {
        return Bloodhound.tokenizers.whitespace(datum);
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: 'http://qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5@scalr.api.appbase.io/1/article/_search',
        //  url: 'http://localhost:9200/digitalocean/article/_search',
        // he time interval in milliseconds that will be used by rateLimitBy. Defaults to 300
        rateLimitWait: 300,
        // Function that provides a hook to allow you to prepare the settings object passed to transport when a request is about to be made.
        // The function signature should be prepare(query, settings), where query is the query #search was called with
        // and settings is the default settings object created internally by the Bloodhound instance. The prepare function should return a settings object.
        prepare: function(query, settings) {

          settings.type = "POST";
          settings.xhrFields = {
            withCredentials: true
          };
          settings.headers = {
            "Authorization": "Basic " + btoa("qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5")
          };
          settings.contentType = "application/json; charset=UTF-8";
          search_payload = default_variable.SEARCH_PAYLOAD();
          settings.data = JSON.stringify(search_payload);
          return settings;
        }
        
      }
    };

    return engineInside;
  }

}