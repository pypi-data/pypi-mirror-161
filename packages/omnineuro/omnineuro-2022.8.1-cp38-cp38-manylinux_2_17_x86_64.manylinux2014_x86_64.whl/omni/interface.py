"""Python/C++ Interface for Omni.

    This file contains the python side wrapper for the
    underlying C++ code.
"""
import os
import sys
import warnings
from typing import List
import numpy as np
import nibabel as nib

# first try loading the development library if available
try:
    # get the top level directory
    PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
    # if the build folder exists, add to path
    if "build" in os.listdir(PARENT_DIR):
        sys.path.insert(0, os.path.join(PARENT_DIR, "build"))
    else:
        raise ImportError
    # import the omni C++ module from build
    from omni_lib import omni

    print("omni C++ module loaded from development build!")
except ImportError as e:
    # try to load the omni C++ modules
    try:
        from omni_cpp import omni
    except ImportError:
        warnings.warn("omni C++ modules not found. This may be intentional or the omni install has failed.")


class OmniInterface:
    """Wrapper for interface object.

    Does python level preprocessing before hand over
    to the C++ backend.

    Methods
    -------
    set_img:
        Sets an image to pass into the C++ interface.
    get_img:
        Gets an image from the C++ interface.
    """

    def __init__(self, *args, **kwargs):
        """Initialize interface."""
        # initialize and store reference to interface object
        self._interface = omni.Interface(*args, **kwargs)

    @property
    def link(self):
        """Returns the _interface object for direct access."""
        return self._interface

    @link.setter
    def link(self, x):
        pass

    def set_img(self, name: str, image: nib.Nifti1Image) -> None:
        """Stores a Nifti1Image in omnireg database at "name".

        Parameters
        ----------
        name: str
            Key to save the image at in C++ interface table.
        image: nib.Nifti1Image
            Image to save.
        """
        # check if image is a Nifti1Image
        assert isinstance(image, nib.Nifti1Image), "image is not a Nifti1Image"

        # get data (squeeze out any singleton dims)
        data = np.squeeze(image.get_fdata())

        # check dim size, throw error if >3
        assert len(data.shape) == 3, "omni does not yet support non-3D images!"

        # store in database
        self._interface.set_img(name, np.squeeze(image.get_fdata()), image.affine)

    def get_img(
        self, name: str, affine: np.ndarray = None, ref: nib.Nifti1Image = None, clip: List[float] = None
    ) -> nib.Nifti1Image:
        """Returns a Nifti1Image from the array stored at "name".

        Uses default nibabel image header information if affine/header
        is not defined. The ref variable can also be used to specify the
        image header information.

        Parameters
        ----------
        name: str
            Key for image to get from C++ interface table.
        affine: np.ndarray
            Affine to use for returned image.
        ref: nib.Nifti1Image
            Reference image to use for header of returned image.
        clip: List[float]
            Clipping limits to apply to image data.

        Returns
        -------
        nib.Nifti1Image
            Return image represented by key from C++ interface.
        """
        # get the array data
        array = self._interface.return_array(name)

        # clip array
        if clip:
            array = np.clip(array, clip[0], clip[1])

        # check method inputs
        if affine is not None and ref is not None:
            raise ValueError("Ambiguous Input: affine/ref should " "not all be defined at the same time.")
        elif ref is not None:
            # check inputs
            assert isinstance(ref, nib.Nifti1Image), "ref type is not Nifti1Image"

            # return image
            return nib.Nifti1Image(array, ref.affine, ref.header)
        elif affine is not None:
            # check inputs
            assert isinstance(affine, np.ndarray), "affine not a numpy array"
            assert affine.shape == (4, 4), "affine shape not (4,4)"

            # return image
            return nib.Nifti1Image(array, affine)
        else:
            # return defaults with image
            return nib.Nifti1Image(array, np.eye(4))
