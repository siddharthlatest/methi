function appbase_main() {

  var $this = this;

  //Variable js
  $this.variables = new variables('sD2YBlBKk:706d9a4f-56b9-4513-a35d-14885d60373a', 'methi-1299', 'article', 'appbase');
  $this.url = $this.variables.createURL();
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

  $.ajax({
    type: "GET",
    url: 'https://accapi.appbase.io/user',
    dataType: 'json',
    contentType: "application/json",
    success: function(full_data) {
    },
    error:function(){
      window.location.href = "index.html";
    }
  });

  function scroll_callback(full_data, method) {
    var hits = full_data.hits.hits;
    if (hits.length) {
      $this.appbase_increment += hits.length;
      $("#search-title").html($this.variables.showing_text($this.appbase_increment, $this.appbase_total, $('.typeahead').eq(1).val(), full_data.took));

      for (var i = 0; i < hits.length; i++) {
        var data = hits[i];
        var single_record_in = '<div><h4><a href="' + data.fields.link + '">' + data.highlight.title + '</a></h4><p> ' + data.highlight.body.join('...') + '...</p></div>'
        $('.tt-menu .tt-dataset.tt-dataset-my-dataset').append(single_record_in);
      }
      appbase_xhr_flag = true;
    }
    else{
      $(".appbase_total_info").html($this.variables.NO_RESULT_TEXT);
      $('.tt-menu .tt-dataset.tt-dataset-my-dataset').html('');
    }
  };
  //Initialize Variables End

  //Bloodhound Start
  $this.engine = $this.variables.createEngine($this, function(length) {
    $this.appbase_total = length;
    if (length)
      $this.appbase_xhr_flag = true;
    else
      $this.appbase_xhr_flag = false;
  }, scroll_callback);
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

  $('.typeahead').on('keyup', function() {
    if ($(this).val().length == 0)
      $('.appbase_total_info').text($this.variables.NO_RESULT_TEXT);
  });

  $(window).scroll(function() {
    if ($(window).scrollTop() + $(window).height() == $(document).height()) {
      if ($this.appbase_total != 0 && $this.appbase_total > $this.appbase_increment && $this.appbase_xhr_flag) {
        alert('hi');
        $this.variables.scroll_xhr($this, 'appbase', scroll_callback);
      }
    }
  });


}
appbase_main();

