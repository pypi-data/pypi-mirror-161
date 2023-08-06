"""
This script gets the location of the current server
"""

import argparse
import json
import logging
import pprint
import sys

import geocoder

from whereisip import __version__
from whereisip.utils import (make_sexagesimal_location,
                             make_decimal_location,
                             make_human_location,
                             get_cache_file,
                             get_distance_to_server,
                             geoinfo2location)

__author__ = "Eelco van Vliet"
__copyright__ = "Eelco van Vliet"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

OUTPUT_FORMATS = {"raw", "human", "decimal", "sexagesimal", "full", "short"}


class IpErrorNoLocationFound(Exception):
    pass


class LocationReport:
    """
    Object to report the location of the server

    Args:
        geo_info: dict
            Output of geocoder
        n_digits_seconds: int
            Number of digits to use for the seconds in the d-m-s notation of the location
    """

    def __init__(self, geo_info, n_digits_seconds=1):

        self.geo_info = geo_info

        self.ip_address = geo_info["ip"]

        latitude = float(geo_info["lat"])
        longitude = float(geo_info["lng"])

        self.my_location = geo_info.get("my_location")
        self.distance = geo_info.get("distance")

        self.location_sexagesimal = make_sexagesimal_location(latitude=latitude,
                                                              longitude=longitude,
                                                              n_digits_seconds=n_digits_seconds)
        self.location_decimal = make_decimal_location(latitude=latitude,
                                                      longitude=longitude,
                                                      n_decimals=n_digits_seconds + 1)
        self.location_human = make_human_location(country_code=geo_info["country"],
                                                  city=geo_info["city"])

        if self.distance is not None:
            my_lat = geo_info["my_lat"]
            my_lng = geo_info["my_lng"]
            self.location_me = make_sexagesimal_location(latitude=my_lat,
                                                         longitude=my_lng,
                                                         n_digits_seconds=n_digits_seconds)

    def make_report(self, output_format: str = "sexagesimal"):
        """
        Make a report of the location

        Args:
            output_format: str
                Type of report to make:

                    decimal:        decimal representation of location
                    sexagesimal:    sexagesimal representation of location
                    human:          human representation of location
                    raw:            raw output of geolocation
                    full:           full report with all information
        """
        if output_format == "decimal":
            self.report_location_decimal()
        elif output_format == "sexagesimal":
            self.report_location_sexagesimal()
        elif output_format == "human":
            self.report_location_human()
        elif output_format == "raw":
            self.report_location_raw()
        elif output_format == "full":
            self.report_full()
        elif output_format == "short":
            self.report_short()
        else:
            raise ValueError(f"Option {output_format} not recognised")

    def report_location_decimal(self):
        """ Print the location as a decimal representation """
        print(self.location_decimal)

    def report_location_sexagesimal(self):
        """ Print the location as a sexagesimal representation """
        print(self.location_sexagesimal)

    def report_location_human(self):
        """ Print the location as City/Country representation """
        print(self.location_human)

    def report_location_raw(self):
        """ Show the raw output of the geocoder module  """
        pprint.pprint(self.geo_info)

    def report_full(self):
        """ Give a full report of the location """
        print(f"Location of server {self.ip_address}:")
        formatter = "{:20} : {}"
        print(formatter.format("  decimal", self.location_decimal))
        print(formatter.format("  sexagesimal", self.location_sexagesimal))
        print(formatter.format("  human", self.location_human))
        if self.distance is not None and self.distance > 0:
            print(f"Distance from device @ {self.my_location}: {self.distance:.0f} km")

    def report_short(self):
        """ Give a one line short location """
        msg = f"Server {self.ip_address} @ {self.location_human} has coordinates ({self.location_sexagesimal})"
        if self.distance is not None and self.distance > 0:
            distance = int(round(self.distance, 0))
            msg += f"\nDistance from {self.my_location} ({self.location_me}):  {distance}km."
        print(msg)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from whereisip.skeleton import fib`,
# when using this Python module as a library.


def get_geo_location_device(my_location, reset_cache=False, write_cache=True):
    """
    Get the latitude/longitude from your location given by my_location

    Args:
        my_location:  str
            Name of your device location, e.g 'Ottawa, ON'
        reset_cache: bool
            Reset the cache
        write_cache: bool
            Write the locations to cache file

    Returns: tuple
        Latitude, longitude in decimal representation
    """
    if my_location is None:
        cache_suffix = "me"
    else:
        cache_suffix = my_location
    cache_file = get_cache_file(ipaddress=cache_suffix, write_cache=write_cache)

    if not cache_file.exists() or reset_cache:
        if my_location is None:
            geocode = geocoder.ip("me")
            geo_info = geocode.geojson['features'][0]['properties']

            location = geoinfo2location(geo_info)
        else:
            try:
                latlon = geocoder.location(my_location)
            except ValueError:
                _logger.debug(f"{my_location} failed. Try if it is an ip")
                geocode = geocoder.ip(my_location)
                geo_info = geocode.geojson['features'][0]['properties']
                location = geoinfo2location(geo_info)
            else:
                location = {
                    "my_location": my_location,
                    "my_lat": latlon.lat,
                    "my_lng": latlon.lng}

        _logger.debug(f"Writing my location to cache {cache_file}")
        if write_cache:
            with open(cache_file, "w") as stream:
                json.dump(location, stream, indent=True)
    else:
        _logger.debug(f"Reading my location from cache {cache_file}")
        with open(cache_file, "r") as stream:
            location = json.load(stream)

    return location


def get_geo_location_ip(ipaddress=None, reset_cache=False, write_cache=True):
    """
    Get the location of the local machine of the ip address if given

    Args:
        ipaddress: str
            Ip address
        reset_cache: bool
            Reset the cache
        write_cache:
            Write the cache

    """
    cache_file = get_cache_file(ipaddress=ipaddress, write_cache=write_cache)

    if not cache_file.exists() or reset_cache:
        if ipaddress is None:
            geocode = geocoder.ip("me")
        else:
            geocode = geocoder.ip(ipaddress)
        if not geocode.ok:
            raise IpErrorNoLocationFound(f"Failed to get a location for IP address {ipaddress}")

        geo_info = geocode.geojson['features'][0]['properties']
        if geo_info["status"] != "OK":
            raise IpErrorNoLocationFound(f"Failed to get a location for IP address {ipaddress}")
        _logger.debug(f"Storing geo_info to cache {cache_file}")
        if write_cache:
            _logger.debug(f"Writing geo_info to cache {cache_file}")
            with open(cache_file, "w") as stream:
                json.dump(geo_info, stream, indent=True)
    else:
        _logger.debug(f"Reading geo_info from cache {cache_file}")
        with open(cache_file, "r") as stream:
            geo_info = json.load(stream)

    return geo_info


class SmartFormatter(argparse.ArgumentDefaultsHelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Get the location of your server (or any other server) and calculate the "
                    "distance to your own location",
        formatter_class=SmartFormatter)
    parser.add_argument(
        "--reset_cache",
        action="store_true",
        default=False,
        help="Reset the cache files located in the .cache directory. Without reset, the information"
             "is read from a cache file instead of making a new request to geocoder. "
             "Each IP address of location gets its own cache file."
    )
    parser.add_argument(
        "--skip_cache",
        action="store_true",
        help="Do not read of write to the cache files",
        default=False,
    )
    parser.add_argument("--n_digits_seconds", type=int, default=1,
                        help="Number of digits to use for the seconds notation. If a decimal "
                             "notation is used, the number of decimals will be n_digit_seconds + 1")
    parser.add_argument(
        "--ip_address",
        help="The ip address to get the geo location from. If not given, the local machine is used"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="whereisip {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-f",
        "--format",
        help="R|Format of the output. Choices are:\n"
             ""
             " - decimal    : Decimal latitude/longitude (default)\n"
             " - sexagesimal: Sexagesimal latitude/longitude\n"
             " - human      : Human location City/Country\n"
             " - full       : Full report with all location notations\n"
             " - short      : A compact report with a sexagesimal and human nation + distance\n"
             " - raw        : raw output from api\n",
        choices=OUTPUT_FORMATS,
        default="short"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--debug",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "--my_location",
        metavar="<Location or IP>",
        help="Define the location of your device which is used to calculate the distance to "
             "the server. "
             "A location can be a 'cite,country' combination (or any other address recognised by"
             " Google) or an IP address. "
             "In case no location is given and the *ip_address* option is used to specify an other"
             "server than your local server, my location is set to you local server's IP address"
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s [%(lineno)4d]:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting getting location...")

    write_cache = not args.skip_cache

    reset_cache = args.reset_cache | args.skip_cache

    geo_info_ip = get_geo_location_ip(ipaddress=args.ip_address,
                                      reset_cache=reset_cache,
                                      write_cache=write_cache)

    my_device_latlon = get_geo_location_device(my_location=args.my_location,
                                               reset_cache=reset_cache,
                                               write_cache=write_cache)
    if my_device_latlon is not None:
        geo_info_ip["my_location"] = args.my_location
        for key, value in my_device_latlon.items():
            geo_info_ip[key] = value

        try:
            geo_info_ip["distance"] = get_distance_to_server(geo_info_ip)
        except TypeError:
            _logger.warning(f"Failed to calculate distance to {my_device_latlon}\n\n")

    server = LocationReport(geo_info=geo_info_ip,
                            n_digits_seconds=args.n_digits_seconds)
    server.make_report(output_format=args.format)

    _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m whereisip.skeleton 42
    #
    run()
