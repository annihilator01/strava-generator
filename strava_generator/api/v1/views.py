from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from pytz import timezone
from ... import service


def _get_400_response(msg):
    response = {
        'code': 400,
        'error': msg
    }
    response_status = status.HTTP_400_BAD_REQUEST
    return response, response_status


@api_view(['GET'])
def get_generated_strava_gpx(request):
    service.register_action(request)

    params = request.query_params
    try:
        origin = service.get_coordinates(service.get_required(params, 'origin'))
        destination = service.get_coordinates(service.get_required(params, 'destination'))
        waypoints = service.get_coordinates_list(params.get('waypoints'))
        activity_type = service.validate_activity_type(params.get('activity_type', 'run'))
        end_time = service.get_datetime_from_string(params.get('end_time'))
    except (
            service.IncorrectCoordinatesFormatException,
            service.IncorrectActivityTypeException,
            ValueError
    ) as e:
        return Response(*_get_400_response(str(e)))

    if end_time:
        msk_timezone = timezone('Europe/Moscow')
        now_time = datetime.now(msk_timezone)
        end_time = msk_timezone.localize(end_time)
        if now_time.timestamp() < end_time.timestamp():
            string_now_time = service.get_string_from_datetime(now_time)
            string_end_time = service.get_string_from_datetime(end_time)
            return Response(
                *_get_400_response(f'Activity end time ({string_end_time}) exceeds '
                                   f'now time ({string_now_time})')
            )

    try:
        cooked_gpx_generator = service.get_cooked_gpx_generator(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
            activity_type=activity_type,
            end_time=end_time
        )
    except Exception as e:
        return Response(*_get_400_response(str(e)))

    generated_gpx = cooked_gpx_generator.build()
    response = {
        'code': 200,
        'gpx': generated_gpx
    }

    return Response(response)
