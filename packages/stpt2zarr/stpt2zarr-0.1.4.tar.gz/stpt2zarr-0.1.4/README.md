# STPT to Zarr converter

Convert STPT scan dataset to Zarr.

## Install

```
pip install stpt2zarr
```

### Requirements

* click
* dask
* distributed
* imaxt_image
* python_dateutil
* xarray
* zarr

## Usage

### Arguments
* input_path: the root folder of the STPT scan containing a mosaic file
* output_path: the location where to store the converted output in Zarr format 

### From Python script

```
from stpt2zarr import stpt2zarr

stpt2zarr(input_path, output_path)
```

### From the command line

```
stpt2zarr input_path output_path
```
