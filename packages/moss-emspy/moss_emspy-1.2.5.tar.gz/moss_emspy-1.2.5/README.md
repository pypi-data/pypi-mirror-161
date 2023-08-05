# MOSS emspy

## Description

This is the Python SDK to interact with [M.O.S.S. Computer Grafik Systeme GmbH](https://www.moss.de/wega/) WEGA-EMS

## Installation

This package kann be installed using pip

```shell
python -m pip install moss_emspy
```

## Usage

```python
my_service = Service("http://localhost:8080/wega-ems/",
            username="Test",
            password="Test")
my_service.projects
```
