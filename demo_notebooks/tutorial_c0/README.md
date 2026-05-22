# Tutorial Notebooks

These notebooks are designed to teach you about the product, and are intended to be followed in numerical order.

* [01_product_info.ipynb](01_product_info.ipynb) - high-level information about the product, including data availability and metadata
* [02_demonstration.ipynb](02_demonstration.ipynb) - a simple demonstration of key steps involved in loading and preparing SAR backscatter data for analysis
* [03_loading_with_stac.ipynb](03_loading_with_stac.ipynb) - more detailed information of how to work with the STAC API
* [04_loading_with_datacube.ipynb](04_loading_with_datacube.ipynb) - more detailed information of how to work with the Datacube API
* [05_post_processing_data.ipynb](05_post_processing_data.ipynb) - more detailed information about transformations such as masking, speckle filtering, and converting to different backscatter normalisation conventions.

The [demonstration notebook](02_demonstration.ipynb) and [post-processing notebook](05_post_processing_data.ipynb) can be configured to run either in a Geoscience Australia Sandbox environment (by setting `approach = "datacube"` in the first cell) or in a local compute environment (by setting `approach = "stac"` in the first cell).