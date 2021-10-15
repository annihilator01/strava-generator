import logging
import googlemaps
import polyline

from datetime import datetime

from django.contrib.auth import logout
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

from strava.settings import GMAPS_API_TOKEN
from mylibs.gpxgen import GpxGen
from .models import (
    Visit,
    Visitor,
    CustomUser,
    UsageToken,
    Action,
    GpxGenerationHistory,
)


logger = logging.getLogger('django')


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
    except Exception as e:
        logger.exception(e)
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

    from_location = directions_result['legs'][0]['start_address']
    to_location = directions_result['legs'][-1]['end_address']

    return {
        'generator': generator,
        'distance': total_distance,
        'from_location': from_location,
        'to_location': to_location,
    }


def validate_activity_type(activity_type):
    activity_type = activity_type.strip().lower()

    if not activity_type:
        activity_type = 'run'

    if activity_type not in ['run', 'bike']:
        raise IncorrectActivityTypeException(f'Incorrect activity type: {activity_type}')
    return activity_type


def validate_username(username):
    if not username:
        raise ValidationError('Username is not provided')

    if len(username) < 6:
        raise ValidationError('Username length must be at least 6 characters')

    if len(username) > 128:
        raise ValidationError('Username length cannot be more than 128 characters')

    user_exists = CustomUser.objects.filter(username=username).exists()
    if user_exists:
        raise ValidationError(f'User with username \'{username}\' already exists')

    try:
        CustomUser.username_validator(username)
    except ValidationError as ve:
        raise ValidationError(ve.args[0].rstrip('.'))


def validate_password(password):
    if not password:
        raise ValidationError('Password is not provided')

    if len(password) < 6:
        raise ValidationError('Password length must be at least 6 characters')

    if len(password) > 128:
        raise ValidationError('Password length cannot be more than 128 characters')


def validate_password_confirm(password_confirm, password):
    if not password_confirm:
        raise ValidationError('Confirm password is not provided')

    if password_confirm != password:
        raise ValidationError('Confirm password doesn\'t match with password')


def validate_usage_token(usage_token):
    if not usage_token:
        raise ValidationError('Usage token is not provided')

    try:
        usage_token = UsageToken.objects.get(value=usage_token)
    except UsageToken.DoesNotExist:
        raise ValidationError('Usage token doesn\'t exist')

    if usage_token.status == UsageToken.UsageTokenStatus.INUSE:
        raise ValidationError('Usage token is already in use now')
    elif usage_token.status == UsageToken.UsageTokenStatus.INACTIVE:
        raise ValidationError('Usage token is inactive')


def user_active_status_required(_func=None, *, isApi=False):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user is not None:
                if user.status != CustomUser.CustomUserStatus.ACTIVE:
                    if isApi:
                        raise PermissionDenied(detail='Your account doesn\'t have permission to use this service')
                    else:
                        logout(request)
                        request.session['signin_info'] = {
                            'error_info': 'Your account doesn\'t have permission to use this service',
                        }

                    return redirect('/signin')
            return func(request, *args, **kwargs)
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def handle_signin_info(func):
    def wrapper(request, *args, **kwargs):
        signin_info = request.session.pop('signin_info', None)
        if signin_info is not None:
            if signin_info.get('error_info') is not None:
                return render(request, 'strava_generator/registration/signin.html',
                              {'error_info': signin_info['error_info']})
        return func(request, *args, **kwargs)
    return wrapper


def active_usage_token_required(_func=None, *, isApi=False):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user is not None:
                active_usage_token = user.active_usage_token
                if not active_usage_token or active_usage_token.status == UsageToken.UsageTokenStatus.INACTIVE:
                    if isApi:
                        raise PermissionDenied(detail='Your usage token has expired. Provide new one')
                    else:
                        return redirect('/update-usage-token')
            return func(request, *args, **kwargs)
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


@transaction.atomic
def register_user(username, password, usage_token):
    usage_token = UsageToken.objects.get(value=usage_token)
    user = CustomUser.objects.create_user(
        username=username,
        password=password,
        active_usage_token=usage_token
    )
    return user


@transaction.atomic
def update_usage_token(user, new_active_usage_token):
    usage_token = UsageToken.objects.get(value=new_active_usage_token)
    user.active_usage_token = usage_token
    user.save()
    return user


@transaction.atomic
def use_usage_token(user, use_num=1):
    usage_token = user.active_usage_token
    usage_token.uses_left -= use_num
    user.total_uses_num += 1

    usage_token.save()
    user.save()


def register_visit(request):
    visitor = register_visitor(request)
    user_agent = request.META.get('HTTP_USER_AGENT')

    visit = Visit.objects.create(
        visitor=visitor,
        user_agent=user_agent,
    )

    return visit


def register_visitor(request):
    visitor_ip = get_client_ip(request)
    visitor = Visitor.objects.get_or_create(ip=visitor_ip)[0]
    return visitor


def register_action(request):
    user = request.user
    action_url = request.get_full_path()
    user_agent = request.META.get('HTTP_USER_AGENT')

    action = Action.objects.create(
        user=user,
        action_url=action_url,
        user_agent=user_agent,
    )

    return action


@transaction.atomic
def register_generate_gpx_action_info(
        user,
        from_location,
        to_location,
        activity_type,
        distance,
        end_time,
        gpx,
):
    gpx_generation_history_record = GpxGenerationHistory.objects.create(
        user=user,
        from_location=from_location,
        to_location=to_location,
        activity_type=activity_type,
        distance=distance,
        end_time=end_time,
        gpx=gpx,
    )

    return gpx_generation_history_record
