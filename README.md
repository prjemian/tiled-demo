# tiled

<!-- 2022-08-29 -->

Getting started with the new tiled server and handling of custom formats.

- [tiled](#tiled)
  - [Goal](#goal)
    - [Stretch goals](#stretch-goals)
  - [Links](#links)
  - [Local Directories with Examples](#local-directories-with-examples)
  - [Python environment](#python-environment)
  - [Identify Custom Files](#identify-custom-files)
  - [Configuration file](#configuration-file)

## Goals

- [ ] Write a custom data file identifier and loader.
- [ ] Support the example files shown.
- [ ] Authentication

### Stretch goals

- [ ] Handle the `.npy` file with the 10,000+ images. (maybe unrealistic)
- [ ] Handle all examples in `punx` and `spec2nexus`
- [ ] Handle the [synApps MDA format](https://github.com/epics-modules/sscan/blob/master/documentation/saveData_fileFormat.txt) ([Python support](https://github.com/EPICS-synApps/utils/blob/master/mdaPythonUtils/INSTALL.md))

## Links

- https://github.com/bluesky/tiled/issues/175
- https://blueskyproject.io/tiled/how-to/read-custom-formats.html#case-2-no-file-extension

## Local Directories with Examples

directory | file content
--- | ---
`~/Documents/2021_10_05_Gadikota_usaxs/` | mixed content, typical USAXS
`~/Documents/2022-02-10-databroker-2.0-test-usaxs/` | mixed content, typical USAXS
`~/Documents/raw/` | CSV files from `dhtioc` project
`~/Documents/specdata/` | SPEC

## Python environment

- create: `micromamba create -n tiled -f environment.yml`
- use: `micromamba activate tiled`

## Identify Custom Files

[example](https://blueskyproject.io/tiled/how-to/read-custom-formats.html#write-a-custom-function-for-detecting-the-mime-type):

```py
# custom.py

def detect_mimetype(filepath, mimetype):
    if mimetype is None:
        # If we are here, detection based on file extension came up empty.
        ...
        mimetype = "text/csv"
    return mimetype
```

## Configuration file

```yml
# config.yml
trees:

    tree: specdata
    args:
        directory: /home/prjemian/Documents/specdata/
        mimetypes_by_file_ext:
        .dat: text/spec_data

    # tree: files
    # args:
    #     directory: path/to/directory
    #     mimetypes_by_file_ext:
    #     .stuff: text/csv

    # tree: custom_files
    # args:
    #     directory: path/to/custom/directory
    #     mimetype_detection_hook: custom:detect_mimetype
```
