const MAX_ROUTE_POINTS_NUM = 26;
const LABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const activity_limit = {
    run: {
        val: 3000,
        warn: 'Run activity must take at least 3km'
    },
    bike: {
        val: 5000,
        warn: 'Bike activity must take at least 5km'
    }
}


$(document).ready(() => {
    initDocumentBehaviour();
    initLocationInput();
    initLocationList();
    initForm();
});

let map,
    autocomplete,
    geocoder,
    directionService,
    directionsRenderer,
    routeMarkers = {};

let $markerMenu,
    $statusBar;

async function initMap() {
    directionService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({suppressMarkers: true});
    geocoder = new google.maps.Geocoder();
    $markerMenu = $('#marker-menu');
    $statusBar = getStatusBar();

    let center_coords, zoom;
    getCurrentLocation()
        .then(position => {
            center_coords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            zoom = 17;
        })
        .catch(() => {
            center_coords = new google.maps.LatLng(59.9386, 30.3141);
            zoom = 10;
        })
        .finally(() => {
            map = new google.maps.Map($('#map')[0], {
                center: center_coords,
                zoom: zoom,
                disableDefaultUI: true,
                zoomControl: true,
                scaleControl: true,
                fullscreenControl: true
            });

            map.addListener("click", (event) => {
                geocoder.geocode(
                    {location: event.latLng},
                    (results, status) => {
                        if (status === google.maps.GeocoderStatus.OK) {
                            addMarker(event.latLng, results[0].formatted_address);
                        } else {
                            addMarker(event.latLng, `${event.latLng.lat().toFixed(3)}, ${event.latLng.lng().toFixed(3)}`);
                        }
                    }
                )
            });

            map.controls[google.maps.ControlPosition.LEFT_TOP].push($statusBar[0]);
            directionsRenderer.setMap(map);
        });

    const locationInput = $locationInput[0];
    autocomplete = new google.maps.places.Autocomplete(locationInput);
    google.maps.event.addListener(autocomplete, 'place_changed', () => {
        $locationInput.val('');

        const place = autocomplete.getPlace();
        const coords = new google.maps.LatLng(
            place.geometry.location.lat(),
            place.geometry.location.lng()
        )

        addMarker(coords, place.formatted_address);
    });
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}

function getStatusBar() {
    return $('<h3/>').append($('<div/>', {
        id: 'status-bar',
        class: 'badge badge-success no-select',
        text: '0 km'
    }))
    // return $('<div/>', {
    //     id: 'status-bar',
    //     class: '',
    // }).append(
    //     $('<div/>')
    // ).append(
    //     $('<div/>', {
    //     })
    // )
}

function initDocumentBehaviour() {
    $(document).click(() => {
        $markerMenu.css('display', 'none');
    });
    $(window).contextmenu(() => {
        $markerMenu.css('display', 'none');
    })
}


const $locationInput = $('#location-input');
function initLocationInput() {
}


const genForm = $('.gen-form');
function initForm() {
    genForm.submit(e => {
        e.preventDefault();
    });
}


const $locationList = $('#location-list');
function initLocationList() {
    $locationList.sortable({
        axis: 'y',
        handle: '.drag-item',
        scrollSpeed: 10,
        tolerance: 'pointer',
        update: drawRoute
    });
}