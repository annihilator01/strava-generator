let map;


function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject);
  });
}


async function initMap() {
  let center_coords = new google.maps.LngLat(55.755799012637766, 37.617742567387175);

  getCurrentLocation()
      .then(position => {
        center_coords = new google.maps.LngLat(position.coords.latitude, position.coords.longitude);
      })
      .finally(onFinally => {
        map = new google.maps.Map($('#map')[0], {
          center: LatLng,
          zoom: 17
        });
      })
}