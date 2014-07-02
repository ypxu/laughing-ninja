// Geo API make request to backend


(function(win, options){
  var geo_api = {},
      protocol = win.location.protocol,
      api_url = protocol + '//' + win.location.host + '/api/'

  function get_near_stops(latitude, longitude, radius, callback, errback) {
    var url = api_url + 'near_routes.json?',
        args = {'lat': latitude, 'lon': longitude, 'radius': radius}
    //$.get(url + $.param(args), callback)
    $.ajax({
      url: url + $.param(args),
      type: 'GET',
      success: callback,
      error: errback
    });
  }

  function get_full_stop(stop_key, callback, errback) {
    var url = api_url + 'stop_config.json?',
        args = {'stop': stop_key || ''};
    //$.get(url + $.param(args), callback)
    $.ajax({
      url: url + $.param(args),
      type: 'GET',
      success: callback,
      error: errback
    });
  } 

  geo_api = {
    get_near_stops: get_near_stops,
    get_full_stop: get_full_stop
  }

  win.geoapi = geo_api;

})(window);

