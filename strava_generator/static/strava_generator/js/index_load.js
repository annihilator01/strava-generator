const MAX_ROUTE_POINTS_NUM = 26;
const LABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

const INIT_MAP_ZOOM = 10;
const DEFAULT_MAP_ZOOM = 15;

const activity_limit = {
    run: {
        val: 3000,
        warn: 'Run activity must take at least 3 km'
    },
    bike: {
        val: 5000,
        warn: 'Bike activity must take at least 5 km'
    }
}


$(document).ready(() => {
    initDocumentBehaviour();
    initLocationInput();
    initRemoveAllMarkersButton();
    initLocationList();
    initActivityTypeGroup();
    initDatetimePicker();
    initGenerateFileButton();
    initForm();
});


let map,
    autocomplete,
    geocoder,
    directionService,
    directionsRenderer,
    routeMarkers = {};

let $markerMenu = $('#marker-menu'),
    $statusBar = getStatusBar(),
    $statusBarInfo = $statusBar.children('#status-bar');

async function initMap() {
    directionService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({suppressMarkers: true});
    geocoder = new google.maps.Geocoder();
    $statusBarInfo.data('totalDistance', 0);

    let center_coords, zoom;
    getCurrentLocation()
        .then(position => {
            center_coords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            zoom = DEFAULT_MAP_ZOOM;
        })
        .catch(() => {
            center_coords = new google.maps.LatLng(59.9386, 30.3141);
            zoom = INIT_MAP_ZOOM;
        })
        .finally(() => {
            map = new google.maps.Map($('#map')[0], {
                center: center_coords,
                zoom: zoom,
                disableDefaultUI: true,
                zoomControl: true,
                gestureHandling: 'greedy',
                scaleControl: true,
                fullscreenControl: true,
                styles: [
                    {elementType: "geometry", stylers: [{color: "#242f3e"}]},
                    {elementType: "labels.text.stroke", stylers: [{color: "#242f3e"}]},
                    {elementType: "labels.text.fill", stylers: [{color: "#746855"}]},
                    {
                        featureType: "administrative.locality",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#d59563"}],
                    },
                    {
                        featureType: "poi",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#d59563"}],
                    },
                    {
                        featureType: "poi.park",
                        elementType: "geometry",
                        stylers: [{color: "#263c3f"}],
                    },
                    {
                        featureType: "poi.park",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#6b9a76"}],
                    },
                    {
                        featureType: "road",
                        elementType: "geometry",
                        stylers: [{color: "#38414e"}],
                    },
                    {
                        featureType: "road",
                        elementType: "geometry.stroke",
                        stylers: [{color: "#212a37"}],
                    },
                    {
                        featureType: "road",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#9ca5b3"}],
                    },
                    {
                        featureType: "road.highway",
                        elementType: "geometry",
                        stylers: [{color: "#746855"}],
                    },
                    {
                        featureType: "road.highway",
                        elementType: "geometry.stroke",
                        stylers: [{color: "#1f2835"}],
                    },
                    {
                        featureType: "road.highway",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#f3d19c"}],
                    },
                    {
                        featureType: "transit",
                        elementType: "geometry",
                        stylers: [{color: "#2f3948"}],
                    },
                    {
                        featureType: "transit.station",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#d59563"}],
                    },
                    {
                        featureType: "water",
                        elementType: "geometry",
                        stylers: [{color: "#17263c"}],
                    },
                    {
                        featureType: "water",
                        elementType: "labels.text.fill",
                        stylers: [{color: "#515c6d"}],
                    },
                    {
                        featureType: "water",
                        elementType: "labels.text.stroke",
                        stylers: [{color: "#17263c"}],
                    },
                ],
            });

            map.addListener('click', (event) => {
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

            map.addListener('zoom_changed', () => {
                $markerMenu.css('display', 'none');
            });

            map.addListener('mousedown', () => {
                $markerMenu.css('display', 'none');
            });

            map.controls[google.maps.ControlPosition.LEFT_TOP].push($statusBar[0]);
            directionsRenderer.setMap(map);
        });

    const locationInput = $locationInput[0];
    autocomplete = new google.maps.places.Autocomplete(locationInput);
    autocomplete.setFields(['geometry', 'formatted_address']);
    google.maps.event.addListener(autocomplete, 'place_changed', () => {
        $locationInput.val('');

        const place = autocomplete.getPlace();
        const coords = new google.maps.LatLng(
            place.geometry.location.lat(),
            place.geometry.location.lng()
        )

        addMarker(coords, place.formatted_address);
        map.setZoom(DEFAULT_MAP_ZOOM);
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
        class: 'badge badge-warning user-select-none',
        text: '0 km',
        title: activity_limit.run.warn
    }));
}

function initDocumentBehaviour() {
    $(document).on('click scroll',(e) => {
        if (e.target.currentSrc !== 'https://maps.gstatic.com/mapfiles/transparent.png') {
            $markerMenu.css('display', 'none');
        }
    });
}


const $locationInput = $('#location-input');
function initLocationInput() {
}


const $removeAllMarkersButton = $('#remove-all-markers');
function initRemoveAllMarkersButton() {
    $removeAllMarkersButton.click(removeAllMarkers);
}

function removeAllMarkers() {
    const $locationListChildren = $locationList.children('.list-group-item');

    $locationListChildren.each(function () {
        const marker = $(this).data('marker');
        marker.setMap(null);
    });

    clearRouteRenderer();
    showNoRoutePointsInfo();
    turnWarning(
        $statusBarInfo,
        '0 km', activity_limit[getCheckedActivity()].warn,
        'totalDistance', 0
    );
    $locationList.html('');
    $removeAllMarkersButton.blur();
    $generateGpxButton.prop('disabled', true);
}


const $activityTypeGroup = $('#activity-type');
function initActivityTypeGroup() {
    $activityTypeGroup.change(updateStatusBarWithActivityType);
}

function updateStatusBarWithActivityType() {
    const checkedActivity = getCheckedActivity();
    const totalDistance = $statusBarInfo.data('totalDistance');
    if (totalDistance < activity_limit[checkedActivity].val) {
        turnWarning(
            $statusBarInfo,
            null, activity_limit[checkedActivity].warn,
            null, null
        );
    } else {
        turnSuccess(
            $statusBarInfo,
            null, '',
            null, null
        );
    }
}

function getCheckedActivity() {
    return $activityTypeGroup.find('input[name="options"]:checked').val();
}


$datetimePicker = $('#datetime-picker');
$nowTimeCheckbox = $('#now-time-checkbox');
function initDatetimePicker() {
    $datetimePicker.Zebra_DatePicker({
        format: 'Y-m-d H:i:s',
        open_icon_only: true,
        show_clear_date: false,
        onChange: () => {
            const dateObject = new Date($datetimePicker.val());
            $datetimePicker.data('datetime', dateObject);
        }
    });

    $nowTimeCheckbox.change(function () {
        $datetimePicker.prop('disabled', this.checked);
        if (this.checked) {
            setNowTimeInInterval();
        } else {
            const intervalId = $datetimePicker.data('intervalId');
            clearInterval(intervalId);
        }
        $datetimePicker.data('Zebra_DatePicker').update();
    });

    $nowTimeCheckbox.trigger('change');

}

function setNowTimeInInterval() {
    function setNowTime() {
        const nowTime = new Date();
        $datetimePicker.data('Zebra_DatePicker').set_date(nowTime);
        $datetimePicker.data('datetime', nowTime);
    }

    setNowTime();
    const intervalId = setInterval(setNowTime, 1000);
    $datetimePicker.data('intervalId', intervalId);
}


$generateGpxButton = $('#generate-gpx-button');
function initGenerateFileButton () {
    $generateGpxButton.click(generateGpxFile);
}

$usesLeft = $('#uses-left');
function generateGpxFile() {
    $generateGpxButton.prop('disabled', true);
    $generateGpxButton.data('originalHtml', $generateGpxButton.html());
    $generateGpxButton.html(getLoadingSpinner());

    const $locationListChildren = $locationList.children('.list-group-item');
    let coordsArr = [];
    $locationListChildren.each(function () {
        coordsArr.push(getCoordsString($(this).data('marker')));
    });

    const origin = coordsArr[0];
    const destination = coordsArr[coordsArr.length - 1];
    const waypoints = coordsArr.splice(1, coordsArr.length - 2).join('|');
    const activityType = getCheckedActivity();

    const endDatetime = $datetimePicker.data('datetime');
    const endTime = getFormattedDatetime(endDatetime);

    const urlRequest = `/api/v1/generate-strava-gpx?
                        origin=${origin}&
                        destination=${destination}&
                        waypoints=${waypoints}&
                        activity_type=${activityType}&
                        end_time=${endTime}`
                        .replace(/(\r\n|[\r\n\t\s])/gm, '');

    fetch(urlRequest)
        .then(rawResponse => rawResponse.json())
        .then(response => {
            const code = response.code;
            switch (code) {
                case 200:
                    const uses_left = response.uses_left;
                    $usesLeft.text(uses_left);

                    const generatedGpx = response.gpx;
                    const blob = new Blob([generatedGpx], {type: 'text/plain'});

                    const nowTime = getFormattedDatetime(new Date()).replace(/[-:]/gm, '_')
                    saveAs(blob, `strava_${nowTime}.gpx`);
                    break;

                case 400:
                    showErrorMessage(response.error);
                    break;

                case 403:
                    window.location.replace('/');
                    break;
            }
        })
        .catch(() => {
            showErrorMessage('Bad Internet connection')
        })
        .finally(() => {
            $generateGpxButton.prop('disabled', false);
            $generateGpxButton.html($generateGpxButton.data('originalHtml'));
        })
}

function getLoadingSpinner() {
    return `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Loading...`;
}

function getFormattedDatetime(datetime) {
    return `${new Date(
        datetime.getTime() -
        (datetime.getTimezoneOffset() * 60000)
    ).toJSON().split('.')[0]}`;
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
        containment: 'parent',
        scrollSpeed: 10,
        tolerance: 'pointer',
        update: drawRoute
    });
}