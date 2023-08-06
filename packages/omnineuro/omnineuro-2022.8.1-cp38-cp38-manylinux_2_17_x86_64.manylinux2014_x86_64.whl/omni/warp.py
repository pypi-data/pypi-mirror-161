import tempfile
import numpy as np
import nibabel as nib
from omni.interfaces.common import run_process
from omni.interfaces.afni import NwarpCat
from memori.pathman import PathManager

# warp types
CHOICES = ["afni", "fsl"]


def convert_warp(
    in_warp: nib.Nifti1Image,
    in_warp_type: str,
    out_warp_type: str,
    invert: bool,
    target: nib.Nifti1Image,
) -> nib.Nifti1Image:
    """Convert a warp from one type to another.

    Parameters
    ----------
    in_warp : nib.Nifti1Image
        The input warp.
    in_warp_type : str
        The type of the input warp.
    out_warp_type : str
        The type of the output warp.
    invert : bool
        Whether to invert the warp.
    target : nib.Nifti1Image
        The target image.

    Returns
    -------
    nib.Nifti1Image
        The output warp.
    """
    # set warp variables
    afni_warp = None
    fsl_warp = None

    # call appropriate functions based on the warp type
    if in_warp_type == "afni":
        if out_warp_type == "afni":
            afni_warp = in_warp
        elif out_warp_type == "fsl":
            fsl_warp = convert_warp_afni_to_fsl(in_warp)
        else:
            raise ValueError(f"Unknown warp type: {out_warp_type}")
    elif in_warp_type == "fsl":
        if out_warp_type == "afni":
            afni_warp = convert_warp_fsl_to_afni(in_warp, target)
        elif out_warp_type == "fsl":
            fsl_warp = in_warp
        else:
            raise ValueError(f"Unknown warp type: {out_warp_type}")
    else:
        raise ValueError(f"Unknown warp type: {in_warp_type}")

    # check return (invert if set)
    if afni_warp is not None:
        if invert:
            afni_warp = invert_afni_warp(afni_warp)
        return afni_warp
    elif fsl_warp is not None:
        if invert:
            fsl_warp = invert_fsl_warp(fsl_warp)
        return fsl_warp


def convert_warp_afni_to_fsl(in_warp: nib.Nifti1Image) -> nib.Nifti1Image:
    """Convert an AFNI warp to FSL warp.

    Parameters
    ----------
    in_warp : nib.Nifti1Image
        The input warp.

    Returns
    -------
    nib.Nifti1Image
        The output warp.
    """
    # get the data and eliminate the 4th dimension
    data = np.squeeze(in_warp.get_fdata())

    # flip y axis
    data[:, :, :, 1] = -data[:, :, :, 1]

    # construct the fsl warp and return it
    warp = nib.Nifti1Image(data, in_warp.affine)
    warp.header.set_intent("vector")
    return warp


def convert_warp_fsl_to_afni(in_warp: nib.Nifti1Image, target: nib.Nifti1Image) -> nib.Nifti1Image:
    """Convert an FSL warp to AFNI warp.

    Parameters
    ----------
    in_warp : nib.Nifti1Image
        The input warp.
    target : nib.Nifti1Image
        The target image.

    Returns
    -------
    nib.Nifti1Image
        The output warp.
    """
    # save the warp to a temp directory
    with tempfile.TemporaryDirectory() as d:
        # write the warp to a file
        warp_file = PathManager(d) / "warp.nii.gz"
        in_warp.to_filename(warp_file)

        # write the target to a file
        target_file = PathManager(d) / "target.nii.gz"
        target.to_filename(target_file)

        # convert the warp to a relative warp
        out_warp_file = PathManager(d) / "out_warp.nii.gz"
        run_process(f"convertwarp --ref={target_file} --warp1={warp_file} --out={out_warp_file} --rel --relout -v")

        # load the output warp
        out_warp = nib.load(out_warp_file)

        # cache the data
        out_warp.get_fdata()
        assert out_warp.in_memory, "Warp failed to cache!"

    # get the data
    data = out_warp.get_fdata()[:, :, :, np.newaxis, :]

    # flip y axis
    data[:, :, :, :, 1] = -data[:, :, :, :, 1]

    # construct the afni warp and return it
    warp = nib.Nifti1Image(data, target.affine)
    warp.header.set_intent("vector")
    return warp


def invert_fsl_warp(in_warp: nib.Nifti1Image) -> nib.Nifti1Image:
    """Invert an FSL warp.

    Parameters
    ----------
    in_warp : nib.Nifti1Image
        The input warp.

    Returns
    -------
    nib.Nifti1Image
        The output warp (inverted).
    """
    # make temp directory
    with tempfile.TemporaryDirectory() as d:
        # write the warp to a file
        warp_file = PathManager(d) / "warp.nii.gz"
        in_warp.to_filename(warp_file)

        # invert the warp
        out_warp_file = PathManager(d) / "out_warp.nii.gz"
        run_process(f"invwarp --ref={warp_file} --warp={warp_file} --out={out_warp_file} --rel -v")

        # load the output warp
        out_warp = nib.load(out_warp_file)

        # set the intent code
        out_warp.header.set_intent("vector")

        # cache the data
        out_warp.get_fdata()
        assert out_warp.in_memory, "Warp failed to cache!"

    # return the inverted warp
    return out_warp


def invert_afni_warp(in_warp: nib.Nifti1Image) -> nib.Nifti1Image:
    """Invert an AFNI warp.

    Parameters
    ----------
    in_warp : nib.Nifti1Image
        The input warp.

    Returns
    -------
    nib.Nifti1Image
        The output warp (inverted).
    """
    # make temp directory
    with tempfile.TemporaryDirectory() as d:
        # write the warp to a file
        warp_file = PathManager(d) / "warp.nii.gz"
        in_warp.to_filename(warp_file)

        # invert the warp
        out_warp_file = PathManager(d) / "out_warp.nii.gz"
        NwarpCat(out_warp_file, warp_file, True)

        # load the output warp
        out_warp = nib.load(out_warp_file)

        # set the intent code
        out_warp.header.set_intent("vector")

        # cache the data
        out_warp.get_fdata()
        assert out_warp.in_memory, "Warp failed to cache!"

    # return the inverted warp
    return out_warp
