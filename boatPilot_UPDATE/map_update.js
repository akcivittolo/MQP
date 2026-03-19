let map = null
let boatMarker = null

// This gets the map ID folium randomly assigns
function getMap() {
    if (map) return map;

    for (let key in window) {
        if (key.startsWith("map_")) {
            map = window[key];
            return map;
        }
    }
    return null;
}

function initBoatMarker(lat, lon) {
    boatMarker = L.marker([lat, lon], {
        icon: L.icon({
            iconUrl: markerIconPath,
            iconSize: [100, 100],
            iconAnchor: [50, 50]
        })
    }).addTo(map);

    // Allows coords to be connected back to the main python program
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.pyHandler = channel.objects.pyHandler;

        map.on('click', function(e) {
            pyHandler.mapClicked(e.latlng.lat, e.latlng.lng);
        });
    });
}

// Update the boat marker's position and rotation
function updateBoatMarker(lat, lon, hdg) {
    // Update marker position and rotation
    boatMarker.setLatLng([lat, lon]);
    boatMarker.setRotationAngle(hdg);
    
    
    // Move the map to the marker
    map.panTo([lat, lon]);
}

// Add waypoints to map
function addWaypoint(lat, lon, index) {
    if (!window.waypoints) {
        window.waypoints = [];
    }

    // Use a DivIcon to display the number
    let icon = L.divIcon({
        className: 'waypoint-marker', // you can style this in CSS
        html: '<div style="background:blue;color:white;border-radius:50%;width:24px;height:24px;line-height:24px;text-align:center;">' + index + '</div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    let marker = L.marker([lat, lon], { icon: icon }).addTo(map);
    window.waypoints.push(marker);
}

// Clear waypoints on the map
function clearWaypoints() {
    if (!window.waypoints) return;

    for (let i = 0; i < window.waypoints.length; i++) {
        map.removeLayer(window.waypoints[i]);
    }
    window.waypoints = [];
}

