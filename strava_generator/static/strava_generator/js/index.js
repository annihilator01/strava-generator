function addMarker(coords, name) {
    const marker = new google.maps.Marker({
        position: coords,
        map: map,
        draggable: true,
        title: name,
    });

    let $routePoint;

    google.maps.event.addListener(marker, 'rightclick', (e) => {
        if (e.domEvent instanceof MouseEvent || e.domEvent instanceof TouchEvent) {
            const clickEvent = e.domEvent;

            let clientX, clientY;
            switch (true) {
                case clickEvent instanceof MouseEvent:
                    clientX = clickEvent.clientX;
                    clientY = clickEvent.clientY;
                    break;

                case clickEvent instanceof TouchEvent:
                    clientX = clickEvent.changedTouches[0].clientX;
                    clientY = clickEvent.changedTouches[0].clientY;
                    break;
            }

            const left = clientX;
            const top = clientY;

            $markerMenu.css('left', `${left}px`);
            $markerMenu.css('top', `${top}px`);
            $markerMenu.css('display', 'block');

            $markerMenu.find('.add-marker')
                .off('click')
                .click(() => {
                    $routePoint = addRoutePoint(marker);
                });

            $markerMenu.find('.remove-marker')
                .off('click')
                .click(() => {
                    marker.setMap(null);
                    removeRoutePoint($routePoint);
                });

            clickEvent.preventDefault();
        }
    });

    google.maps.event.addListener(marker, 'click', (e) => {
        if (e.domEvent instanceof TouchEvent) {
            google.maps.event.trigger(marker, 'rightclick', e);
        }
    });

    map.setCenter(coords);
}

function removeRoutePoint($routePoint) {
    if (!$routePoint) {
        return;
    }

    const marker = $routePoint.data('marker');
    const coordsString = getCoordsString(marker);

    marker.setMap(null);
    delete routeMarkers[coordsString];
    $routePoint.remove();

    drawRoute();
}


function drawRoute() {
    setMarkersLabels();
    const $locationListChildren = $locationList.children('.list-group-item');

    if ($locationListChildren.length === 0) {
        showNoRoutePointsInfo();
        turnWarning(
            $statusBarInfo,
            '0 km', activity_limit[getCheckedActivity()].warn,
            'totalDistance', 0
        );
        return;
    }

    hideNoRoutePointsInfo();

    let coordsArr = [];
    $locationListChildren.each(function () {
        coordsArr.push(getCoordsString($(this).data('marker')));
    });

    const origin = coordsArr[0];
    const destination = coordsArr[coordsArr.length - 1];

    let waypoints = [];
    if ($locationListChildren.length > 2) {
        const waypointsArr = coordsArr.splice(1, coordsArr.length - 2);
        waypointsArr.forEach((coords) => {
            waypoints.push({
                location: coords,
                stopover: true
            });
        });
    }

    turnSpinner($statusBarInfo);
    $generateGpxButton.prop('disabled', true);

    directionService.route(
        {
            origin: origin,
            destination: destination,
            waypoints: waypoints,
            travelMode: google.maps.TravelMode.WALKING
        },
        (response, status) => {
            if (status === 'OK' && response) {
                processLegs(response.routes[0].legs);
                if ($locationListChildren.length < 2) {
                    clearRouteRenderer();
                    turnWarning(
                        $statusBarInfo,
                        '0 km', activity_limit[getCheckedActivity()].warn,
                        'totalDistance', 0
                    );
                } else {
                    directionsRenderer.setDirections(response);
                    $generateGpxButton.prop('disabled', false);
                }
            } else {
                clearRouteRenderer();
                turnDanger(
                    $statusBarInfo,
                    'N/A', `Route cannot be built with this set of markers`,
                    'totalDistance', 0
                );
            }
        }
    );
}

$noRoutePointsInfo = $('#no-route-points-info');
function hideNoRoutePointsInfo() {
    $noRoutePointsInfo.removeClass('d-lg-flex');
}

function showNoRoutePointsInfo() {
    $noRoutePointsInfo.addClass('d-lg-flex');
}

