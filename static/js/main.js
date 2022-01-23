function initMap() {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 41.85, lng: -87.65 },
    });

    directionsRenderer.setMap(map);
    calculateAndDisplayRoute(directionsService, directionsRenderer);
}

function calculateAndDisplayRoute(directionsService, directionsRenderer) {
    directionsService
        .route({
            origin: {
                query: "chicago, il",
            },
            destination: {
                query: "st louis, mo",
            },
            travelMode: google.maps.TravelMode.DRIVING,
        })
        .then((response) => {
            directionsRenderer.setDirections(response);
        })
        .catch((e) => window.alert("Directions request failed due to " + status));
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