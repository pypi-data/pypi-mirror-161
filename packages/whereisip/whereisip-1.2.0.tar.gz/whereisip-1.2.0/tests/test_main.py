import pytest

from whereisip.getgeolocation import (main)

__author__ = "eelco"
__copyright__ = "eelco"
__license__ = "MIT"


def test_main_default(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["--skip_cache",
          "--ip_address", "8.8.8.8",
          "--my_location", "Amsterdam,The Netherlands"])
    captured = capsys.readouterr()
    expected = "Server 8.8.8.8 @ Mountain View/United States (US) has coordinates (37° 24′ 20.2″ N, 122° 4′ 39.0″ W)\n" \
               "Distance from Amsterdam,The Netherlands (52° 22′ 21.9″ N, 4° 53′ 37.0″ E):  8816km.\n"
    assert expected == captured.out


def test_main_default_decimal(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["--skip_cache",
          "--ip_address", "8.8.8.8",
          "--format", "decimal"])
    captured = capsys.readouterr()
    expected = "37.41, -122.08\n"
    assert expected == captured.out


def test_main_default_sexagesimal(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["--skip_cache",
          "--ip_address", "8.8.8.8",
          "--format", "sexagesimal"])
    captured = capsys.readouterr()
    expected = "37° 24′ 20.2″ N, 122° 4′ 39.0″ W\n"
    assert expected == captured.out


def test_main_full(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["--skip_cache",
          "--ip_address", "8.8.8.8",
          "--my_location", "Amsterdam,The Netherlands",
          "--format", "full"])
    captured = capsys.readouterr()
    expected = "Location of server 8.8.8.8:\n" \
               "  decimal            : 37.41, -122.08\n" \
               "  sexagesimal        : 37° 24′ 20.2″ N, 122° 4′ 39.0″ W\n" \
               "  human              : Mountain View/United States (US)\n" \
               "Distance from device @ Amsterdam,The Netherlands: 8816 km\n"
    assert expected == captured.out


def test_main_default_short(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["--skip_cache",
          "--ip_address", "8.8.8.8",
          "--my_location", "Amsterdam,The Netherlands",
          "--format", "short"])
    captured = capsys.readouterr()
    expected = "Server 8.8.8.8 @ Mountain View/United States (US) has coordinates (37° 24′ 20.2″ N, 122° 4′ 39.0″ W)\n" \
               "Distance from Amsterdam,The Netherlands (52° 22′ 21.9″ N, 4° 53′ 37.0″ E):  8816km.\n"
    assert expected == captured.out


def test_main_raw(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["--skip_cache",
          "--ip_address", "8.8.8.8",
          "--my_location", "Amsterdam,The Netherlands",
          "--format", "raw"])
    captured = capsys.readouterr()
    expected = ("{'address': 'Mountain View, California, US',\n"
                " 'city': 'Mountain View',\n"
                " 'country': 'US',\n"
                " 'distance': 8815.981026602274,\n"
                " 'hostname': 'dns.google',\n"
                " 'ip': '8.8.8.8',\n"
                " 'lat': 37.4056,\n"
                " 'lng': -122.0775,\n"
                " 'my_lat': 52.3727598,\n"
                " 'my_lng': 4.8936041,\n"
                " 'my_location': 'Amsterdam,The Netherlands',\n"
                " 'ok': True,\n"
                " 'org': 'AS15169 Google LLC',\n"
                " 'postal': '94043',\n"
                " 'raw': {'anycast': True,\n"
                "         'city': 'Mountain View',\n"
                "         'country': 'US',\n"
                "         'hostname': 'dns.google',\n"
                "         'ip': '8.8.8.8',\n"
                "         'loc': '37.4056,-122.0775',\n"
                "         'org': 'AS15169 Google LLC',\n"
                "         'postal': '94043',\n"
                "         'readme': 'https://ipinfo.io/missingauth',\n"
                "         'region': 'California',\n"
                "         'timezone': 'America/Los_Angeles'},\n"
                " 'state': 'California',\n"
                " 'status': 'OK'}\n")

    assert expected == captured.out