function processLegs(legs) {
    let totalDistance = 0;
    const $locationListChildren = $locationList.children('.list-group-item');
    $locationListChildren.each(function (i) {
        const marker = $(this).data('marker');

        let addressHtml;
        if (i < legs.length) {
            addressHtml = `${legs[i].start_address}`
            setTextInfo(
                $(this).find('.location-name'),
                `&nbsp; ${addressHtml}`,
                addressHtml
            );

            marker.setTitle(legs[i].start_address);
            marker.setPosition(new google.maps.LatLng(
                legs[i].start_location.lat(),
                legs[i].start_location.lng()
            ));
            totalDistance += legs[i].distance.value;
        } else {
            addressHtml = `${legs[i - 1].end_address}`;
            setTextInfo(
                $(this).find('.location-name'),
                `&nbsp; ${addressHtml}`,
                addressHtml
            );

            marker.setTitle(legs[i - 1].end_address);
            marker.setPosition(new google.maps.LatLng(
                legs[i - 1].end_location.lat(),
                legs[i - 1].end_location.lng()
            ));
        }
    });


    const totalDistanceString = `${Number(totalDistance / 1000).toFixed(2)} km`;
    const checkedActivity = getCheckedActivity();
    if (totalDistance < activity_limit[checkedActivity].val) {
        turnWarning(
            $statusBarInfo,
            totalDistanceString, activity_limit[checkedActivity].warn,
            'totalDistance', totalDistance
        );
    } else {
        turnSuccess(
            $statusBarInfo,
            totalDistanceString, '',
            'totalDistance', totalDistance
        );
    }
}

function addRoutePoint(marker) {
    if ($locationList.length === MAX_ROUTE_POINTS_NUM) {
        return null;
    }

    const $locationListChildren = $locationList.children('.list-group-item');

    if (marker.label) {
        let $existedRoutePoint = null;
        $locationListChildren.each(function () {
            if ($(this).data('marker') === marker) {
                $existedRoutePoint = $(this);
            }
        });
        return $existedRoutePoint;
    }

    const coordsString = getCoordsString(marker);
    if (!routeMarkers[coordsString]) {
        routeMarkers[coordsString] = marker;
    } else {
        return routeMarkers[coordsString];
    }


    const name = marker.title;
    const $routePoint = getRoutePoint(name);
    $routePoint.data('marker', marker);
    $routePoint.click(() => {
        map.setCenter(getCoordsObject(marker));
        map.setZoom(DEFAULT_MAP_ZOOM);
    });

    if ($locationListChildren.length < 2) {
        $locationList.append($routePoint);
    } else {
        $locationList.children(':last-child').before($routePoint);
    }

    google.maps.event.addListener(marker, 'dragend', drawRoute);
    drawRoute();

    return $routePoint;
}

function getRoutePoint(name) {
    const $routePoint = $('<li/>', {
        class: 'list-group-item d-flex align-items-center'
    }).append(
        $('<i/>', {
            class: 'drag-item fas fa-bars fa-sm mr-2',
            'aria-hidden': 'true',
        })
    ).append(
        $('<span/>', {
            class: 'circle',
        }).append(
            $('<strong/>', {
                class: 'location-label alph user-select-none'
            })
        )
    ).append(
        $('<p/>', {
            class: 'location-name m-0 mr-3 user-select-none text-truncate',
            title: name,
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

function setMarkersLabels() {
    const $locationListChildren = $locationList.children('.list-group-item');
    $locationListChildren.each(function (i) {
        const marker = $(this).data('marker');

        const label = {
            color: 'white',
            fontWeight: 'bold',
            text: LABELS[i]
        };

        $(this).find('.location-label').text(label.text);
        marker.setLabel(label);
    });
}

function getCoordsString(marker) {
    return `${marker.position.lat()},${marker.position.lng()}`
}

function getCoordsObject(marker) {
    return new google.maps.LatLng(
        marker.position.lat(),
        marker.position.lng()
    );
}

function clearRouteRenderer() {
    directionsRenderer.setDirections({routes: []});
}

function turnSuccess($el, text, title, dataKey, dataValue) {
    $el.removeClass('badge-warning badge-danger badge-info');
    $el.addClass('badge-success');
    setData($el, dataKey, dataValue);
    setTextInfo($el, text, title);
}

function turnWarning($el, text, title, dataKey, dataValue) {
    $el.removeClass('badge-success badge-danger badge-info');
    $el.addClass('badge-warning');
    setData($el, dataKey, dataValue);
    setTextInfo($el, text, title);
}

function turnDanger($el, text, title, dataKey, dataValue) {
    $el.removeClass('badge-success badge-warning badge-info');
    $el.addClass('badge-danger');
    setData($el, dataKey, dataValue);
    setTextInfo($el, text, title);
}

function turnSpinner($el) {
    $el.removeClass('badge-success badge-warning badge-danger');
    $el.addClass('badge-info');
    setData($el, null, null);
    setTextInfo($el, getStatusBarSpinner(), 'Loading...');
}

function setTextInfo($el, text, title) {
    if (text !== null) {
        $el.html(text);
    }

    if (title !== null) {
        $el.prop('title', title);
    }
}

function setData($el, dataKey, dataValue) {
    if (dataKey !== null) {
        $el.data(dataKey, dataValue);
    }
}

function getStatusBarSpinner() {
    return '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
}