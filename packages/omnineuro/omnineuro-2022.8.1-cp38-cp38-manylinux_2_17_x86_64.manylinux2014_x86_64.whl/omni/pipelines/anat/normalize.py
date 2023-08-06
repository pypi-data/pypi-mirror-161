import logging
from concurrent.futures import ProcessPoolExecutor
import nibabel as nib
from memori.pathman import replace_suffix, repath
from memori.helpers import create_output_path
from omni.interfaces.common import normalize
from omni.interfaces.ants import N4BiasFieldCorrection


@create_output_path
def debias(output_path: str, t1_do: str, t2_do: str, spline_fit: str = "[100,3,1x1x1,3]"):
    """Bias field correction of anatomical images.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    t1_do : str
        Deobliqued T1 image.
    t2_do : str
        Deobliqued T2 image.
    spline_fit : str
        Custom spline fitting string.

    Returns
    -------
    str
        Bias field corrected/Normalized T1.
    str
        Bias field corrected/Normalized T2.
    """
    # normalize images
    logging.info("Normalizing images...")
    t1_nm = replace_suffix(repath(output_path, t1_do), "_nm")
    t2_nm = replace_suffix(repath(output_path, t2_do), "_nm")
    nib.Nifti1Image(
        10000 * normalize(nib.load(t1_do).get_fdata()), nib.load(t1_do).affine, nib.load(t1_do).header
    ).to_filename(t1_nm)
    nib.Nifti1Image(
        10000 * normalize(nib.load(t2_do).get_fdata()), nib.load(t2_do).affine, nib.load(t2_do).header
    ).to_filename(t2_nm)

    # Bias correct anatomical images
    logging.info("Bias field correcting anatomical images...")
    t1_debias = replace_suffix(t1_nm, "_debias")
    t2_debias = replace_suffix(t2_nm, "_debias")
    with ProcessPoolExecutor(max_workers=2) as executor:
        # bias correct t1 and t2
        future_t1 = executor.submit(N4BiasFieldCorrection, t1_debias, t1_nm, spline_fit)
        future_t2 = executor.submit(N4BiasFieldCorrection, t2_debias, t2_nm, spline_fit)

        # wait for jobs to finish
        logging.info("Waiting for bias correction...")
        future_t1.result()
        logging.info("T1 is Done!")
        future_t2.result()
        logging.info("T2 is Done!")

    # return images
    return (t1_debias, t2_debias)
