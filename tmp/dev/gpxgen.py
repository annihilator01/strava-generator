from lxml import etree
from datetime import datetime


class GpxGen:
    def __init__(self, name, *, activity_type=9, start_time=None):
        self.name = name
        self.activity_type = activity_type
        self.start_time = start_time

        self.root = self._build_root()
        self.points = self.root.find('trk').find('trkseg')

    def add_point(self, point):
        point_attrs = {
            'lat': f"{point['coords']['lat']}",
            'lon': f"{point['coords']['lon']}"
        }

        trkpt = self.get_element('trkpt', attrib=point_attrs)
        point_time = self.get_element('time', text='2021-02-18T13:39:50Z')
        trkpt.extend([point_time])

        self.points.append(trkpt)

    def add_points(self, points):
        for point in points:
            self.add_point(point)

    def get_element(self, tag, *, attrib=None, nsmap=None, text=None):
        element = etree.Element(tag, attrib=attrib, nsmap=nsmap)
        if text:
            element.text = str(text)

        return element

    def build(self):
        start_time = self.start_time if self.start_time else datetime.now()
        start_time = datetime.strftime(start_time, '%Y-%m-%dT%H:%M:%SZ')
        start_time_tag = self.root.find('metadata').find('time')
        start_time_tag.text = start_time

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

    def _populate_with_intermediate_points(self, points):
        pass