import os
import googlemaps
import polyline

from datetime import datetime
from django.utils.datastructures import MultiValueDictKeyError
from strava.settings import GMAPS_API_TOKEN
from mylibs.gpxgen import GpxGen
from .models import Visitor, Visit, Action


# constants
MAX_TOTAL_DISTANCE = 50000


class TooLongDistanceException(Exception):
    def __init__(self, msg):
        super(TooLongDistanceException, self).__init__(msg)


class IncorrectCoordinatesFormatException(Exception):
    def __init__(self, msg):
        super(IncorrectCoordinatesFormatException, self).__init__(msg)


class IncorrectActivityTypeException(Exception):
    def __init__(self, msg):
        super(IncorrectActivityTypeException, self).__init__(msg)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_required(params, key):
    try:
        return params[key]
    except MultiValueDictKeyError:
        raise ValueError(f'Parameter {key} is required')


def get_coordinates(string_coords):
    string_coords = string_coords.strip()

    if not string_coords:
        return []

    coords = string_coords.split(',')

    try:
        coords = [float(coords[0]), float(coords[1])]
    except (IndexError, ValueError):
        raise IncorrectCoordinatesFormatException(f'Incorrect coordinates format: {string_coords}')

    return coords


def get_coordinates_list(string_coords_list):
    string_coords_list = string_coords_list.strip()

    if not string_coords_list:
        return []

    coords_list = string_coords_list.split('|')
    for i in range(len(coords_list)):
        try:
            coords_list[i] = get_coordinates(coords_list[i])
        except IncorrectCoordinatesFormatException:
            raise IncorrectCoordinatesFormatException(f'Incorrect coordinates format: {string_coords_list}')

    return coords_list


def get_string_from_datetime(datetime_obj):
    if not datetime_obj:
        return None
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')


def get_datetime_from_string(string_datetime):
    string_datetime = string_datetime.strip()

    if not string_datetime:
        return None

    try:
        return datetime.strptime(string_datetime, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        raise ValueError(f'Incorrect time format: {string_datetime}')


def get_cooked_gpx_generator(origin, destination, waypoints, activity_type, end_time):
    gmaps = googlemaps.Client(key=GMAPS_API_TOKEN)

    try:
        directions_result = gmaps.directions(
            origin=origin,
            waypoints=waypoints,
            destination=destination,
            mode='walking'
        )[0]
    except Exception:
        raise Exception('Impossible route')

    all_points_coords = []
    total_distance = 0
    for leg in directions_result['legs']:
        total_distance += leg['distance']['value']
        for step in leg['steps']:
            all_points_coords += polyline.decode(step['polyline']['points'])

    if total_distance > MAX_TOTAL_DISTANCE:
        raise TooLongDistanceException(f'Distance cannot be more than {round(MAX_TOTAL_DISTANCE / 1000, 2)} km, '
                                       f'current distance: {round(total_distance / 1000, 2)} km')

    generator = GpxGen(activity_type=activity_type, end_time=end_time)
    points = []
    for coords in all_points_coords:
        points.append(coords)
    generator.add_points(points)

    return generator


def validate_activity_type(activity_type):
    activity_type = activity_type.strip().lower()

    if not activity_type:
        activity_type = 'run'

    if activity_type not in ['run', 'bike']:
        raise IncorrectActivityTypeException(f'Incorrect activity type: {activity_type}')
    return activity_type


def register_visitor(request):
    visitor_ip = get_client_ip(request)
    visitor = Visitor.objects.get_or_create(ip=visitor_ip)[0]
    return visitor


def register_visit(request):
    visitor = register_visitor(request)
    user_agent = request.META.get('HTTP_USER_AGENT')

    visit = Visit.objects.create(
        visitor=visitor,
        user_agent=user_agent,
    )

    return visit


def register_action(request):
    visitor = register_visitor(request)
    action_url = request.get_full_path()
    user_agent = request.META.get('HTTP_USER_AGENT')

    action = Action.objects.create(
        visitor=visitor,
        action_url=action_url,
        user_agent=user_agent,
    )

    return action
