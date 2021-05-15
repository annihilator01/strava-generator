from django.db import transaction, DatabaseError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import ParseError

from datetime import datetime
from pytz import timezone
from ... import service


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['code'] = response.status_code
        response.data['error'] = response.data.pop('detail')

    return response


@api_view(['GET'])
@service.user_active_status_required(isApi=True)
@service.active_usage_token_required(isApi=True)
def get_generated_strava_gpx(request):
    user = request.user
    service.register_action(request)

    params = request.query_params
    try:
        origin = service.get_coordinates(service.get_required(params, 'origin'))
        destination = service.get_coordinates(service.get_required(params, 'destination'))
        waypoints = service.get_coordinates_list(params.get('waypoints', ''))
        activity_type = service.validate_activity_type(params.get('activity_type', ''))
        end_time = service.get_datetime_from_string(params.get('end_time', ''))
    except (
            service.IncorrectCoordinatesFormatException,
            service.IncorrectActivityTypeException,
            ValueError
    ) as e:
        raise ParseError(detail=str(e))

    if end_time:
        msk_timezone = timezone('Europe/Moscow')
        now_time = datetime.now(msk_timezone)
        end_time = msk_timezone.localize(end_time)
        if now_time.timestamp() < end_time.timestamp():
            string_now_time = service.get_string_from_datetime(now_time)
            string_end_time = service.get_string_from_datetime(end_time)
            raise ParseError(detail=f'Activity end time &#171;{string_end_time}&#187; exceeds '
                                    f'now time &#171;{string_now_time}&#187;')

    try:
        cooked_gpx_generator = service.get_cooked_gpx_generator(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
            activity_type=activity_type,
            end_time=end_time
        )
    except Exception as e:
        raise ParseError(detail=str(e))

    generated_gpx = cooked_gpx_generator['generator'].build()

    try:
        with transaction.atomic():
            service.register_generate_gpx_action_info(
                user=user,
                from_location=cooked_gpx_generator['from_location'],
                to_location=cooked_gpx_generator['to_location'],
                activity_type=activity_type,
                distance=cooked_gpx_generator['distance'],
                end_time=end_time,
                gpx=generated_gpx,
            )
            service.use_usage_token(user)
    except DatabaseError:
        raise ParseError(detail='Something went wrong. Try again')

    response = {
        'code': 200,
        'gpx': generated_gpx,
        'uses_left': user.active_usage_token.uses_left if user.active_usage_token else 0,
    }

    return Response(response)
