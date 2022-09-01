"""Read the synApps MDA file format."""

from tiled.adapters.dataframe import DataFrameAdapter
from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
import mda
import pathlib


def as_str(v):
    if isinstance(v, bytes):
        return v.decode()
    return v


def read_mda(filename):
    mda_obj = mda.readMDA(
        str(filename),
        useNumpy=True,
        verbose=False,
        showHelp=False,
    )
    # read the "header"
    h_obj = mda_obj[0]
    metadata = {key: h_obj[key] for key in h_obj["ourKeys"] if key != "ourKeys"}
    metadata["PVs"] = {
        as_str(key): dict(
            desc=as_str(values[0]),
            unit=as_str(values[1]),
            value=values[2],
            EPICS_type=mda.EPICS_types_dict.get(values[3], f"unknown #{values[3]}"),
            count=values[4],
        )
        for key, values in h_obj.items()
        if key not in h_obj["ourKeys"]
    }
    if "version" in metadata:
        # fix the truncation error of 1.299999...
        metadata["version"] = round(metadata["version"], 2)
    if len(mda_obj) != metadata["rank"] + 1:
        raise ValueError(f"rank={metadata['rank']} but {len(mda_obj)=}")

    # TODO: refactor into a hierarchical structure
    # MapAdapter(scans, metadata=file_md)
    # scans["scan1"] = {}
    # scans["scan2"] = {}
    # scans["scan..."] = {}
    # each scan is MapAdapter(P_and_D_array_dict, metadata=scan_md)
    # each array_dict_value is ArrayAdapter.from_array(arr, metadata=array_md)
    # ... work this out ...

    content = {}
    for scan in mda_obj[1:]:
        prefix = f"S{scan.rank}_"
        # print(f"{scan.rank=}")
        content[f"{prefix}time"] = as_str(
            scan.time
        )  # TODO: convert to timestamp (must assume a time zone)
        content[f"{prefix}number_requested"] = scan.npts
        content[f"{prefix}number_acquired"] = scan.curr_pt
        for detector in scan.d:
            v = {
                k: getattr(detector, k)
                for k in "data desc fieldName number unit".split()
            }
            v["EPICS_PV"] = as_str(detector.name)
            content[f"{prefix}{v['fieldName']}"] = v
        for positioner in scan.p:
            v = {
                k: getattr(positioner, k)
                for k in """
                    data
                    desc
                    fieldName
                    number
                    readback_desc
                    readback_name
                    readback_unit
                    step_mode
                    unit
                """.split()
            }
            v["readback_PV"] = v.pop("readback_name")  # rename
            v["EPICS_PV"] = as_str(positioner.name)
            content[f"{prefix}{v['fieldName']}"] = v
        for i, trigger in enumerate(scan.t, start=1):
            v = {k: getattr(trigger, k) for k in "command number".split()}
            v["EPICS_PV"] = as_str(trigger.name)
            content[f"{prefix}T{i}"] = v

    # build nested structure for tiled
    key_list = [k for k, v in content.items() if isinstance(v, dict) and "data" in v]
    data = {}
    for k in key_list:
        arr = content[k].pop("data")
        data[k] = ArrayAdapter.from_array(arr, metadata=content[k])

    return MapAdapter(data, metadata=metadata)


def main():
    path = (
        pathlib.Path().home()
        / "Documents"
        / "projects"
        / "NeXus"
        / "exampledata"
        / "APS"
        / "scan2nexus"
    )
    for filename in sorted(path.iterdir()):
        if filename.name.endswith(".mda"):
            structure = read_mda(filename)
            print(f"{filename.name=}")
            print(structure)


if __name__ == "__main__":
    main()
