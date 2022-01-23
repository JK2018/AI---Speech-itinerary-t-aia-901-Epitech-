function initMap() {
    if (route) {
        const directionsService = new google.maps.DirectionsService();
        const directionsRenderer = new google.maps.DirectionsRenderer();
        const map = new google.maps.Map(document.getElementById("map"), {
            center: { lat: 46.6315, lng: 2.4571 },
            zoomControl: false,
            gestureHandling: "none",
            streetViewControl: false
        });

        directionsRenderer.setMap(map);
        calculateAndDisplayRoute(directionsService, directionsRenderer, formatPythonArray(route));
    }
}

function calculateAndDisplayRoute(directionsService, directionsRenderer, route) {
    route = route.route.length ? route.route : {};

    if (route.length) {
        createRouteList(route);

        const travelMode = route.length == 2 ? google.maps.TravelMode.TRANSIT : google.maps.TravelMode.WALKING;
        const transitOptions = route.length == 2 ? { modes: ['TRAIN'] } : {};

        var waypoints = [];
        for (var i = 1; i < route.length - 1; i++) {
            waypoints.push({
                location: new google.maps.LatLng(route[i]['lat'], route[i]['lng']),
                stopover: false
            });
        }

        directionsService
            .route({
                origin: route[0],
                destination: route[route.length - 1],
                waypoints: waypoints,
                travelMode: travelMode,
                transitOptions: transitOptions,
            })
            .then((response) => {
                directionsRenderer.setDirections(response);
            })
            .catch((e) => window.alert("Directions request failed due to " + e));
    }
}

function onMic() {
    document.getElementById("sendMic").style.display = 'none';
    document.getElementById("pendingMic").style.display = 'block';
}

function submitFile() {
    document.getElementById("sendUpload").style.display = 'none';
    document.getElementById("pendingUpload").style.display = 'block';
    document.getElementById("uploadForm").submit();
}

function formatPythonArray(json) {
    var object = '{"route": [' + json.substring(1);
    object = object.substring(0, object.length - 1) + ']}';
    object = object.replaceAll('&#34;', '"');
    return JSON.parse(object);
}

function createRouteList(route) {
    for (var i = 0; i < route.length; i++) {
        const mainStation = (i == 0 || i == route.length - 1)
        addRouteOnList(route[i]["station"], route[i]["city"], mainStation);
    }
}

function addRouteOnList(station, city, mainStation) {
    var ul = document.getElementById("route-list");
    var li = document.createElement("li");

    if (mainStation){
        li.classList.add("main");
    } else {
        li.classList.add("second");
    }

    li.appendChild(document.createTextNode(station + ", " + city));
    ul.appendChild(li);
}