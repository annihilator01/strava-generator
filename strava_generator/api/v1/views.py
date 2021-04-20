from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from strava.settings import GMAPS_API_TOKEN
from gpxgen import GpxGen
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
    params = request.query_params
    response = {}
    response_status = status.HTTP_200_OK

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
        response, response_status = _get_400_response(str(e))
    else:
        msk_timezone = timezone('Europe/Moscow')
        now_time = datetime.now().timestamp()
        end_time = msk_timezone.localize(end_time).timestamp() if end_time else 0
        if now_time < end_time:
            response, response_status = _get_400_response('Activity end time exceeds now time')
        else:
            try:
                cooked_gpx_generator = service.get_cooked_gpx_generator(
                    origin=origin,
                    destination=destination,
                    waypoints=waypoints,
                    activity_type=activity_type,
                    end_time=end_time
                )
            except IndexError as e:
                response, response_status = _get_400_response(str(e))
            else:
                generated_gpx = cooked_gpx_generator.build()
                response = {
                    'code': 200,
                    'gpx': generated_gpx
                }

    return Response(response, response_status)
