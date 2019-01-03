origin_coords = origin_coords.split(',');
destination_coords = destination_coords.split(',');
origin_coords = [parseFloat(origin_coords[1]), parseFloat(origin_coords[0])];
destination_coords = [parseFloat(destination_coords[1]), parseFloat(destination_coords[0])];
let view = origin_coords;

let zoom = 16;

var map = L.map('map').setView(view, 16);
directions = JSON.parse(directions);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    id: 'mapbox.streets'
}).addTo(map);


L.geoJSON(directions, {
    style: function (feature) {
        return {
            "color": "#959595",
            weight: 5,
            opacity: .7,
            lineJoin: 'round',
        };
    }

}).addTo(map);

if(walking_directions){
    walking_directions = JSON.parse(walking_directions);
    var localization_coords = walking_directions.features[0].geometry.coordinates[0];
    localization_coords = [localization_coords[1], localization_coords[0]];
    L.marker(localization_coords).addTo(map).bindPopup("<b>Twoja lokalizacja</b>");
    L.geoJSON(walking_directions, {
    style: function (feature) {
        return {
            weight: 5,
            opacity: .7,
            dashArray: '10,8',
            lineJoin: 'round'
        };
    }

}).addTo(map);
}

L.marker(origin_coords).addTo(map).bindPopup("<center><b>" + origin_name + "</b><br>Stąd jedziesz</center>");
L.marker(destination_coords).addTo(map).bindPopup("<center><b>" + destination_name + "</b><br>Tutaj wysiadasz</center>");