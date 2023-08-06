# IMC to Zarr converter

Convert IMC scan dataset to Zarr.

## Install

```
pip install imc2zarr
```

### Requirements

* click
* numpy
* pandas
* python_dateutil
* xarray

## Usage

### Arguments
* input_path:
  * the root folder of the IMC scan containing a single mcd file and/or other related files: XML meta & scan data in text format
  * or, the path of an mcd file
* output_path: the location where to store the converted output in Zarr format 

### From Python script

```
from imc2zarr import imc2zarr

imc2zarr(input_path, output_path)
```

### From the command line

```
imc2zarr input_path output_path
```
