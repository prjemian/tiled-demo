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
import dhtioc_csv
import numpy


FILE_OF_UNRECOGNIZED_FILE_TYPES = "/tmp/unrecognized_files.txt"


mimetype_table = {
    is_spec_file_with_header: "text/spec_data",  # spec2nexus.spec.is_spec_file_with_header
    # is_dhtioc_file: "text/dhtioc_data",  # local definition, special CSV file
    dhtioc_csv.is_dhtioc_file: dhtioc_csv.MIMETYPE,  # local definition, special CSV file
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
