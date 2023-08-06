"""Image preprocessing functions.
"""
import numpy as np
import nibabel as nib
import scipy.stats as stats
from skimage.exposure import equalize_adapthist
from omni.interfaces.common import normalize


def saturate(img: nib.Nifti1Image, n: float = 0.01) -> nib.Nifti1Image:
    """Similar behavior to MATLAB imadjust.

    Saturates bottom/top n of data.

    Parameters
    ----------
    img: nib.Nifti1Image
        Image to saturate.
    n: float
        Percentage (as decimal) of voxels to saturate.

    Returns
    -------
    nib.Nifti1Image
        Saturated image.
    """
    # get image data
    img_data = img.get_fdata()

    # sort data
    sorted_data = np.sort(img_data.ravel())

    # get sorted data size
    img_size = sorted_data.shape[0]

    # get low/high voxel count (we always round up/down for lower/upper bound)
    low_count = int(np.ceil(n * img_size))
    high_count = int(np.floor((1 - n) * img_size))

    # get the image value at low and high counts
    low_value = sorted_data[low_count]
    high_value = sorted_data[high_count]

    # clip the original image by the low/high values
    clipped_data = np.clip(img_data, low_value, high_value)

    # create new image with modified data, but same affine and header
    mod_img = nib.Nifti1Image(clipped_data, img.affine, img.header)

    # return modified image
    return mod_img


def equalize(img: nib.Nifti1Image, precision: int = 4) -> nib.Nifti1Image:
    """Applies histogram equalization to the image.

    Parameters
    ----------
    img: nib.Nifti1Image
        Image to histogram equalize.
    precision: int
        Number of decimal places to estimate historgram bins.

    Returns
    -------
    nib.Nifti1Image
        Historgram equalized image.
    """
    # get image data
    img_data = img.get_fdata()

    # get image shape
    img_shape = img.shape

    # get maximum of data
    max_scale = int(img_data.ravel().max())
    min_scale = int(img_data.ravel().min())

    # set precision by multiplying image
    rnd_data = (img_data.ravel() * (10**precision)).astype("int")
    max_val = max_scale * (10**precision)
    min_val = min_scale * (10**precision)

    # generate pdf
    data_histogram, _ = np.histogram(rnd_data, bins=max_val, range=(min_val, max_val))

    # make histogram equalization map
    data_cdf = np.cumsum(data_histogram)
    cdf_min = data_cdf[np.where(data_cdf > 0)[0].min()]
    voxel_count = rnd_data.shape[0]
    voxel_map = (data_cdf - cdf_min) * (max_val / (voxel_count - 1))
    voxel_map = np.clip(voxel_map, 0, max_val).astype("int")  # ensure > 0 and convert to ints

    # scale the original image for precision
    scaled_data = (img_data * (10**precision)).astype("int").ravel()

    # map values onto voxel map
    equalized_data = (np.take(voxel_map, scaled_data, mode="clip").astype("float") / (10**precision)).reshape(
        img_shape
    )

    # create new image with modified data, but same affine and header
    mod_img = nib.Nifti1Image(equalized_data, img.affine, img.header)

    # return modified image
    return mod_img


def localized_contrast_enhance(img: nib.Nifti1Image, mask: nib.Nifti1Image, nfrac: float = 0.05) -> nib.Nifti1Image:
    """Localized histogram equalization.

    Applies histogram equalization to image, but scales it so that
    the range of values inside the mask are enhanced.

    Parameters
    ----------
    img: nib.Nifti1Image
        Image to contrast enhance.
    mask: nib.Nifti1Image
        Image containing region to constrast enhance.
    nfrac: float
        Fraction of voxels to use inside mask.

    Returns
    -------
    nib.Nifti1Image
        LCE image.
    """
    # get data and flatten
    img_data = (img.get_fdata()).flatten()
    mask_data = (mask.get_fdata() > 0.5).flatten()

    # Get a list of unique values in the data set, sorted in ascending order
    unique_data_vals = np.unique(img_data)

    # A vector that indicates what each value of the
    # input data set is mapped to
    initial_map_values = np.linspace(0, 1, unique_data_vals.size)

    # An initial mapping
    initial_interp_values = np.interp(img_data, unique_data_vals, initial_map_values)

    # Get the interpolated values within the supplied binary mask
    initial_mask_interp_values = initial_interp_values[mask_data]
    initial_mask_interp_values.sort(axis=0)

    # Sort the values in the mask in ascending order

    # Get the N% value in the mask. This is used along with the median
    # mask value to define the 'linear' range of the histogram normalizing
    # curve
    n_frac_value = initial_mask_interp_values[int(np.round(nfrac * initial_mask_interp_values.size))]

    # Get the median value in the mask
    median_value = np.median(initial_mask_interp_values)

    # Get transformed data
    transformed_data = normalize(
        stats.norm.cdf(initial_interp_values, loc=median_value, scale=abs(n_frac_value - median_value))
    )

    # return a new Nifti1Image
    return nib.Nifti1Image(transformed_data.reshape(*img.shape), img.affine, img.header)


def clahe(img: nib.Nifti1Image) -> nib.Nifti1Image:
    """Contrast Limited Adaptive Histogram Equalization

    A simple wrapper around the CLAHE algorithm from skimage.

    Parameters
    ----------
    img: nib.Nifti1Image
        input image

    Returns
    -------
    nib.Nifti1Image
        output image
    """
    return nib.Nifti1Image(
        equalize_adapthist(normalize(img.get_fdata()), kernel_size=img.shape, clip_limit=0.02), img.affine
    )


def normalization(img: nib.Nifti1Image) -> nib.Nifti1Image:
    """Normalizes an image from 0 to 1

    Parameters
    ----------
    img: nib.Nifti1Image
        Image to normalize.

    Returns
    -------
    nib.Nifti1Image
        Normalized image.
    """
    # get image data
    data = img.get_fdata()

    # return normalized image
    return nib.Nifti1Image(normalize(data), img.affine, img.header)
