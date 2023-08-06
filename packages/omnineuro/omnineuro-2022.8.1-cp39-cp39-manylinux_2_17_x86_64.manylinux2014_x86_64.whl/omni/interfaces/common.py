import os
import subprocess
import tempfile
import logging
import nibabel as nib
import numpy as np

# Set test mode flag
TEST_MODE = False


def run_process(process_string: str, stdout: bool = True) -> str:
    """Runs an outside terminal process.

    Parameters
    ----------
    process_string: str
        A string containing a valid terminal command to run.
    stdout: bool
        Indicates whether the process string should be directed to
        stdout through the logging module.

    Returns
    -------
    str
        The formatted process_string.
    """
    # try running process, raising exception on error
    try:
        if stdout:  # output to stdout
            logging.info(process_string)
        if not TEST_MODE:  # if in test mode, we don't actually run the process
            subprocess.run(process_string, stdout=stdout, check=True, shell=True)
    except subprocess.CalledProcessError as exception:
        logging.info("Error in subprocess call: %s \n %s", exception.cmd, exception.output)
        raise exception

    # return the formatted process call
    return process_string


def create_fov_masks(
    ref_img: str, source_img: str, affine: str, ref_mask_path: str = None, source_mask_path: str = None
):
    """Creates FOV masks for reference/source images.

    This function generates FOV masks, defining the
    extents of the reference and source images provided.

    Parameters
    ----------
    ref_img: str
        Path to reference image.
    source_img: str
        Path to source image.
    affine: str
        Affine transform (afni).
    ref_mask_path: str
        Path to output reference mask. If None it will create a mask with
        a random name in the /tmp folder.
    source_mask_path: str
        Path to output source mask. If None it will create a mask with a
        random name in the /tmp folder.

    Returns
    -------
    str
        Path to output reference mask.
    str
        Path to output source mask.
    """
    # make temp mask name for source file
    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as orig_source_mask:
        # create random prefix for saving mask files
        ref_mask_file = ref_mask_path if ref_mask_path else tempfile.NamedTemporaryFile(suffix=".nii.gz").name
        source_mask_file = source_mask_path if source_mask_path else tempfile.NamedTemporaryFile(suffix=".nii.gz").name
        orig_source_mask_file = orig_source_mask.name

        # make ref mask
        ref = nib.load(ref_img)
        ref_mask = np.ones(ref.shape)
        nib.Nifti1Image(ref_mask, ref.affine, ref.header).to_filename(ref_mask_file)

        # make source mask
        source = nib.load(source_img)
        source_mask = np.ones(source.shape)
        nib.Nifti1Image(source_mask, source.affine, source.header).to_filename(orig_source_mask_file)
        run_process(
            "3dAllineate -master {} -input {} -prefix {} "
            "-1Dmatrix_apply {} -final NN -overwrite".format(
                ref_mask_file, orig_source_mask_file, source_mask_file, affine
            )
        )

    # return masks
    return ref_mask_file, source_mask_file


def get_prefix(filename: str) -> str:
    """A convenient function for getting the filename without extension.

    Parameters
    ----------
    filename: str
        Name of file to get the prefix.

    Returns
    -------
    str
        prefix of file.
    """
    # strip filename extension
    name, ext = os.path.splitext(os.path.basename(filename))
    if ext != "":
        return get_prefix(name)
    # return the prefix
    return name


def get_path_and_prefix(filename: str) -> str:
    """Gets prefix but leaves in the path.

    Parameters
    ----------
    filename: str
        Name of file to get the prefix and path.

    Returns
    -------
    str
        prefix of file with path.
    """
    # get directory
    dirname = os.path.dirname(filename)

    # get the prefix
    prefix = get_prefix(filename)

    # return directory + prefix
    return os.path.join(dirname, prefix)


def append_suffix(filename: str, suffix: str) -> str:
    """Appends a suffix to a given filename.

    Parameters
    ----------
    filename: str
        Name of file to get the prefix and path.
    suffix: str
        Suffix to add to filename

    Returns
    -------
    str
        Name of file with suffix
    """
    # get prefix
    prefix = get_path_and_prefix(filename)

    # get the extension
    ext = filename[len(prefix) :]

    # return filename with suffix
    return prefix + suffix + ext


def replace_suffix(filename: str, suffix: str) -> str:
    """Replaces the last suffix in the given filename.

    Parameters
    ----------
    filename: str
        Name of file to get the prefix and path.
    suffix: str
        Suffix to replace in the filename

    Returns
    -------
    str
        Name of file with new suffix
    """
    # get prefix
    prefix = get_path_and_prefix(filename)

    # get the extension
    ext = filename[len(prefix) :]

    # remove last suffix in prefix
    prefix = "_".join(prefix.split("_")[:-1])

    # return filename with suffix
    return prefix + suffix + ext


def repath(dirname: str, filename: str) -> str:
    """Changes the directory of a given filename.

    Parameters
    ----------
    dirname: str
        Directory name to use.
    filename: str
        Filename whose path to change.

    Returns
    -------
    str
        Filename with changed path.
    """
    return os.path.join(dirname, os.path.basename(filename))


def normalize(data: np.ndarray) -> np.ndarray:
    """Normalize an array.

    Parameters
    ----------
    data: np.ndarray
        Data to 0/1 normalize.

    Returns
    -------
    np.ndarray
        Normalized data.
    """
    # check if data min max is the same and skip if it is
    if data.ravel().max() == data.ravel().min():
        return data
    return (data - data.ravel().min()) / (data.ravel().max() - data.ravel().min())
