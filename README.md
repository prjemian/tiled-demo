# tiled-demo

<!-- 2022-08-29 -->

Demonstrate tiled server and handling of custom formats.

- [tiled-demo](#tiled-demo)
  - [Goals](#goals)
  - [Stretch goals](#stretch-goals)
  - [Links](#links)

## Goals

- [x] Write a custom data file identifier.
- [x] Write a custom data file loader.
- [x] Identify NeXus/HDF5 files with arbitrary names.
- [x] Identify SPEC data files with arbitrary names and read them.
- [ ] Authentication

## Stretch goals

- [x] Read `.jpg` files.
- [x] Learn how to ignore files such as `.xml` (without startup comments).
- [ ] Handle the `.npy` file with the 10,000+ images. (maybe unrealistic)
- [x] Handle all examples in `punx` and `spec2nexus`
- [x] Read the [synApps MDA format](https://github.com/epics-modules/sscan/blob/master/documentation/saveData_fileFormat.txt) ([Python support](https://github.com/EPICS-synApps/utils/blob/master/mdaPythonUtils/INSTALL.md))

## Links

- <https://github.com/bluesky/tiled/issues/175>
- <https://blueskyproject.io/tiled/how-to/read-custom-formats.html#case-2-no-file-extension>
