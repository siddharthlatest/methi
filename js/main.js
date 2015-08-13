function appbase_main() {

  var $this = this;

  //Variable js
  $this.variables = new variables('qHKbcf4M6:78a6cf0e-90dd-4e86-8243-33b459b5c7c5', '1', 'article');
  $this.url = $this.variables.URL;
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
  //Initialize Variables End

  //Bloodhound Start
  $this.engine = $this.variables.createEngine(function(length) {
    $this.appbase_total = length;
    if (length)
      $this.appbase_xhr_flag = true;
    else
      $this.appbase_xhr_flag = false;
  });
  //Bloodhound End

  $('.typeahead').typeahead({
    minLength: 2,
    highlight: true
  }, {
    name: 'my-dataset',
    limit: 100,
    source: $this.engine.ttAdapter(),
    templates: {
      suggestion: function(data) {
        // return '<div><h4><a href="https://www.digitalocean.com/community/tutorials/'+ data.fields.link + '">' + data.fields.title + '</a></h4><p> ' + "Abhi ke liye yeh hi body se kaam chala  lo baad mein kuch aur daal denge beta - Yo - I am loving this typing" + '</p></div>';
        return '<div><h4><a href="' + data.fields.link + '">' + data.highlight.title + '</a></h4><p> ' + data.highlight.body.join('...') + '...</p></div>';
      }
    }
  });

  $(window).scroll(function() {
    if ($(window).scrollTop() + $(window).height() == $(document).height()) {
      if (appbase_total != 0 && appbase_total > appbase_increment && appbase_xhr_flag) {
        $this.variables.scroll_xhr($this,'appabase', scroll_callback);
      }
    }
  });

  function scroll_callback(full_data) {
        var hits = full_data.hits.hits;
        appbase_increment += hits.length;
        $(".appbase_total_info").html('Showing 1-' + appbase_increment + ' of ' + appbase_total + " for \"" + $('.appbase_input').eq(1).val() + "\"");

        for (var i = 0; i < hits.length; i++) {
          var data = hits[i];
          var single_record_in = '<div><h4><a href="' + data.fields.link + '">' + data.highlight.title + '</a></h4><p> ' + data.highlight.body.join('...') + '...</p></div>'
          $('.tt-menu .tt-dataset.tt-dataset-my-dataset').append(single_record_in);
        }
        appbase_xhr_flag = true;
      };

}
appbase_main();
