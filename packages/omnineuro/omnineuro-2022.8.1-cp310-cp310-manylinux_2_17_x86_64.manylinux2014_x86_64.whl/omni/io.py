"""Read/write functions for various omni outputs.
"""
import os
from typing import Tuple
import numpy as np
import nibabel as nib
from .affine import convert_affine, afni_affine_to_rigid_body


def load_target_source(target: str, source: str) -> Tuple[nib.Nifti1Image, nib.Nifti1Image]:
    """Conveinence function for loading two images (target/source)."""
    t = nib.load(target)
    s = nib.load(source)
    return t, s


def load_interaction_spec(model: str) -> str:
    """Parse the interaction model input."""
    # read in the *.model file if defined
    if ".model" in model:
        with open(model, "r") as f:
            spec = "".join([line.rstrip() for line in f.readlines()])
    else:  # else just return the model as text
        spec = model
    return spec


def read_omni_affine(filename: str) -> np.ndarray:
    """Read omni format affine matrix from disk."""
    # load affine data
    with open(filename, "r") as f:
        data = np.loadtxt(f)
    return data


def read_afni_affine(filename: str) -> np.ndarray:
    """Loads the afni affine matrix file."""
    with open(filename, "r") as f:
        lines = f.readlines()
    # remove comments from read lines
    lines = [i for i in lines if "#" not in i]

    # there should only be one entry in the lines now (make assertion check)
    assert (
        len(lines) == 1
    ), "There was an error in parsing the afni affine \
        file. Tell Andrew that his parsing logic was wrong :("

    # grab the first entry in lines for the affine matrix
    lines = [float(i) for i in lines[0].rstrip().split(" ") if i != ""] + [0, 0, 0, 1]

    # return matrix
    return np.array(lines).reshape(4, 4)


def read_afni_framewise_affine(filename: str) -> np.ndarray:
    """Loads in a framewise affine from afni

    Parameters
    ----------
    filename: str
        Multi frame affine file to load.

    Returns
    -------
    np.ndarray
        n x 16 array of affines
    """
    with open(filename, "r") as f:
        lines = f.readlines()

    # remove comments from read lines
    lines = [i for i in lines if "#" not in i]

    # format string to floats
    lines = [[float(i) for i in line.rstrip().split(" ") if i != ""] + [0, 0, 0, 1] for line in lines]

    # return affine list
    return np.array(lines)


def convert_framewise_affine_to_rigid_body(output: str, filename: str) -> None:
    """Converts framewise affine file to rigid body.

    Parameters
    ----------
    output: str
        Path/name of output rigid body parames file.
    filename: str
        Affine file to convert.
    """
    # read in file
    affines = read_afni_framewise_affine(filename)

    # convert to rigid body params
    rigid_body_params = afni_affine_to_rigid_body(affines)

    # write the rigid body params to file
    np.savetxt(
        output,
        rigid_body_params,
        fmt="%.6f",
        header="3dAllineate parameters:\nx-shift  y-shift  z-shift  z-angle  x-angle  y-angle",
    )


def read_affine_file(filename: str) -> Tuple[np.ndarray, str]:
    """Loads affine file from disk.

    Parameters
    ----------
    filename: str
        Affine filename to load.

    Returns
    -------
    np.ndarray
        4x4 affine matrix.
    str
        Type of affine file loaded (omni/afni/fsl).
    """
    # check extension of file to use appropriate loader
    _, ext = os.path.splitext(filename)
    if ext == ".affine":  # omni
        return read_omni_affine(filename), "omni"
    elif ext == ".1D":  # afni
        return read_afni_affine(filename), "afni"
    elif ext == ".mat":  # fsl (file format is same as omni)
        return read_omni_affine(filename), "fsl"
    else:  # Unknown extension
        raise ValueError("Unknown extension")


