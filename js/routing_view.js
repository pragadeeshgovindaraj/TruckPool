function setOnMap(routeJson) {
    debugger;
    route_json = routeJson;
    //initMap_route(); // Call the function to initialize the map once the data is set
}

function initMap_route() {
    debugger;

    const coordinates = route_json.waypoints;
    const waypoints = coordinates.map(function(coord) {
        return {
            location: new google.maps.LatLng(coord.lat, coord.lng),
            stopover: true
        };
    });

    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    const map = new google.maps.Map(document.getElementById('map-static-route'), {
        zoom: 8,
        center: { lat: 45.5078918, lng: -73.5549053 } // Adjust the center based on your needs
    });

    directionsRenderer.setMap(map);

    const request = {
        origin: waypoints[0].location,
        destination: waypoints[waypoints.length - 1].location,
        waypoints: waypoints.slice(1, waypoints.length - 1),
        optimizeWaypoints: false,
        travelMode: 'DRIVING'
    };

    directionsService.route(request, function(response, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}