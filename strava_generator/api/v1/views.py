from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from strava.settings import GMAPS_API_TOKEN
from gpxgen import GpxGen
from datetime import datetime


@api_view(['GET'])
def get_generated_strava_gpx(request):
    origin = request.query_params.get('origin')
    destination = request.query_params.get('destination')
    waypoints = request.query_params.get('waypoints')
    activity_type = request.query_params.get('activity_type', 'run')
    start_time = request.query_params.get('start_time')


    return Response({'lol': 'wefwef'})
