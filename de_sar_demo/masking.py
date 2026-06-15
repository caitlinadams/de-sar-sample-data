import numpy as np
from skimage.morphology import disk, dilation
import xarray as xr


def dilate_mask(mask: xr.DataArray, dilation_radius: int = 3) -> xr.DataArray:
    """Function to dilate a binary mask using a disk footprint. Values of 1 will be dilated.

    Parameters
    ----------
    mask : xr.DataArray
        The binary mask to dilate, as an xarray.DataArray
    dilation_radius : int, optional
        The radius (in units of pixels) to use for the disk footprint, by default 3

    Returns
    -------
    xr.DataArray
        dilated binary mask
    """
    out = []
    for time in mask["time"].values:
        mask_np_array = mask.sel(time=time).values
        mask_np_array_dilated = dilation(mask_np_array, footprint=disk(dilation_radius))
        out.append(mask_np_array_dilated)

    return xr.DataArray(np.stack(out, axis=0), coords=mask.coords, dims=mask.dims)
