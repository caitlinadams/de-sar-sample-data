import numpy as np
from scipy.ndimage import uniform_filter
import xarray as xr


# Adapted from https://stackoverflow.com/questions/39785970/speckle-lee-filter-in-python
# Made NaN aware following https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/PIRODDI1/NormConv/NormConv.html
def lee_filter(img, size=3):
    """
    Applies the Lee filter to reduce speckle noise in an image.
    This function is NaN-aware and optimised by using uniform_filter from scipy.ndimage.

    The Lee filter is:
    img_lee_applied =  img_uniform_filter + weights * (img - img_uniform_filter)

    where
    - img_uniform_filter = scipy.ndimage.uniform_filter(img)
    - weights = img_filter_variance / (img_filter_variance + img_reference_variance)
    - img_filter_variance = scipy.ndimage.uniform_filter(img**2) - img_uniform_filter**2
    - img_reference_variance = np.nanvar(img)

    The principle of Normalised Convolution is used to make the function nan-aware.
    The basic principles are as follows:
    1. Create a certainty map, which is 0 if the image value is nan and 1 if the image value is valid
    2. Apply the uniform filter to the certainty map, creating a filtered certainty map
    3. Create a zeroed image, replacing any nans with 0
    4. Apply the uniform filter to the zeroed image, creating a filtered zeroed image
    5. Apply the uniform filter to the squared zeroed image, creating a filtered squared zeroed image
    6. Normalise the filtered zero image and squared filtered zero image by the filtered certainty map
    7. Compute other terms using the filtered zero image and squared filtered zero image
    8. Apply a mask to replace any values that were converted from nan to 0 in step 3 back to nan

    Parameters:
    img (ndarray): Input image to be filtered.
    size (int): Size of the uniform filter window.

    Returns:
    ndarray: The filtered image.
    """

    # 1: Create the certainty map, which is 0 if NaN, 1 if valid
    img_certainty_map = ~np.isnan(img)

    # 2: Apply the uniform filter to the certainty map
    mean_img_certainty_map = uniform_filter(img_certainty_map.astype(float), size=size)

    # 3: Replace all NaNs in the image with 0
    img_zero = np.where(img_certainty_map, img, 0.0)

    # 4, 5, 6: Apply uniform filter to zeroed image, squared zeroed image and zeroed nlooks image, and normalise by filtered certainty map
    with np.errstate(invalid="ignore", divide="ignore"):
        img_zero_mean = uniform_filter(img_zero, size=size) / mean_img_certainty_map
        img_zero_sq_mean = (
            uniform_filter(img_zero**2, size=size) / mean_img_certainty_map
        )

    # 7a: Calculate variance on filtered pixels
    img_zero_variance = np.clip(img_zero_sq_mean - img_zero_mean**2, 0, None)

    # 7b: Calculate the reference variance from the image
    img_reference_variance = np.nanvar(img)

    # 7c: Calculate the weights term for the Lee filter
    img_weights = img_zero_variance / (img_zero_variance + img_reference_variance)

    # 7d: Calculate the result of Lee filter
    img_zero_lee_filtered = img_zero_mean + img_weights * (img_zero - img_zero_mean)

    # 8: Replace any elements that were originally NaN with NaN
    img_lee_filtered = np.where(
        img_certainty_map & (mean_img_certainty_map > 0),
        img_zero_lee_filtered,
        np.nan,
    )

    return img_lee_filtered


# Define a function to apply the Lee filter to a DataArray
def lee_filter_xr(da_backscatter: xr.DataArray, size=7):
    """
    Applies the Lee filter to the provided DataArray.

    Parameters:
    da (xarray.DataArray): The data array to be filtered.
    size (int): Size of the uniform filter window. Default is 7.

    Returns:
    xarray.DataArray: The filtered data array.
    """

    filtered_data = xr.apply_ufunc(
        lee_filter,
        da_backscatter,
        input_core_dims=[["y", "x"]],
        output_core_dims=[["y", "x"]],
        vectorize=True,
        dask="parallelized",
        output_dtypes=[da_backscatter.dtype],
        dask_gufunc_kwargs={"allow_rechunk": True},
        kwargs={"size": size},
    )

    return filtered_data
