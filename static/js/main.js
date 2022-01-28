function initMap(route) {
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
        calculateAndDisplayRoute(directionsService, directionsRenderer, route);
    }
}

function calculateAndDisplayRoute(directionsService, directionsRenderer, route) {
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
                origin: new google.maps.LatLng(route[0]['lat'], route[0]['lng']),
                destination: new google.maps.LatLng(route[route.length - 1]['lat'], route[route.length - 1]['lng']),
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
    $("#sendMic").css("display", "none");
    $("#pendingMic").css("display", "block");
}

function submitFile() {
    $("#sendUpload").css("display", "none");
    $("#pendingUpload").css("display", "block");
    $("#upload-form").submit();
}

function resetPage() {
    $("#sendMic").css("display", "block");
    $("#pendingMic").css("display", "none");
    $("#sendUpload").css("display", "flex");
    $("#pendingUpload").css("display", "none");

    $("#route-list li").remove();
}

function createRouteList(route) {
    for (var i = 0; i < route.length; i++) {
        const mainStation = (i == 0 || i == route.length - 1)
        addRouteOnList(route[i]["station"], mainStation);
    }
}

function addRouteOnList(station, mainStation) {
    var ul = document.getElementById("route-list");
    var li = document.createElement("li");

    if (mainStation){
        li.classList.add("main");
    } else {
        li.classList.add("second");
    }

    li.appendChild(document.createTextNode(station));
    ul.appendChild(li);
}

function submitHandler(form, actionUrl) {
    $.ajax({
        type: "POST",
        url: actionUrl,
        data: form.serialize(),
        success: function(data) {
            data = JSON.parse(data);
            resetPage();
            initMap(data[0]);
        }
    });
}

function submitFileHandler(form, actionUrl) {
    var formData = new FormData();
    var files = $("#upload-form input[name='file']")[0].files;
    
    // Check file selected or not
    if(files.length > 0 ){
        formData.append('file',files[0]);
    }

    $.ajax({
        type: "POST",
        url: actionUrl,
        data: formData,
        contentType: false,
        processData: false,
        success: function(data) {
            data = JSON.parse(data);
            resetPage();
            initMap(data[0]);
        }
    });
}

$(document).ready(function() {
    // When search form is submited
    $("#search-form").submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var actionUrl = form.attr('action');

        submitHandler(form, actionUrl);
    });

    // When mic form is submited
    $("#mic-form").submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var actionUrl = form.attr('action');

        submitHandler(form, actionUrl);
    });

    // When upload form is submited
    $("#upload-form").submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var actionUrl = form.attr('action');

        submitFileHandler(form, actionUrl);
    });
});