import asf_search as asf
from odc.geo import BoundingBox
import odc.geo.xr
from odc.stac import load
from pystac_client import Client
from de_sar_demo.speckle_filters import lee_filter_xr
import numpy as np
import xarray
from pathlib import Path
from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class SceneMetadata:
    """Dataclass for key metadata from Sentinel-1 SLC"""

    name: str
    start_time: str
    stop_time: str
    center_lat: float
    center_lon: float
    polarization: str
    processing_level: str


def _get_metadata_from_ASF(scene: str) -> SceneMetadata:
    """For a given Sentinel-1 SLC scene name, query ASF and return key metadata

    Parameters
    ----------
    scene : str
        Sentinel-1 SLC scene name, e.g. S1A_IW_SLC__1SSH_20250402T103324_20250402T103352_058576_073FF3_ED28

    Returns
    -------
    SceneMetadata
        Metadata including: name, start_time, stop_time, center_lat, center_lon, polarization, and processing_level
    """
    scene_metadata = asf.granule_search(
        [scene], asf.ASFSearchOptions(processingLevel=["SLC"])
    )

    if len(scene_metadata) == 0:
        raise ValueError(
            "No matching SLC scenes were found for this scene name. Check whether the requested scene name is for a SLC."
        )

    scene_properties = scene_metadata[0].properties

    scene_metadata = SceneMetadata(
        name=scene_properties["sceneName"],
        start_time=scene_properties["startTime"],
        stop_time=scene_properties["stopTime"],
        center_lat=scene_properties["centerLat"],
        center_lon=scene_properties["centerLon"],
        polarization=scene_properties["polarization"],
        processing_level=scene_properties["processingLevel"],
    )

    return scene_metadata


