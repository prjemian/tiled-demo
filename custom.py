"""
Custom handling for data file types not recognized by tiled.

https://blueskyproject.io/tiled/how-to/read-custom-formats.html
"""

from punx.utils import isHdf5FileObject
from punx.utils import isNeXusFile
from spec2nexus.spec import is_spec_file_with_header
from tiled.adapters.dataframe import DataFrameAdapter
from pandas import DataFrame
import dask
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

"""
(tiled) prjemian@zap:~/Documents/tiled-demo$ !tiled
tiled serve config config.yml
ValidationError while parsing configuration file config.yml: {'tree': 'dhtioc_mbr', 'args': {'directory': '../raw/porch/2020/11', 'mimetype_detection_hook': 'custom:detect_mimetype', 'readers_by_mimetype': {'text/dhtioc_data': 'custom:read_dhtioc'}}} is not of type 'array'
Aborted.
"""

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
            md["IOC_prefix"] = content[len("# IOC prefix: "):].strip()
            break
        elif n < 5 and content.strip() != "#":
            p = content.find(": ")
            key = content[:p].lstrip("#").strip()
            value = content[p+1:].strip()
            md[key] = value
    md["humidity"] = dict(
        description="relative humidity, %",
        units="%",
        pvname=f"{md['IOC_prefix']}humidity"
    )
    md["temperature"] = dict(
        description="temperature, C",
        units="C",
        pvname=f"{md['IOC_prefix']}temperature"
    )

    numbers = numpy.array(
        [
            list(map(float, line.split()))
            for line in buf
            if not line.startswith("#")
        ]
    ).T
    df = DataFrame(
        dict(
            timestamp=numbers[0],
            humidity=numbers[1],
            temperature=numbers[2],
            iso8601=list(map(str, map(datetime.datetime.fromtimestamp, numbers[0]))),
        )
    )
    return DataFrameAdapter.from_pandas(df, npartitions=1, metadata=md)
