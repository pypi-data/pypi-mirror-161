import logging
import nibabel as nib
from memori.pathman import append_suffix, repath
from memori.helpers import create_output_path
from omni.interfaces.common import normalize
from omni.interfaces.afni import Autobox, resample


@create_output_path
def autobox_and_normalize(
    output_path: str,
    ref_func_debias: str,
    ref_func_debias_bet: str,
    ref_func_debias_mask: str,
    func_do_moco: str,
    func_do: str,
):
    """Autobox and normalize functional.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    ref_func_debias : str
        Debiased reference functional.
    ref_func_debias_bet : str
        Debiased reference functional brain extracted.
    ref_func_debias_mask : str
        Reference functional brain mask.
    func_do_moco : str
        Motion corrected functional.
    func_do : str
        Deobliqued functional.

    Returns
    -------
    str
        Debiased reference functional + Autobox/Normalized.
    str
        Debiased reference functional brain extracted + Autobox/Normalized.
    str
        Reference functional brain mask + Autobox/Normalized.
    str
        Motion corrected functional + Autobox/Normalized.
    str
        Deobliqued functional + Autobox/Normalized.
    """
    # create autobox names
    ref_func_debias_ab = append_suffix(repath(output_path, ref_func_debias), "_ab")
    ref_func_debias_bet_ab = append_suffix(repath(output_path, ref_func_debias_bet), "_ab")
    ref_func_debias_mask_ab = append_suffix(repath(output_path, ref_func_debias_mask), "_ab")
    func_do_moco_ab = append_suffix(repath(output_path, func_do_moco), "_ab")
    func_do_ab = append_suffix(repath(output_path, func_do), "_ab")

    # autobox the reference functional
    Autobox(ref_func_debias_ab, ref_func_debias, npad=5)
    resample(ref_func_debias_bet_ab, ref_func_debias_ab, ref_func_debias_bet)
    resample(ref_func_debias_mask_ab, ref_func_debias_ab, ref_func_debias_mask)
    resample(func_do_moco_ab, ref_func_debias_ab, func_do_moco)
    resample(func_do_ab, ref_func_debias_ab, func_do)

    # convert mask to closest canonical form
    nib.as_closest_canonical(nib.load(ref_func_debias_mask_ab)).to_filename(ref_func_debias_mask_ab)

    # normalize images
    logging.info("Normalizing functional images...")
    nib.as_closest_canonical(
        nib.Nifti1Image(
            normalize(nib.load(ref_func_debias_ab).get_fdata()),
            nib.load(ref_func_debias_ab).affine,
            nib.load(ref_func_debias_ab).header,
        )
    ).to_filename(ref_func_debias_ab)
    nib.as_closest_canonical(
        nib.Nifti1Image(
            normalize(nib.load(ref_func_debias_bet_ab).get_fdata()),
            nib.load(ref_func_debias_bet_ab).affine,
            nib.load(ref_func_debias_bet_ab).header,
        )
    ).to_filename(ref_func_debias_bet_ab)
    nib.as_closest_canonical(
        nib.Nifti1Image(
            normalize(nib.load(func_do_moco_ab).get_fdata()),
            nib.load(func_do_moco_ab).affine,
            nib.load(func_do_moco_ab).header,
        )
    ).to_filename(func_do_moco_ab)

    # convert func_do_ab to closest canonical form
    nib.as_closest_canonical(nib.load(func_do_ab)).to_filename(func_do_ab)

    # return autoboxed/normalized data
    return (ref_func_debias_ab, ref_func_debias_bet_ab, ref_func_debias_mask_ab, func_do_moco_ab, func_do_ab)
