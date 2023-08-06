import pytest

from whereisip.utils import (deg_to_dms, get_distance_to_server, get_cache_file,
                             make_human_location, make_decimal_location, make_sexagesimal_location)

__author__ = "eelco"
__copyright__ = "eelco"
__license__ = "MIT"


def test_deg_to_dms():
    """ test deg_to_dms function """
    assert deg_to_dms(36) == "36° 0' 0″"
    assert deg_to_dms(4.5) == "4° 30' 0.0″"
    assert deg_to_dms(-84.95) == "-84° 57' 0.0″"


def test_make_sexagesimal_location():
    """test location funtions """

    assert make_sexagesimal_location(latitude=54.2,
                                     longitude=4.4) == "54° 12′ 0.0″ N, 4° 24′ 0.0″ E"

    assert make_sexagesimal_location(latitude=37.41,
                                     longitude=-122.08) == "37° 24′ 36.0″ N, 122° 4′ 48.0″ W"


def test_make_decimal_location():
    """test location funtions """
    assert make_decimal_location(latitude=4.4, longitude=94.1) == "4.4, 94.1"
    assert make_decimal_location(latitude=37.41,
                                 longitude=-122.08) == "37.4, -122.1"


def test_make_human_location():
    """test location funtions """

    assert make_human_location(country_code="NL", city="Amsterdam") == "Amsterdam/Netherlands (NL)"
    assert make_human_location(country_code="US",
                               city="Mountain View") == "Mountain View/United States (US)"
