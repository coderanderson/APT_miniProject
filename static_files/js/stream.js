var filtered_photos = new Array();
var markers = new Array();
var map;
var markerCluster;
var filtered_photos = new Array();
var date_min;
var date_max;

var photo_objs = new Array();

for(var i = 0; i < photos.length; i++) {
  var newObj = {
    url: photos[i],
    x: Math.random() * 75,
    y: Math.random() * 75,
    date: dates[i]
  };
  photo_objs.push(newObj);
}

function initMap() {}


function refresh() {

  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 2,
    center: {lat: 45, lng: 45}
  });

  for (i = 0; i < filtered_photos.length; i++) {  
    var id = i;
    var x = filtered_photos[i].x;
    var y = filtered_photos[i].y;
    var marker = new google.maps.Marker({
      position: new google.maps.LatLng(x, y),
      map: map,
      id: id,
      icon: 'http://www.christielakekids.com/_images/new/blue_circle.png'
    });

    markers.push(marker);
    photo_link = 'http://' + window.location.host + filtered_photos[i].url;
    var content = photo_link;

    google.maps.event.addListener(marker,'mouseover', (function(marker,content){ 
        return function() {
           marker.setIcon({
             url: content,
             scaledSize: new google.maps.Size(100, 100)
           });
        };
    })(marker,content)); 

    google.maps.event.addListener(marker, 'mouseout', (function(marker,content){ 
        return function() {
           marker.setIcon('http://www.christielakekids.com/_images/new/blue_circle.png');
        };
    })(marker,content)); 
  }

  markerCluster = new MarkerClusterer(map, markers,
      {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
}

//slider

$(function() {
  $( "#slider-range" ).slider({
    range: true,
    min: (new Date().getTime() / 1000) - 31536000 + 86400,
    max: (new Date().getTime() / 1000) + 86400,
    step: 86400,
    values: [ new Date('2017-01-01').getTime() / 1000, (new Date().getTime() / 1000) + 86400 ],
    slide: function( event, ui ) {
      $( "#amount" ).val( (new Date(ui.values[ 0 ] *1000).toDateString() ) + " - " + (new Date(ui.values[ 1 ] *1000)).toDateString() );
      date_min = ui.values[ 0 ] * 1000;
      date_max = ui.values[ 1 ] * 1000;
      markerCluster.clearMarkers();
      markers = new Array();
      filter();
      refresh();
    }
  });
  $( "#amount" ).val( (new Date($( "#slider-range" ).slider( "values", 0 )*1000).toDateString()) +
    " - " + (new Date($( "#slider-range" ).slider( "values", 1 )*1000)).toDateString());
  date_min = $( "#slider-range" ).slider( "values", 0 )*1000;
  date_max = $( "#slider-range" ).slider( "values", 1 )*1000;
  filter();
  setTimeout(refresh, 300);
});

function filter() {
  filtered_photos = new Array();
  for(var i = 0; i < photo_objs.length; i++) {
    var p_date = photo_objs[i].date;
    var date_value = new Date(p_date.substring(0, 19)).getTime();
    if(date_value >= date_min && date_value <= date_max) {
      filtered_photos.push(photo_objs[i]);
    }
  }
}
