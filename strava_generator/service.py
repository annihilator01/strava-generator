import os
import googlemaps
import polyline

from datetime import datetime
from django.utils.datastructures import MultiValueDictKeyError
from mylibs.gpxgen import GpxGen


class IncorrectCoordinatesFormatException(Exception):
    def __init__(self, msg):
        super(IncorrectCoordinatesFormatException, self).__init__(msg)


class IncorrectActivityTypeException(Exception):
    def __init__(self, msg):
        super(IncorrectActivityTypeException, self).__init__(msg)


def get_required(params, key):
    try:
        return params[key]
    except MultiValueDictKeyError:
        raise ValueError(f'Parameter {key} is required')


def get_coordinates(string_coords):
    if not string_coords:
        return []

    coords = string_coords.split(',')

    try:
        coords = [float(coords[0]), float(coords[1])]
    except (IndexError, ValueError):
        raise IncorrectCoordinatesFormatException(f'Incorrect coordinates format: {string_coords}')

    return coords


def get_coordinates_list(string_coords_list):
    if not string_coords_list:
        return []

    coords_list = string_coords_list.split('|')
    for i in range(len(coords_list)):
        try:
            coords_list[i] = get_coordinates(coords_list[i])
        except IncorrectCoordinatesFormatException:
            raise IncorrectCoordinatesFormatException(f'Incorrect coordinates format: {string_coords_list}')

    return coords_list


def get_datetime_from_string(string_datetime):
    if not string_datetime:
        return None

    try:
        return datetime.strptime(string_datetime, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        raise ValueError(f'Incorrect time format: {string_datetime}')


def get_cooked_gpx_generator(origin, destination, waypoints, activity_type, end_time):
    gmaps = googlemaps.Client(key=os.environ['GMAPS_API_TOKEN'])

    try:
        directions_result = gmaps.directions(
            origin=origin,
            waypoints=waypoints,
            destination=destination,
            mode='walking'
        )[0]
    except IndexError:
        raise IndexError('Wrong coordinates')

    all_points_coords = []
    for leg in directions_result['legs']:
        for step in leg['steps']:
            all_points_coords += polyline.decode(step['polyline']['points'])

    generator = GpxGen(activity_type=activity_type, end_time=end_time)
    points = []
    for coords in all_points_coords:
        points.append(coords)
    generator.add_points(points)

    return generator


def validate_activity_type(activity_type):
    if activity_type not in ['run', 'bike']:
        raise IncorrectActivityTypeException(f'Incorrect activity type: {activity_type}')
    return activity_type
