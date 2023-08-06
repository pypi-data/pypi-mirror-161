import unittest

from whereisip.getgeolocation import IpErrorNoLocationFound
from whereisip.getgeolocation import (get_geo_location_ip)

__author__ = "Eelco van Vliet"
__copyright__ = "Eelco van Vliet"
__license__ = "MIT"


class TestGetGeoLocation(unittest.TestCase):
    geo_info = get_geo_location_ip("8.8.8.8", write_cache=False, reset_cache=True)
    expected = {'address': 'Mountain View, California, US',
                'city': 'Mountain View',
                'country': 'US',
                'hostname': 'dns.google',
                'ip': '8.8.8.8',
                'lat': 37.4056,
                'lng': -122.0775,
                'ok': True,
                'org': 'AS15169 Google LLC',
                'postal': '94043',
                'raw': {'ip': '8.8.8.8',
                        'hostname': 'dns.google',
                        'anycast': True,
                        'city': 'Mountain View',
                        'region': 'California',
                        'country': 'US',
                        'loc': '37.4056,-122.0775',
                        'org': 'AS15169 Google LLC',
                        'postal': '94043',
                        'timezone': 'America/Los_Angeles',
                        'readme': 'https://ipinfo.io/missingauth'},
                'state': 'California',
                'status': 'OK'
                }

    def test_geo_location_equal(self):
        self.assertDictEqual(self.geo_info, self.expected)


class TestGetGeoLocationException(unittest.TestCase):
    def test_geo_location_exception(self):
        with self.assertRaises(IpErrorNoLocationFound):
            geo_info = get_geo_location_ip("10.2.30.11", write_cache=False, reset_cache=True)
