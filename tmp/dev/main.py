from pprint import pprint
from gpxgen import GpxGen

import googlemaps
import polyline
import datetime


def main():
    with open('api_token') as token:
        api_token = token.read()

    gmaps = googlemaps.Client(key=api_token)
    now = datetime.datetime.now()

    directions_result = gmaps.directions(
        origin='60.002283970833204,30.299341854763778',
        destination='59.95921270722829,30.40653922132564',
        mode='walking',
        departure_time=now
    )[0]

    overview_points_result = polyline.decode(directions_result['overview_polyline']['points'])

    concat_points_result = []
    for step in directions_result['legs'][0]['steps']:
        concat_points_result += polyline.decode(step['polyline']['points'])

    generator = GpxGen('Yet another generator')
    for coords in concat_points_result:
        point = {'coords': {'lat': coords[0], 'lon': coords[1]}}
        generator.add_point(point)

    result = generator.build()

    with open('tmpfile.gpx', 'wb') as file:
        file.write(result)


if __name__ == '__main__':
    main()
