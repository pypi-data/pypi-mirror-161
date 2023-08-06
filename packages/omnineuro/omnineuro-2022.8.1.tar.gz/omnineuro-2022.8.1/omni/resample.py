"""Image resampling function.
"""
import numpy as np
import nibabel as nib
from .interface import OmniInterface


def resample(target: nib.Nifti1Image, source: nib.Nifti1Image, affine: np.ndarray) -> nib.Nifti1Image:
    """Resamples an image to target image space.

    Resamples image from source to target image space. An
    optional affine can be given to also transform the image.

    Parameters
    ----------
    target: nib.Nifti1Image
        Target image to resample to.
    source: nib.Nifti1Image
        Source image to transform.
    affine: np.ndarray
        Affine matrix to transform source to target.

    Returns
    -------
    nib.Nifti1Image
        Resampled/transformed source image.
    """
    # setup interface
    oi = OmniInterface()
    oi.set_img("target", target)
    oi.set_img("source", source)

    # resample the image
    oi.link.resample("target", "source", "output", affine)

    # return output array (using header information of target)
    output_img = oi.get_img("output", ref=target)

    # return output image
    return output_img
