.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://readthedocs.org/projects/whereisip/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://whereisip.readthedocs.io/en/stable/
    .. image:: https://img.shields:2.io/pypi/v/whereisip.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/whereisip/
    .. image:: https://img.shields.io/conda/vn/conda-forge/whereisip.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/whereisip
    .. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
        :alt: Project generated with PyScaffold
        :target: https://pyscaffold.org/

=========
whereisip
=========


Get the geolocation of the current server


This package provides a command line utility to get the geolocation of the current server.

Installation
============

To install with conda do::

   conda install whereisip

To install with pip do::

   pip install whereisip

Requirements
------------

- Python 3.6+
- appdirs
- country_converter
- geocoder
- latloncalc

Python version
--------------
Tested for Python 3.6, 3.7, 3.8, 3.9, 3.10

Usage
=====

Varying output format
---------------------

You can simply run on the command line::

  whereisip

This yields the location of the server you are currently logged into, e.g.::

   >>> Server 37.97.253.1 @ Amsterdam/Netherlands (NL) has coordinates (52° 22′ 26.4″ N, 4° 53′ 22.9″ E)

Other output formats can be picked as well. If you only want the geo coordinates of the location of your server you can do::

   whereisip --format sexagesimal

which yields::

   >>> 52° 22′ 26.4″ N, 4° 53′ 22.9″ E

Or if you prefer to have a decimal representation of your server's location you can do::

   whereisip --format decimal

resulting in::

   >>> 52.37, 4.89

To get the name of the location in stead of coordinates you can do::

   whereisip --format human

which gives::

   >>> Amsterdam/Netherlands (NL)

Note that you can copy-paste the sexagesimal representation  *52° 22′ 26.4″ N, 4° 53′ 22.9″ E* into
google maps in order to show your location on the map.

More examples
-------------

This utility can be used to determine the distance of your server to your current location.
For instance, if your are located in Amsterdam, NL and your are logged in onto the google server,
you can do::

    whereisip  --my_location Amsterdam,NL

Now, next to the location of your sever, also the distance to your location is given::

    Server 8.8.8.8 @ Mountain View/United States (US) has coordinates (37° 24′ 20.2″ N, 122° 4′ 39.0″ W)
    Distance from Amsterdam,NL (52° 22′ 21.9″ N, 4° 53′ 37.0″ E):  8816km.

You can also specify the server location in your are not logged into it like::

    whereisip --ip 8.8.8.8 --my_location Amsterdam,NL

Note the your location does not need to be a server (but can be), but can be any address recognised by google.
In case you specify another server and don't specify your location, by
default your location is set to the location of your current server. The distance is calculated
based on this location.

Cache files
-----------

The *whereisip* script uses *geocoder* to retrieve the coordinates of a location and a server.
All retrieved information is stored in cache files under *$HOME/.cache/whereisip* (for Linux).
The next time you want to retrieve information on the same server or location, the cache file is
read instead of making a new query to *geocoder*. In case you want to force to reset the cache files
you can pass the *--reset_cache* option. In case you don't want to use cache files at all, you
can also pass *--skip_cache* option; this prevent to write any cache files at all.

Get Help
--------

The help information can be shown with::

    whereisip --help

which gives the full help::

    usage: whereisip [-h] [--reset_cache] [--skip_cache]
                     [--n_digits_seconds N_DIGITS_SECONDS]
                     [--ip_address IP_ADDRESS] [--version]
                     [-f {sexagesimal,decimal,human,raw,full,short}] [-v] [-vv]
                     [--my_location <Location or IP>]

    Get the location of your server (or any other server) and calculate the
    distance to your own location

    optional arguments:
      -h, --help            show this help message and exit
      --reset_cache         Reset the cache files located in the .cache directory.
                            Without reset, the informationis read from a cache
                            file instead of making a new request to geocoder. Each
                            IP address of location gets its own cache file.
                            (default: False)
      --skip_cache          Do not read of write to the cache files (default:
                            False)
      --n_digits_seconds N_DIGITS_SECONDS
                            Number of digits to use for the seconds notation. If a
                            decimal notation is used, the number of decimals will
                            be n_digit_seconds + 1 (default: 1)
      --ip_address IP_ADDRESS
                            The ip address to get the geo location from. If not
                            given, the local machine is used (default: None)
      --version             show program's version number and exit
      -f {sexagesimal,decimal,human,raw,full,short}, --format {sexagesimal,decimal,human,raw,full,short}
                            Format of the output. Choices are:
                             - decimal    : Decimal latitude/longitude (default)
                             - sexagesimal: Sexagesimal latitude/longitude
                             - human      : Human location City/Country
                             - full       : Full report with all location notations
                             - short      : A compact report with a sexagesimal and human nation + distance
                             - raw        : raw output from api
                             (default: short)
      -v, --verbose         set loglevel to INFO (default: None)
      -vv, --debug          set loglevel to DEBUG (default: None)
      --my_location <Location or IP>
                            Define the location of your device which is used to
                            calculate the distance to the server. A location can
                            be a 'cite,country' combination (or any other address
                            recognised by Google) or an IP address. In case no
                            location is given and the *ip_address* option is used
                            to specify an otherserver than your local server, my
                            location is set to you local server's IP address
                            (default: None)

.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.2.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
