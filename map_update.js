let map = null
let boatMarker = null
let waypointLine = null
let startToEndLine = null
let waypointCords = []

let firstPanFlag = null

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
    
    if (firstPanFlag == null){
        // Move the map to the marker
        map.panTo([lat, lon]);
        firstPanFlag = true
    }
}

// Add waypoints to map
function addWaypoint(mission_type, lat, lon, index) {
    if (!window.waypoints) {
        window.waypoints = [];
    }

    waypointCords.push([lat, lon])

    let icon

    if (mission_type == "Point to Point"){
        // Use a DivIcon to display the number
        icon = L.divIcon({
            className: 'waypoint-marker', // you can style this in CSS
            html: '<div style="background:blue;color:white;border-radius:50%;width:24px;height:24px;line-height:24px;text-align:center;">' + index + '</div>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
    }
    else if (mission_type == "Lawnmower"){
        // Use a DivIcon to display the number
        icon = L.divIcon({
            className: 'waypoint-marker', // you can style this in CSS
            html: '<div style="background:red;color:white;border-radius:50%;width:24px;height:24px;line-height:24px;text-align:center;">'  + '</div>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
    }

    let marker = L.marker([lat, lon], { icon: icon }).addTo(map);
    window.waypoints.push(marker);

    addWaypointLine();
    
    if (mission_type == "Lawnmower"){
        drawStartToEndLine();
    }
}

// Clear waypoints on the map
function clearWaypoints() {
    if (!window.waypoints) return;

    for (let i = 0; i < window.waypoints.length; i++) {
        map.removeLayer(window.waypoints[i]);
    }
    window.waypoints = [];

    waypointCords = []
    map.removeLayer(waypointLine)
    map.removeLayer(startToEndLine)
}

// Add line between waypoints
function addWaypointLine() {
    if (waypointLine) {
        map.removeLayer(waypointLine);
    }

    waypointLine = L.polyline(waypointCords, {
        color: 'yellow',
        weight: 3
    }).addTo(map);
}

function drawStartToEndLine() {
    if (!waypointCords || waypointCords.length < 2) {
        return; // need at least 2 points
    }

    if (startToEndLine != null){
        map.removeLayer(startToEndLine);
    }

    let start = waypointCords[0];
    let end = waypointCords[waypointCords.length - 1];

    startToEndLine = L.polyline([start, end], {
        color: 'yellow',
        weight: 3
    }).addTo(map);
}

