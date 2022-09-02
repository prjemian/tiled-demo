"""
Custom handling for data file types not recognized by tiled.

https://blueskyproject.io/tiled/how-to/read-custom-formats.html
"""

from punx.utils import isHdf5FileObject
from punx.utils import isNeXusFile
from spec2nexus.spec import is_spec_file_with_header
from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
import datetime
import numpy


FILE_OF_UNRECOGNIZED_FILE_TYPES = "/tmp/unrecognized_files.txt"


def is_dhtioc_file(filename):
    """
    CSV file from dhtioc project.

    Example content::

        # file: /home/pi/Documents/dhtioc_raw/2021/03/2021-03-06.txt
        # created: 2021-03-06 00:00:00.506106
        # program: dhtioc
        # version: 1.1.1+27.g45d1c2c
        # URL: https://dhtioc.readthedocs.io/
        #
        # IOC prefix: rpiad6d:
        #
        # time: python timestamp (``time.time()``), seconds (since 1970-01-01T00:00:00 UTC)
        # RH: relative humidity, %
        # T: temperature, C
        #
        # time  RH  T
        1615010400.50 51.5 20.6
        1615010402.53 51.5 20.6
    """
    with open(filename, "r") as fp:
        for line_number, content in enumerate(fp.read().splitlines()):
            if "dhtioc" in content:
                return True
            if line_number > 3:
                break
    return False


mimetype_table = {
    is_spec_file_with_header: "text/spec_data",  # spec2nexus.spec.is_spec_file_with_header
    # is_dhtioc_file: "text/dhtioc_data",  # local definition, special CSV file
    is_dhtioc_file: "text/csv",  # local definition, special CSV file
    isNeXusFile: "application/x-hdf5",  # punx.utils.isNeXusFile
    isHdf5FileObject: "application/x-hdf5",  # punx.utils.isHdf5FileObject
}


def detect_mimetype(filename, mimetype):
    if mimetype is None:
        # When tiled has not already recognized the mimetype.
        mimetype = "text/csv"  # the default
        for tester, mtype in mimetype_table.items():
            # iterate through our set of known types
            if tester(filename):
                mimetype = mtype
                break

    if mimetype is None:
        with open(FILE_OF_UNRECOGNIZED_FILE_TYPES, "a") as fp:
            fp.write(f"{mimetype}  {filename}\n")

    return mimetype


def read_dhtioc(filename):
    """
    CSV file, partial header::

        # file: /home/pi/Documents/dhtioc_raw/2020/11/2020-11-14.txt
        # created: 2020-11-14 00:00:01.472291
        # program: dhtioc
        # version: 1.1.1+1.gcd2796d
        # URL: https://dhtioc.readthedocs.io/
    """
    buf = open(filename, "r").read().splitlines()
    md = {}
    for n, content in enumerate(buf):
        if content.startswith("# IOC prefix: "):
            md["IOC_prefix"] = content[len("# IOC prefix: ") :].strip()
            break
        elif n < 5 and content.strip() != "#":
            p = content.find(": ")
            key = content[:p].lstrip("#").strip()
            value = content[p + 1 :].strip()
            md[key] = value
    IOC = md["IOC_prefix"]
    md["temperature"] = dict(
        description="temperature, C", units="C", pvname=f"{IOC}temperature"
    )

    # fmt: off
    numbers = numpy.array(
        [
            list(map(float, line.split()))
            for line in buf
            if not line.startswith("#")
        ]
    ).T
    # fmt: on
    arrays = {}
    arrays["timestamp"] = ArrayAdapter.from_array(
        numbers[0],
        metadata=dict(description="Linux EPOCH, seconds since 1970-01-01 UTC")
    )
    arrays["humidity"] = ArrayAdapter.from_array(
        numbers[1],
        metadata=dict(
            description="relative humidity, %",
            units="%",
            EPICS_PV=f"{IOC}humidity",
        )
    )
    arrays["temperature"] = ArrayAdapter.from_array(
        numbers[2],
        metadata=dict(
            description="temperature, C",
            units="C",
            EPICS_PV=f"{IOC}temperature"
        )
    )
    arrays["Fahrenheit"] = ArrayAdapter.from_array(
        numbers[2]*1.8+32,
        metadata=dict(
            description="temperature, F",
            units="F",
            EPICS_PV=f"{IOC}temperature"
        )
    )
    # FIXME: cannot supply list of string?
    # arrays["iso8601"] = ArrayAdapter(
    #     list(map(str, map(datetime.datetime.fromtimestamp, numbers[0]))),
    #     metadata=dict(description="ISO-8601 time string")
    # )
    return MapAdapter(arrays, metadata=md)
