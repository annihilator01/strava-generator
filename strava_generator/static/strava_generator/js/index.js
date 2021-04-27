$(document).ready(() => {
    initDocumentBehaviour();
    initLocationInput();
    initLocationList();
    initForm();
    addLocation('First');
    addLocation('Second');
    addLocation('Third');
})


let map,
    autocomplete,
    geocoder,
    markerMenu;
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

    google.maps.event.addListener(marker, 'rightclick', (e) => {
        for (const prop in e) {
            if (e[prop] instanceof MouseEvent) {
                const mouseEvt = e[prop];
                const left = mouseEvt.clientX;
                const top = mouseEvt.clientY;

                markerMenu.css('left', `${left}px`);
                markerMenu.css('top', `${top}px`);
                markerMenu.css('display', 'block');

                mouseEvt.preventDefault();
            }
        }
    });

    map.setCenter(coords);
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}


function initDocumentBehaviour() {
    $(document).click(() => {
        if (markerMenu.css('display') !== 'none') {
            markerMenu.css('display', 'none');
        }
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

function addLocation(name) {
    const $listItem = getListItem(name);

    if ($locationList.find('.list-group-item').length < 2) {
        $locationList.append($listItem);
    } else {
        $locationList.find(' > .list-group-item:last-child').before($listItem);
    }
}

function getListItem(name) {
    const $listItem = $('<li/>', {
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

    $listItem.children('.remove-item').click(() => $listItem.remove());
    $listItem.data('kek', new Date());

    return $listItem;
}
