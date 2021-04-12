import numpy as np

from lxml import etree
from datetime import datetime


class GpxGen:
    def __init__(self, name, *, activity_type=9, start_time=None):
        self.name = name
        self.activity_type = activity_type
        self.start_time = start_time

        self.root = self._build_root()
        self.points = []
        self.activity_points = self.root.find('trk').find('trkseg')

        # constants
        self.route_deviation_scale = 1e-5

    def add_point(self, point):
        intermediate_points = []
        if len(self.points):
            intermediate_points = self._get_intermediate_points(self.points[-1], point)

        for p in [*intermediate_points, point]:
            self.points.append(p)

    def add_points(self, points, noise_mode=True):
        for point in points:
            self.add_point(point)

        if noise_mode:
            self.points = self._make_noisy(self.points, self.route_deviation_scale / 2, self.route_deviation_scale)

    def create_activity_point(self, point):
        point_attrs = {
            'lat': f"{point[0]}",
            'lon': f"{point[1]}"
        }

        trkpt = self.get_element('trkpt', attrib=point_attrs)
        point_time = self.get_element('time', text='2021-03-18T13:39:50Z')
        trkpt.extend([point_time])

        self.activity_points.append(trkpt)

    def create_activity_points(self, points):
        for point in points:
            self.create_activity_point(point)

    def get_element(self, tag, *, attrib=None, nsmap=None, text=None):
        element = etree.Element(tag, attrib=attrib, nsmap=nsmap)
        if text:
            element.text = str(text)

        return element

    def set_start_time(self):
        start_time = self.start_time if self.start_time else datetime.now()
        start_time = datetime.strftime(start_time, '%Y-%m-%dT%H:%M:%SZ')
        start_time_tag = self.root.find('metadata').find('time')
        start_time_tag.text = start_time

    def build(self):
        self.set_start_time()
        self.create_activity_points(self.points)

        return etree.tostring(
            self.root,
            xml_declaration=True,
            encoding='UTF-8',
            # encoding='unicode',
            pretty_print=True,
        )

    def _build_root(self):
        root_nsmap = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }

        root_attrs = {
            f"{{{root_nsmap['xsi']}}}schemaLocation": 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd',
            'version': '1.1',
            'xmlns': 'http://www.topografix.com/GPX/1/1'
        }

        root = self.get_element('gpx', attrib=root_attrs, nsmap=root_nsmap)

        metadata = self.get_element('metadata')
        start_time = self.get_element('time')
        metadata.extend([start_time])

        trk = self.get_element('trk')
        name = self.get_element('name', text=self.name)
        activity_type = self.get_element('type', text=self.activity_type)
        trkseg = self.get_element('trkseg')
        trk.extend([name, activity_type, trkseg])

        root.extend([metadata, trk])

        return root

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
        arr += np.random.normal(center, deviation, arr)
        return arr
