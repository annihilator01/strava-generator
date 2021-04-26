$(document).ready(() => {
    initLocationInput();
    initLocationList();
    initForm();
    addLocation('First');
    addLocation('Second');
    addLocation('Third');
})


let map, autocomplete;
async function initMap() {
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
                new google.maps.Marker({
                    position: event.latLng,
                    map: map,
                    title: "Hello World!",
                });
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

        new google.maps.Marker({
            position: coords,
            map: map,
            title: "Hello World!",
        });

        map.setCenter(coords);
    });
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
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
    });
}

function addLocation(name) {
    const $listItem = getListItem(name);
    $locationList.append($listItem);
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

    return $listItem;
}
