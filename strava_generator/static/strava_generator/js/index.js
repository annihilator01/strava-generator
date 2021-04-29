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

                mouseEvent.preventDefault();
            }
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

    if ($locationListChildren.length < 2) {
        directionsRenderer.setDirections({routes: []});
        return;
    }

    let coordsArr = [];
    $locationListChildren.each(function() {
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

    directionService.route(
        {
            origin: origin,
            destination: destination,
            waypoints: waypoints,
            travelMode: google.maps.TravelMode.WALKING
        },
        (response, status) => {
            if (status === 'OK' && response) {
                directionsRenderer.setDirections(response);
                setNewNamesAndPositionsToMarker(response.routes[0].legs);
            }
        }
    );
}

function setNewNamesAndPositionsToMarker(legs) {
    const $locationListChildren = $locationList.children('.list-group-item');
    $locationListChildren.each(function(i) {
        const marker = $(this).data('marker');

        if (i < legs.length) {
            $(this).find('.location-name').html = `&nbsp; ${legs[i].start_address}`;
            marker.setTitle(legs[i].start_address);
            marker.setPosition(new google.maps.LatLng(
                legs[i].start_location.lat(),
                legs[i].start_location.lng()
            ));
        } else {
            $(this).find('.location-name').html = `&nbsp; ${legs[i - 1].end_address}`;
            marker.setTitle(legs[i - 1].end_address);
            marker.setPosition(new google.maps.LatLng(
                legs[i - 1].end_location.lat(),
                legs[i - 1].end_location.lng()
            ));
        }
    });
}

function addRoutePoint(marker) {
    if ($locationList.length === MAX_ROUTE_POINTS_NUM) {
        return null;
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
    $routePoint.click(() => map.setCenter(getCoordsObject(marker)));

    if ($locationList.find('.list-group-item').length < 2) {
        $locationList.append($routePoint);
    } else {
        $locationList.find(' > .list-group-item:last-child').before($routePoint);
    }

    drawRoute();
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
        $('<span/>', {
            class: 'location-label fa-stack ml-2'
        }).append(
            $('<i/>', {
                class: 'far fa-circle fa-stack-2x',
            })
        ).append(
            $('<strong/>', {
                class: 'fa-stack-1x'
            })
        )
    ).append(
        $('<p/>', {
            class: 'location-name m-0 mr-3 no-select text-truncate',
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
            fontWeight: 'white',
            text: LABELS[i]
        };

        $(this).find('.location-label > strong').text(label.text);
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
