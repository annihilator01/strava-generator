from pprint import pprint
from gpxgen import GpxGen
from datetime import datetime

import googlemaps
import polyline


def main():
    with open('api_token') as token:
        api_token = token.read()

    gmaps = googlemaps.Client(key=api_token)
    now = datetime.now()

    directions_result = gmaps.directions(
        origin='59.98560246938819, 30.30091891500659',
        waypoints=['59.9709480037374, 30.274053896371452', '59.96179774500544, 30.279632890814575'],
        destination='59.95623821581812, 30.31035283478617',
        mode='walking',
        # departure_time=now
    )[0]

    import json
    with open('tmp.json', 'w') as f:
        f.write(json.dumps(directions_result))

    all_points_coords = []
    for leg in directions_result['legs']:
        for step in leg['steps']:
            all_points_coords += polyline.decode(step['polyline']['points'])

    generator = GpxGen(start_time=datetime(2021, 4, 13, 14, 22, 39))
    points = []
    for coords in all_points_coords:
        points.append(coords)

    generator.add_points(points)
    result = generator.build()

    with open('tmpfile.gpx', 'wb') as file:
        file.write(result)


if __name__ == '__main__':
    main()
