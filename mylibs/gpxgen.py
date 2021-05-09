import numpy as np
import haversine as hs

from lxml import etree
from datetime import datetime
from pytz import timezone


class GpxGen:
    def __init__(self, *, activity_type='run', end_time=None):
        self.end_time = end_time

        self.root = self._build_root()
        self.points = []
        self.time_info = []
        self.activity_points = self.root.find('trk').find('trkseg')

        # constants
        self.eps = 1e-10
        self.route_deviation_scale = 1e-5
        self.min_sin_deviation = 0.05
        self.max_sin_deviation = 0.5
        self.default_max_chunk_size = 0.025
        self.timezone = timezone('Europe/Moscow')

        if activity_type == 'run':
            self.min_pace = 3
            self.max_pace = 8
        elif activity_type == 'bike':
            self.min_pace = 2
            self.max_pace = 6

    def add_point(self, point):
        intermediate_points = []
        if len(self.points):
            intermediate_points = self._get_intermediate_points(self.points[-1], point)

        for p in [*intermediate_points, point]:
            self.points.append(p)

    def add_points(self, points):
        for point in points:
            self.add_point(point)
        self.points = self._make_noisy(self.points, self.route_deviation_scale / 2, self.route_deviation_scale)

    def _set_end_time(self):
        if not self.end_time:
            self.end_time = datetime.now(self.timezone)
        else:
            if self.end_time.tzinfo:
                self.end_time = self.end_time.astimezone(self.timezone)
            else:
                self.end_time = self.timezone.localize(self.end_time)

    def build(self):
        self._set_end_time()
        self._create_activity_points(self.points)
        self._create_points_time_info()

        start_time_tag = self.root.find('metadata').find('time')
        start_time_tag.text = self.activity_points[0].find('time').text

        return etree.tostring(
            self.root,
            xml_declaration=True,
            encoding='UTF-8',
            pretty_print=True,
        )

    def _get_element(self, tag, *, attrib=None, nsmap=None, text=None):
        element = etree.Element(tag, attrib=attrib, nsmap=nsmap)
        if text:
            element.text = str(text)

        return element

    def _build_root(self):
        root_nsmap = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }

        root_attrs = {
            f"{{{root_nsmap['xsi']}}}schemaLocation": 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd',
            'version': '1.1',
            'xmlns': 'http://www.topografix.com/GPX/1/1'
        }

        root = self._get_element('gpx', attrib=root_attrs, nsmap=root_nsmap)

        metadata = self._get_element('metadata')
        start_time = self._get_element('time')
        metadata.extend([start_time])

        trk = self._get_element('trk')
        trkseg = self._get_element('trkseg')
        trk.extend([trkseg])

        root.extend([metadata, trk])

        return root

    def _create_activity_point(self, point):
        point_attrs = {
            'lat': f"{point[0]}",
            'lon': f"{point[1]}"
        }

        trkpt = self._get_element('trkpt', attrib=point_attrs)
        self.activity_points.append(trkpt)

    def _create_activity_points(self, points):
        for point in points:
            self._create_activity_point(point)

    def _get_intermediate_points(self, point_1, point_2, inter_num=4):
        intermediate_points = []
        lat_step = (point_2[0] - point_1[0]) / (inter_num + 1)
        lon_step = (point_2[1] - point_1[1]) / (inter_num + 1)

        current = point_1
        for i in range(inter_num):
            current = (current[0] + lat_step, current[1] + lon_step)
            intermediate_points.append(current)

        return intermediate_points

    def _make_noisy(self, arr, center, deviation):
        arr = np.array(arr)
        arr += np.random.normal(center, deviation, arr.shape)
        return arr.tolist()

    def _make_noisy_by_chunks(self, points):
        nosed_points = []
        last_seen_index = 0
        for chunk_points_count in self._get_points_count_by_chunks():
            chunk_points = points[last_seen_index:last_seen_index + chunk_points_count]
            chunk_deviation = np.random.uniform(self.min_sin_deviation, self.max_sin_deviation)
            noised_chunk_points = self._make_noisy(chunk_points, 0, chunk_deviation)

            nosed_points.extend(noised_chunk_points)
            last_seen_index += chunk_points_count

        return nosed_points

    def _create_points_time_info(self):
        sin_points = self._get_sin_points()
        noisy_sin_points = self._make_noisy_by_chunks(sin_points)
        result_sin_points = self._get_fit_to_range_points(noisy_sin_points)
        self._form_time_info(result_sin_points)

        time_for_curr_point = self.end_time
        for i in reversed(range(len(self.activity_points))):
            utc_time_for_curr_point = time_for_curr_point.astimezone(timezone('UTC'))
            point_time = self._get_element(
                'time',
                text=f"{utc_time_for_curr_point.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            )
            self.activity_points[i].extend([point_time])

            time_for_curr_point = datetime.fromtimestamp(
                time_for_curr_point.timestamp() - self.time_info[i],
                tz=self.timezone
            )

    def _get_sin_points(self):
        sin_points = []
        for chunk_points_count in self._get_points_count_by_chunks():
            sin_type = np.random.choice([-1, 1])
            if sin_type == -1:
                left_border = np.random.uniform(-np.pi, 0)
                right_border = np.random.uniform(left_border, 0)
            elif sin_type == 1:
                left_border = np.random.uniform(0, np.pi)
                right_border = np.random.uniform(left_border, np.pi)

            numbers_in_borders = np.linspace(left_border, right_border, chunk_points_count)
            for number_in_borders in numbers_in_borders:
                sin_value = np.sin(number_in_borders)
                sin_points.append(sin_value)

        return sin_points

    def _get_fit_to_range_points(self, sin_points):
        fit_to_range_points = []
        last_seen_index = 0
        for chunk_points_count in self._get_points_count_by_chunks():
            chunk_points = sin_points[last_seen_index:last_seen_index + chunk_points_count]
            low_pace = np.random.uniform(self.min_pace, self.max_pace)
            high_pace = np.random.uniform(low_pace, self.max_pace)
            fit_to_range_chunk_points = np.interp(
                chunk_points,
                (max(chunk_points), min(chunk_points)),
                (low_pace, high_pace)
            ).tolist()

            fit_to_range_points.extend(fit_to_range_chunk_points)
            last_seen_index += chunk_points_count

        return fit_to_range_points

    def _get_points_count_by_chunks(self):
        points_count_by_chunks = []
        points_left = points_count = len(self.points)

        while points_left != 0:
            chunk_size = np.random.uniform(self.eps, self.default_max_chunk_size)
            chunk_points_count = max(int(points_count * chunk_size), 1)
            chunk_points_count = chunk_points_count if chunk_points_count < points_left else points_left
            points_count_by_chunks.append(chunk_points_count)
            points_left -= chunk_points_count

        return points_count_by_chunks

    def _form_time_info(self, pace_values):  # pace values in min/km format
        self.time_info = [0]
        for i in range(len(pace_values) - 1):
            loc1 = self.points[i]
            loc2 = self.points[i + 1]
            distance = hs.haversine(loc1, loc2)
            time_for_distance = distance * (pace_values[i] * 60)  # time_for_distance is in seconds format
            self.time_info.append(time_for_distance)
