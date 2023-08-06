# IMAXT Mosaic Pipeline

The IMAXT mosaic pipeline produces stitched images from tile observations.
Currently we support two instruments: Serial Two-Photon Tomography (STPT)
and AXIOScan. 

Note that raw data (typically in the form of TIFF images) need to be converted
to Zarr format first using e.g. [stpt2zarr](https://pypi.org/project/stpt2zarr/)
or [axio2zarr](https://pypi.org/project/axio2zarr/).


## Pipeline Definition File

In order to run the pipeline you need a YAML file as follows:

```
version: 1

name: imaxt-mosaic

input_path: /storage/imaxt/raw/stpt/20211020_PDX_STG139_GFP_029621_100x15um
output_path: /storage/imaxt/processed/stpt/20211020_PDX_STG139_GFP_029621_100x15um

stitcher: stpt

recipes:
  - calibration
  - mosaic
  - beadfit

resources:
  cpu: 16
  workers: 1
  memory: 48
```

### Execute locally with Owl

In order to run the pipeline locally, install as follows:
```
pip install imaxt-mosaic owl-pipeline-client
```

and execute:

```
owl execute pipeline.yaml
```

### Remote execution

To execute the pipeline using a remote Owl server it is not needed to install
the module locally. Just submit as:

```
owl submit pipeline.yaml
```
