# Accessing the Digital Earth Normalised Radar Backscatter Product for Sentinel-1 from Geoscience Australia 

This repository demonstrates how to use Python to access preliminary Sentinel-1 Interferometric Wide (IW) mode backscatter products developed by Geoscience Australia. 

For Sentinel-1, Geoscience Australia's Digital Earth (DE) branch are currently offering a suite of experimental products, with sample data available over parts of Australia and Antarctica.
The product is a collaborative effort from Digital Earth Australia and Digital Earth Antarctica, with support from the CSIRO.

## Data availability

Geoscience Australia's Sentinel-1 data is published across multiple products, one for each polarisation mode used to capture the data.

There are two collections available: Collection 0 and Collection 1. We recommend using Collection 1 as it is closer to the format we will use for final data release. If Collection 1 does not have sufficient coverage to meet your test case, we recommend looking at Collection 0, which has wider area coverage and deeper timeseries data.

### Collection 0
You can see the distribution of captured data for Collection 0 over time and space in the DEA Dev Explorer:
* [Collection 0 VV+VH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_vv_vh_0)
* [Collection 0 VV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_vv_0)
* [Collection 0 HH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_hh_0)
* [Collection 0 HH+HV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_hh_hv_0)

### Collection 1
You can see the distribution of captured data for Collection 1 over time and space in the DEA Dev Explorer:
* [Collection 1 VV+VH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_vv_vh_1)
* [Collection 1 VV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_vv_1)
* [Collection 1 HH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_hh_1)
* [Collection 1 HH+HV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_hh_hv_1)

## Documentation

This repository provides examples for how to load data in two ways:
* Using DEA's development STAC API, which can be run on any computer.
* Using DEA's development Open Data Cube, which is only available in DEA's Development or Production Sandbox environment. 

If you are not a Geoscience Australia employee, you will need to use the STAC API approach.

Both Collection 0 and Collection 1 are available.

We provide two options for documentation
* [Rendered html pages](demo_html_pages), which can be viewed in a browser. 
This shows you the outcome of each step required to load and transform the data.
* [iPython notebooks](demo_notebooks), which can be run in an appropriate environment.
  * [Collection 0 tutorial](demo_notebooks/tutorial_c0)
  * [Collection 1 tutorial](demo_notebooks/tutorial_c1)

To view either file, you will first need to [clone the repository](#cloning-the-repository) to get a copy of the files.

We also have a collection of recorded videos that provide an overview of each iPython notebook. 
If you wish to view these videos, please contact DigitalEarthAntarctic@ga.gov.au to request access.

## Set up

### Cloning the repository
To access and run the iPython notebooks, you will need to clone this repository into your local computing environment, or the Digital Earth Australia Development or Production Sandbox. 

In a terminal, navigate to where you wish to keep the repository and run
```
git clone https://github.com/caitlinadams/de-sar-sample-data.git
```

### Updating the repository
This repository is in a state of active development, so we recommend regularly running `git pull` to get new notebooks.

### Setting up the environment

#### Own computer or cloud
If using your own computer to load data from the STAC API, you will need a Python environment with the required packages. 
Two different environment files are provided:
* A Conda [environment.yaml](environment.yaml) file
    * [Install conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#installing-conda)
    * [Install the environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)
    * [Activate the environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment)
* A Pixi [pyproject.toml](pyproject.toml) file
    * [Install pixi](https://pixi.sh/dev/installation/)
    * [Install the environment](https://pixi.sh/dev/python/tutorial/#installation-pixi-install)
    * [Activate the environment](https://pixi.sh/dev/workspace/environment/#activation)

You can also choose to manually install the following required packages using your preferred python package manager:
* botocore       1.40.70
* dea_tools      0.4.7
* folium         0.19.7
* geopandas      1.1.1
* ipykernel      6.31.0
* ipywidgets     8.1.8
* matplotlib     3.10.7
* netcdf4        1.7.3
* numpy          2.3.4
* odc-stac       0.4.0
* pystac-client  0.8.6
* python         3.13.9
* scikit-image   0.25.2
* scipy          1.16.3
* de_sar_demo    0.0.1    (use `pip install .` from the repository directory)

#### DEA Sandbox
This is intended for employees internal to Geoscience Australia.
For all other users, we recommend accessing data via the STAC API.

If using DEA's Development or Production Sandbox, no conda/pixi environment set up is required.

You will need to pip install the `de_sar_demo` module to gain access to utility functions for speckle filtering and mask dilation.
You will need to pip install the module each time you log into the Sandbox.
Follow these steps
1. Open a terminal
1. In the terminal, navigate to where you cloned the repository. For example, `cd repositories/de-sar-sample-data` if you cloned it in a folder called `repositories`
1. In the terminal, run `pip install .`

If you are using the Production Sandbox, you will also need to connect to the Development ODC database.
Please see internal Geoscience Australia documentation on how to do this.
