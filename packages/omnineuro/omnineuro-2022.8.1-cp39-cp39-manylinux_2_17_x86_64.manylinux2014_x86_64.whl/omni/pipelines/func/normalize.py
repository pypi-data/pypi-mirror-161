import logging
import nibabel as nib
from memori.pathman import append_suffix, replace_suffix, repath
from memori.helpers import create_output_path
from omni.interfaces.common import normalize
from omni.interfaces.ants import N4BiasFieldCorrection


@create_output_path
def debias(output_path: str, ref_func: str, spline_fit: str = "[200,3,1x1x1,3]"):
    """Bias field correction of anatomical images.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    ref_func : str
        Reference functional
    spline_fit : str
        Custom spline fitting string.

    Returns
    -------
    str
        Bias field corrected/Normalized functional.
    """
    # normalize images
    logging.info("Normalizing functional...")
    ref_func_nm = append_suffix(repath(output_path, ref_func), "_nm")
    nib.Nifti1Image(
        10000 * normalize(nib.load(ref_func).get_fdata()), nib.load(ref_func).affine, nib.load(ref_func).header
    ).to_filename(ref_func_nm)

    # Bias correct functional
    logging.info("Bias field correcting anatomical images...")
    ref_func_debias = replace_suffix(ref_func_nm, "_debias")
    N4BiasFieldCorrection(ref_func_debias, ref_func_nm, spline_fit)

    # return images
    return ref_func_debias
