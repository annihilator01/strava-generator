$(document).ready(() => {
    initDocumentBehaviour();
    initLocationInput();
    initLocationList();
    initForm();
})


let map,
    autocomplete,
    geocoder,
    markerMenu
    routeMarkers = {};

async function initMap() {
    geocoder = new google.maps.Geocoder();
    markerMenu = $('#marker-menu');

    let center_coords, zoom;
    getCurrentLocation()
        .then(position => {
            center_coords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            zoom = 17;
        })
        .catch(() => {
            center_coords = new google.maps.LatLng(55.755799012637766, 37.617742567387175);
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


function addMarker(coords, name) {
    const marker = new google.maps.Marker({
        position: coords,
        map: map,
        title: name,
    });

    let $routePoint;

    google.maps.event.addListener(marker, 'rightclick', (e) => {
        for (const property in e) {
            if (e[property] instanceof MouseEvent) {
                const mouseEvent = e[property];
                const left = mouseEvent.clientX;
                const top = mouseEvent.clientY;

                markerMenu.css('left', `${left}px`);
                markerMenu.css('top', `${top}px`);
                markerMenu.css('display', 'block');

                markerMenu.find('.add-marker')
                    .off('click')
                    .click(() => {
                        $routePoint = addRoutePoint(marker);
                    });

                markerMenu.find('.remove-marker')
                    .off('click')
                    .click(() => {
                        marker.setMap(null);
                        removeRoutePoint($routePoint);
                    });

                mouseEvent.preventDefault();
            }
        }
    });

    map.setCenter(coords);
}

function removeRoutePoint($routePoint) {
    if ($routePoint) {
        const marker = $routePoint.data('marker');
        const coordsString = getCoordsString(marker);

        marker.setMap(null);
        delete routeMarkers[coordsString];
        $routePoint.remove();
    }
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}


function initDocumentBehaviour() {
    $(document).click(() => {
        markerMenu.css('display', 'none');
    });
    $(window).contextmenu(() => {
        markerMenu.css('display', 'none');
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
        update: () => console.log('changed')  // TODO action
    });
}

function addRoutePoint(marker) {
    const coordsString = getCoordsString(marker);
    if (!routeMarkers[coordsString]) {
        routeMarkers[coordsString] = marker;
    } else {
        return routeMarkers[coordsString];
    }


    const name = marker.title;
    const $routePoint = getRoutePoint(name);
    $routePoint.data('marker', marker);

    if ($locationList.find('.list-group-item').length < 2) {
        $locationList.append($routePoint);
    } else {
        $locationList.find(' > .list-group-item:last-child').before($routePoint);
    }

    return $routePoint;
}

function getRoutePoint(name) {
    const $routePoint = $('<li/>', {
        class: 'list-group-item d-flex align-items-center'
    }).append(
        $('<i/>', {
            class: 'drag-item fas fa-bars fa-sm',
            'aria-hidden': 'true',
        })
    ).append(
        $('<p/>', {
            class: 'm-0 mr-3 no-select text-truncate',
            html: `&nbsp; ${name}`,
        })
    ).append(
        $('<i/>', {
            class: 'remove-item fas fa-trash fa-sm ml-auto',
            'aria-hidden': 'true',
        })
    );

    $routePoint.find('.remove-item').click(() => removeRoutePoint($routePoint));
    return $routePoint;
}

function getCoordsString(marker) {
    return `${marker.position.lat()},${marker.position.lng()}`
}