# Changelog moss_emspy

## [1.2.4] - 2021-11-17

- Add option to specify attachments output
- Add Exception for EMS Connection error

## [1.2.3] - 2021-08-30

- Fix close() method to logout from EMS

## [1.2.2] - 2021-07-01

- Restore missing file query objctclass layers

## [1.2.1] - 2021-05-17

### Fixed

- Restore geometry_converter deleted from git

## [1.2.0] - 2021-05-12

### Added

#### EMSCLI

- Add a new flag for the export submodule _--master_filter_ to use a filter for the master object.

### Fixed

- Fix output variant tree structure when there is just one node

## [1.1.0] - 2021-04-29

### Added

- A new command line tool has been added: **emscli**. It's a command line tool to interact with WEGA-EMS. This first release icludes 2 subcommands used to backup/restore a Project:

  - _export_: Export the selected project in specific directory
  - _import_: Import an exported project

  Please check the documentation for more informations.

- Method _variants_tree()_ has been added to the EmsProject Class. The output of this method is an iterable with the current variant tree structure:

```python
>>> project = my_service.project("wegaems_prj20")
>>> project.variants_tree()

├── qserfora_2021_01_28_qswegaci_1
│   └── v01
├── Windpark Tostedt
│   ├── V_001
│   └── V_02
└── qserfora2_2021_03_25
    └── v01
```

### Changed

- The attachments method has a new parameter _asUrl_. If True, the output will contain the exact
  path of an attachment. This is important to get the exact path of an attachment when using hash-storage as storaging system.

- The same query parameter of WEGA-EMS query, can be used inside the query method. This is usefull, for example _returnIdsOnly_ to return only the ids of the features.

```python
query = my_layer.query(where="ID<40", returnIdsOnly=True)
```

- The query method accept a geometry to limit the results to a specific extent. For example:

```python
FILTER_GEOMETRY = {
        "xmin": 400041.3182861694,
        "ymin": 5579618.707941717,
        "xmax": 401007.4908240417,
        "ymax": 5580061.03023693
    }

query = my_layer.query(geometry=FILTER_GEOMETRY)
```

## [1.0.2] - 2021-03-09

### Fixed

- Fixed wrong type definition for python2

## [1.0.1] - 2021-03-08

First release.