def write_omni_affine(filename: str, affine_mat: np.ndarray) -> None:
    """Writes omni format affine matrix to disk."""
    # add extension if not exist
    _, ext = os.path.splitext(filename)
    if ext != ".affine":
        filename += ".affine"

    # write data to file
    with open(filename, "w") as f:
        np.savetxt(f, affine_mat)


def write_afni_affine(filename: str, affine_mat: np.ndarray) -> None:
    """Writes an afni affine matrix file to disk."""
    # grab extension
    def get_ext(x):
        return "".join(
            [get_ext(os.path.splitext(x)[0]) if os.path.splitext(x)[1] != "" else "", os.path.splitext(x)[1]]
        )

    # add extension if not exist
    ext = get_ext(filename)
    if ext != ".aff12.1D":
        filename += ".aff12.1D"

    # write data
    with open(filename, "w") as f:
        f.write("# 3dAllineate matrices (DICOM-to-DICOM, row-by-row):\n")
        f.write("       ")
        for i in affine_mat.ravel()[:12]:
            f.write(str(i))
            f.write("   ")


def write_fsl_affine(filename: str, affine_mat: np.ndarray) -> None:
    """Writes fsl format affine matrix to disk."""
    # add extension if not exist
    _, ext = os.path.splitext(filename)
    if ext != ".mat":
        filename += ".mat"

    # write data to file
    with open(filename, "w") as f:
        np.savetxt(f, affine_mat)


def write_affine_file(filename: str, affine_mat: np.ndarray, atype: str) -> None:
    """Write affine file.

    Parameters
    ----------
    filename: str
        Filename of affine file to write.
    affine_mat: np.ndarray
        4x4 affine matrix.
    atype: str
        Type of affine file to write (omni/afni/fsl).
    """
    # call appropriate file writer
    if atype == "omni":  # omni
        write_omni_affine(filename, affine_mat)
    elif atype == "afni":  # afni
        write_afni_affine(filename, affine_mat)
    elif atype == "fsl":  # fsl
        write_fsl_affine(filename, affine_mat)
    else:  # Unknown extension
        raise ValueError("Unknown affine type: {}".format(atype))


def convert_affine_file(
    output: str, filename: str, output_atype: str, invert: bool = False, target: str = None, source: str = None
) -> None:
    """Converts input affine file to output affine file of another type.

    Parameters
    ----------
    output: str
        Path/name of output affine file.
    filename: str
        Affine file to convert.
    output_atype: str
        Type of affine to output (omni/afni/fsl).
    invert: bool
        Controls whether the affine should be inverted.
    target: str
        Path to target image affine is transformed to
        (required for fsl conversion).
    source: str
        Path to source image affine is applying transform to
        (required for fsl conversion).
    """
    # open the affine file to convert
    affine_mat, atype = read_affine_file(filename)

    # load target and source images if defined
    if target and source:
        t = nib.load(target)
        s = nib.load(source)
    else:
        t = None
        s = None

    # convert the affine to output type
    new_affine_mat = convert_affine(affine_mat, atype, output_atype, invert=invert, target=t, source=s)

    # write the new affine to file
    write_affine_file(output, new_affine_mat, output_atype)


def write_regress_params(filename: str, regress_params: np.ndarray) -> None:
    """Writes regression parameters to disk."""
    # add extension if not exist
    _, ext = os.path.splitext(filename)
    if ext != ".regress":
        filename += ".regress"

    # write data to file
    with open(filename, "w") as f:
        np.savetxt(f, regress_params)


def write_rb_params(filename: str, rb_params: np.ndarray) -> None:
    """Writes rigid body params to disk.

    Parameters
    ----------
    filename: str
        Rigid body params file to write.
    rb_params: str
        n x 6 ndarray containing rigid body parameters.
    """
    # add extension if not exist
    _, ext = os.path.splitext(filename)
    if ext != ".params":
        filename += ".params"

    with open(filename, "w") as f:
        np.savetxt(f, rb_params, fmt="%.6f", header="x(mm) y(mm) z(mm) rx(rad) ry(rad) rz(rad)")
