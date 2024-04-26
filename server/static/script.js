// Initialize map variable
let map;
let directionsService;
let directionsRenderer;

// Initialize map function
function initMap() {
    // Check if google is defined
    if (typeof google === 'undefined') {
        console.error('Google Maps JavaScript API is not loaded.');
        return;
    }
    
    // Set the map options
    const mapOptions = {
        zoom: 14,
        center: { lat: 0, lng: 0 } // Set the initial center of the map
    };
    // Create the map
    map = new google.maps.Map(document.getElementById("map"), mapOptions);
    
    // Initialize directions service and renderer
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    // Set the directions renderer to display the route on the map
    directionsRenderer.setMap(map);
}

document.getElementById('route-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const startLocation = encodeURIComponent(document.getElementById('start').value);
    const endLocation = encodeURIComponent(document.getElementById('end').value);
    
    fetch(`http://127.0.0.1:5000/optimize-route?start=${startLocation}&end=${endLocation}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        console.log('Response from server:', data);
        const routeList = data.route;
        // Display route information on the frontend
        displayRouteOnMap(startLocation, endLocation, routeList);
    })
    .catch(error => {
        console.error('Error fetching data:', error.message);
        const optimizedRoute = document.getElementById('optimized-route');
        optimizedRoute.innerHTML = `<p>Failed to retrieve optimized route: ${error.message}</p>`;
    });
});

function displayRouteOnMap(startLocation, endLocation, routeList) {
    const waypoints = [];
    routeList.forEach(step => {
        const location = step.replace(/Travel from | to /g, '').split(' to ');
        waypoints.push({
            location: location[0],
            stopover: true
        });
    });

    const request = {
        origin: startLocation,
        destination: endLocation,
        waypoints: waypoints,
        travelMode: 'DRIVING'
    };

    directionsService.route(request, function(result, status) {
        if (status === 'OK') {
            // Display the route on the map
            directionsRenderer.setDirections(result);
        } else {
            console.error('Directions request failed:', status);
            const optimizedRoute = document.getElementById('optimized-route');
            optimizedRoute.innerHTML = `<p>Failed to retrieve optimized route: ${status}</p>`;
        }
    });
}