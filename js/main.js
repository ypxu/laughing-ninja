
$(function(){

  Application.init()

});


var Application = (function(){

  var geopos,
      google_map,
      geoapi = window.geoapi,
      geolocation = navigator.geolocation,
      Model = Backbone.Model,
      View = Backbone.View,
      Collection = Backbone.Collection;

  var Stop = Model.extend({
    defaults: {
      'stopTitle': '',
      'routeTitle': '',
      'agencyTitle': '',
      'direction': '',
      'departure': 'Loading'
    },

    template: _.template($("#map-info-window").html()),

    load_stop: function(callback){
      var that = this
      geoapi.get_full_stop(this.get('key'), function(data){
        var result = data['result'],
            prediction = result['prediction'] || {};
        that.set(result)
        that.set({'departure': prediction['minutes'] || 'No available'})

        if(callback) {
          callback(result);
        }

        // Add Marker and InfoWindow into google_map
        var marker = new google.maps.Marker({
              position: new google.maps.LatLng(that.get('lat'), that.get('lon')),
              map: google_map,
              title: that.get('key')
          });
        var infoWindow = new google.maps.InfoWindow({
              content: that.template(that.toJSON())
          });

        google.maps.event.addListener(marker, 'click', function() {
            infoWindow.open(google_map, marker);
          });
      }, function(err){
        that.set({'departure': 'No available'})
      });
    }
  });

  var StopList = Collection.extend({
    model: Stop
  })

  var StopRowView = View.extend({

    tagName: 'tr',

    template: _.template($('#stop-row').html()),

    events: {
      "click #update": "handle_update"
    },

    initialize: function(){
      this.model.on("change", this.render, this)
    },

    handle_update: function(e){
      var element = $(e.currentTarget),
          that = this;
      element.text('Loading...');
      this.model.load_stop(function(stop){
        element.text('Update');
      });
    },

    render: function(){
      this.$el.html(this.template(this.model.toJSON()));
      // load stop info and predition
      if(!this.model.get('stopTitle')) {
        this.model.load_stop()
      }
      return this
    }
  })

  var StopTableView = View.extend({

    el: '#stop-table',

    views: [],

    initialize: function(){
      this.collection.on('add', this.render, this);
      this.collection.on('reset', this.render, this);
    },

    render: function(){
      var that = this;
      this.$('tbody').html('')
      this.collection.each(function(model, index){
        view = that.views[index]
        if(view) {
          view.model.set(model.toJSON())
        } else {
          view = new StopRowView({
            model: model
          })
        }
        that.$('tbody').append(view.render().$el)
      });
      return this
    }

  });

  function fetch_maps_api () {
    var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://maps.googleapis.com/maps/api/js?v=3.exp&' +
        'callback=initialize_map&key=AIzaSyDovt924MfA3PuiSAf7jvd9awXPTk4hnEw';
    document.body.appendChild(script);
  }

  function initialize_map() {
    if(geopos){
      var mapOptions = {
        center: new google.maps.LatLng(geopos.latitude, geopos.longitude),
        zoom: 17
      };
      google_map = new google.maps.Map(document.getElementById("map-canvas"),
          mapOptions);

      // Current Location's Marker
      var meMarker = new google.maps.Marker({
          position: new google.maps.LatLng(geopos.latitude, geopos.longitude),
          map: google_map
        })
      meMarker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png')
    }
  }

  function get_value_from_url(key) {
    var regex = ".*[?&]?" ,
        result,
        val = '',
        url = window.location.href;

    if(!key || url.indexOf('?') < 0) {
      return val
    }
    try{
      result = url.match(new RegExp(regex + key + "=(.*)"));
      if(result && result.length == 2) {
        val = parseInt(result[1])
      }
    }catch(e){
      // pass
    }
    return val
  }

  var stopList = new StopList();

  return {
    init: function(){

      var radius = get_value_from_url('radius') || 200,
          tableView = new StopTableView({
        collection: stopList
      })

      // Prevent people from screwing around
      if(radius > 1000) {
        radius = 200
      }

      $("#label-radius").html(radius);

      // Google Maps
      window.initialize_map = initialize_map;

      geolocation.getCurrentPosition(function(pos){
        geopos = pos.coords;

        geoapi.get_near_stops(geopos.latitude, geopos.longitude, radius,
          function(resp){
            stopList.reset(resp['result'])
            fetch_maps_api();
        },function(){
            // handle user rejection
            stopList.reset([])
        })
      })
    }
  }

})()
