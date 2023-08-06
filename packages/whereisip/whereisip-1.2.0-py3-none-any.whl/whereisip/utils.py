"""
module with utilities used by whereisip
"""
import logging
from pathlib import Path

import appdirs

from latloncalc import latlon as llc
import country_converter as coco

_logger = logging.getLogger(__name__)


def deg_to_dms(degrees_decimal: float, n_digits_seconds: int = 1):
    """
    Turn a number in decimal to a sexagesimal representation degrees-minutes-seconds

    Args:
        degrees_decimal: float
            Degrees in decimal representation

        n_digits_seconds:
            Number of digits to use for the seconds of the sexagesimal respresentation

    Returns: str
        Sexagesimal representation of the location in degrees-minutes-seconds
    """
    degrees = int(degrees_decimal)
    minutes_decimal = abs(degrees_decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds_decimal = round((minutes_decimal - minutes) * 60, n_digits_seconds)
    dms_coordinates = f"{degrees}° {minutes}' {seconds_decimal}″"
    return dms_coordinates


def make_sexagesimal_location(latitude: float, longitude: float, n_digits_seconds: int = 1):
    """
    Turns the latitude/longitude location into a sexagesimal string

    Args:
        latitude: float
            The latitude in decimal notation
        longitude: float
            The longitude in decimal notation
        n_digits_seconds: int
            Number of digits to use for the seconds of the sexagesimal representation

    Returns: str
        location as a sexagesimal string
    """
    if llc is None:
        lat_dms = deg_to_dms(latitude, n_digits_seconds=n_digits_seconds)
        lon_dms = deg_to_dms(longitude, n_digits_seconds=n_digits_seconds)
        latlon = (lat_dms, lon_dms)
    else:
        latlon = llc.LatLon(lat=latitude, lon=longitude)
        latlon = latlon.to_string(formatter="d%° %m%′ %S%″ %H", n_digits_seconds=n_digits_seconds)

    location = ", ".join(latlon)

    return location


def make_decimal_location(latitude: float, longitude: float, n_decimals: int = 1):
    """
    Turns the latitude/longitude location into a decimal string

    Args:
        latitude: float
            The latitude in decimal notation
        longitude: float
            The longitude in decimal notation
        n_decimals: int
            Number of digits to use for the decimal representation

    Returns: str
        location as a decimal string
    """
    strfrm = "{:." + f"{n_decimals}" + "f}"
    location = ", ".join([strfrm.format(latitude), strfrm.format(longitude)])
    return location


def make_human_location(country_code: str, city: str):
    """
    Turns the country and city strings into a country/city representation

    Args:
        country_code: str
            The country code of the location
        city: str
            The city of the location

    Returns: str
        Either city / country (country_code)  or city /country_code
    """
    if coco is not None:
        country_name = coco.convert(country_code, to="name_short")
        country = country_name + f" ({country_code})"
    else:
        country = country_code
    location = f"{city}/{country}"
    return location


def query_yes_no(message):
    answer = input(f"{message}. Continue? [y/N]")
    if answer == "":
        answer = "n"
    try:
        first_char = answer.lower()[0]
    except AssertionError:
        raise AssertionError("Could not get first character. This should not happen")

    if first_char == "y":
        positive = True
    elif first_char == "n":
        positive = False
    else:
        _logger.warning("Please answer with [y/N] only.")
        positive = query_yes_no(message)

    return positive


def get_cache_file(ipaddress, write_cache=True) -> Path:
    """
    Get the cache file name based on the ip address

    Args:
        ipaddress: str
            Ip address of the cache file
        write_cache: bool
            Write the cache file

    Returns:

        Path object of cache file name

    """

    cache_dir = Path(appdirs.user_cache_dir("whereisip"))

    if write_cache:
        cache_dir.mkdir(exist_ok=True, parents=True)

    if ipaddress is None:
        suffix = "localhost"
    else:
        suffix = ipaddress

    cache_file = cache_dir / Path("_".join(["resp", suffix]) + ".json")
    return cache_file


def get_distance_to_server(geo_info):
    """
    Get the coordinates from the two locations stored in geo_info and calculate the distance

    Args:
        geo_info:  dict
            Dictionary with the locations stored

    Returns:
        The distance in km between the two locations

    """

    latlon_server = llc.LatLon(lat=geo_info["lat"], lon=geo_info["lng"])
    latlon_device = llc.LatLon(lat=geo_info["my_lat"], lon=geo_info["my_lng"])

    return latlon_server.distance(latlon_device)


def geoinfo2location(geo_info) -> dict:
    """
    Extract the relevant location information from the geo_info dictionary

    Args:
        geo_info: dict
            geographics information returnned by geocode

    Returns: dict
        dictionary with relevant location information
    """
    location_human = make_human_location(country_code=geo_info["country"],
                                         city=geo_info["city"])
    location = {"my_location": location_human,
                "my_lat": geo_info["lat"],
                "my_lng": geo_info["lng"]}
    return location