# Define function to query and download whole scenes (rather than bursts)
def find_and_load_single_scene_from_stac(
    stac_client: Client,
    scene: str,
    collection: Literal[0, 1] = 1,
    output_format: Literal["geotiff", "xarray"] = "geotiff",
    output_dir: Optional[str] = None,
    speckle_filter: bool = True,
    db: bool = True,
) -> Optional[xarray.Dataset]:
    """Query and load data for a given SLC scene ID. Data can be loaded as an xarray, or saved to a GeoTIFF.

    Parameters
    ----------
    stac_client: Client
        the STAC client used by pystac-client
    scene : str
        the scene ID to load, e.g. `S1A_IW_SLC__1SSH_20250402T103324_20250402T103352_058576_073FF3_ED28`. Must be an SLC
    collection: Literal[0, 1], optional
        the DE SAR collection number, either 0 or 1. Use 1 for the most up-to-date data, by default 1
    output_format : Literal["geotiff", "xarray"], optional
        the output format. One of "geotiff" or "xarray", by default "geotiff"
    output_dir : Optional[str], optional
        a string indicating where on disk the outputs should be stored if using "geotiff". By default None, in which case files will be saved in the same location as the script running the function.
    speckle_filter : bool, optional
        whether to apply the Lee speckle filter with a window of 3 pixels, by default True
    db : bool, optional
        whether to convert the gamma0 backscatter from linear scale to decibels, by default True

    Returns
    -------
    Optional[xarray.Dataset]
        An xarray containing the requested polarisation bands, provided if output_format="xarray". Otherwise, None is returned.

    Raises
    ------
    ValueError
        polarisation is not one of HH, HH+HV, VV, or VV+VH
    ValueError
        output_format is not one of "geotiff" or "xarray"
    RuntimeError
        no bursts were found for the scene
    """

    # Indicate start of processing
    print(f"Processing {scene}")

    # Get metadata from ASF
    print("    Querying ASF for metadata")
    scene_metadata = _get_metadata_from_ASF(scene)

    if collection == 0:
        nlooks_band = "number_of_looks"
        # Update settings depending on chosen polarisation
        if scene_metadata.polarization == "HH":
            collections_query = ["ga_s1_nrb_iw_hh_0"]
            bands_query = ["HH_gamma0", nlooks_band]
        elif scene_metadata.polarization == "HH+HV":
            collections_query = ["ga_s1_nrb_iw_hh_hv_0"]
            bands_query = ["HH_gamma0", "HV_gamma0", nlooks_band]
        elif scene_metadata.polarization == "VV":
            collections_query = ["ga_s1_nrb_iw_vv_0"]
            bands_query = ["VV_gamma0", nlooks_band]
        elif scene_metadata.polarization == "VV+VH":
            collections_query = ["ga_s1_nrb_iw_vv_vh_0"]
            bands_query = ["VV_gamma0", "VH_gamma0", nlooks_band]
        else:
            raise ValueError(
                f"Scene polarisation must be one of either HH, HH+HV, VV, or VV+VH. Returned polarisation from ASF was: {scene_metadata.polarization}"
            )
    elif collection == 1:
        nlooks_band = "oa_number_of_looks"
        # Update settings depending on chosen polarisation
        if scene_metadata.polarization == "HH":
            collections_query = ["ga_s1_nrb_iw_hh_1"]
            bands_query = ["hh_gamma0", nlooks_band]
        elif scene_metadata.polarization == "HH+HV":
            collections_query = ["ga_s1_nrb_iw_hh_hv_1"]
            bands_query = ["hh_gamma0", "hv_gamma0", nlooks_band]
        elif scene_metadata.polarization == "VV":
            collections_query = ["ga_s1_nrb_iw_vv_1"]
            bands_query = ["vv_gamma0", nlooks_band]
        elif scene_metadata.polarization == "VV+VH":
            collections_query = ["ga_s1_nrb_iw_vv_vh_1"]
            bands_query = ["vv_gamma0", "vh_gamma0", nlooks_band]
        else:
            raise ValueError(
                f"Scene polarisation must be one of either HH, HH+HV, VV, or VV+VH. Returned polarisation from ASF was: {scene_metadata.polarization}"
            )
    else:
        raise ValueError(
            f"Must specify collection as either 0 or 1. Supplied collection value was {collection}"
        )

    # Get list of output files
    output_files = []
    if output_format == "geotiff":
        output_files = [f"{scene}_{band.lower()}.tif" for band in bands_query]

        # Update files to include output directory
        if output_dir is not None:
            output_files = [Path(output_dir) / Path(file) for file in output_files]
        else:
            output_files = [Path(file) for file in output_files]

        # Check if files have been processed
        if all([file.is_file() for file in output_files]):
            print(
                f"    All requested polarisations for {scene} have already been processed. Check for files in {output_dir}"
            )
            return None
        else:
            generate_files = True
    elif output_format == "xarray":
        generate_files = False
    else:
        raise ValueError(
            f"output_format must be one of either 'geotiff' or 'xarray'. Provided value: {output_format}"
        )

    # Process data
    print(f"    Generating odc-stac query for {scene}")

    # Construct query
    bbox_query = BoundingBox(
        left=scene_metadata.center_lon - 5,
        bottom=scene_metadata.center_lat - 3,
        right=scene_metadata.center_lon + 5,
        top=scene_metadata.center_lat + 3,
        crs="EPSG:4326",
    ).boundary()
    datetime_query = f"{scene_metadata.start_time}/{scene_metadata.stop_time}"
    filter_query = {
        "op": "=",
        "args": [{"property": "sarard:scene_id"}, scene_metadata.name],
    }

    # Find items
    print("    Querying DEA STAC for bursts")
    bursts_for_scene = stac_client.search(
        collections=collections_query,
        datetime=datetime_query,
        intersects=bbox_query,
        filter=filter_query,
    ).item_collection()

    if len(bursts_for_scene) == 0:
        raise RuntimeError(
            f"No bursts were found for {scene}. This scene is not available as part of our current collection {collection} data offering. Try the other collection."
        )
    else:
        print(f"        Found {len(bursts_for_scene)} bursts for scene")

    # Loading scene
    print(f"    Loading scene using odc-stac")

    ds = load(
        items=bursts_for_scene,
        bands=bands_query,
        crs="EPSG:3031",
        resolution=20,
        groupby="sarard:scene_id",
    ).squeeze()

    # Drop the nlooks band from the list of bands to process
    bands_query.remove(nlooks_band)

    # Applying speckle filtering
    if speckle_filter:
        print(f"    Applying speckle filter")
        for band in bands_query:
            ds[band] = lee_filter_xr(ds[band], ds[nlooks_band], size=3)

    # Convert to db
    if db:
        print(f"    Converting to decibels")
        for band in bands_query:
            ds[band] = 10 * np.log10(ds[band])

    if output_format == "xarray":
        return ds
    elif output_format == "geotiff":
        band_files = zip(bands_query, output_files)
        for band, file in band_files:
            print(f"    Writing to file: {file}")
            ds[band].odc.write_cog(file, overwrite=True)
