import os
import logging
import nibabel as nib
import numpy as np
from scipy.ndimage import binary_dilation
from memori.pathman import append_suffix, repath
from memori.helpers import create_output_path
from omni.masks import compute_weight_mask
from omni.interfaces.common import normalize
from omni.interfaces.afni import Autobox, resample
from omni.preprocessing import saturate, localized_contrast_enhance


@create_output_path
def weight_mask_and_autobox(
    output_path: str, t1_debias: str, t2_debias: str, anat_bet_mask: str, anat_eye_mask: str, dilation_size: int = 30
):
    """Generate an anatomical weight mask

    Parameters
    ----------
    output_path : str
        Output path to write out files to
    t1_debias : str
        T1 image.
    t2_debias : str
        T2 image.
    anat_bet_mask : str
        Anatomical brain mask
    anat_eye_mask : str
        Anatomical eye mask
    dilation_size : int
        Dilation size for the weight mask

    Returns
    -------
    str
        Weight mask
    str
        Weight mask + autobox
    str
        Brain mask + autobox
    str
        Debiased T1 + autobox
    str
        Debiased T2 + autobox
    str
        Debiased T1 + autobox + sat/lce
    str
        Debiased T2 + autobox + sat/lce
    str
        Debiased T1 + autobox + sat/lce + bet
    str
        Debiased T2 + autobox + sat/lce + bet
    """
    logging.info("Creating anatomical weight mask...")
    logging.info(
        """
        It may look like that this part has hung,
        but it really is just that slow... Blame scipy for having a
        crappy mathematical morphology library..."""
    )

    # load bet masks
    bet_mask_img = nib.load(anat_bet_mask)
    bet_data = bet_mask_img.get_fdata()
    eye_mask_img = nib.load(anat_eye_mask)
    eye_data = eye_mask_img.get_fdata()

    # create structural element for dilation
    strel = np.ones(tuple([dilation_size for _ in range(3)]), dtype=np.bool)

    # create weight mask by adding dilated mask + eye_mask
    weight_mask_data = normalize(
        np.logical_or(binary_dilation(bet_data.astype("?"), strel), eye_data.astype("?")).astype(bet_data.dtype)
        + bet_data
    )

    # save the mask to file
    weight_mask = os.path.join(output_path, "weight_mask.nii.gz")
    nib.Nifti1Image(weight_mask_data, bet_mask_img.affine, bet_mask_img.header).to_filename(weight_mask)

    # autobox the weighted anatomical mask
    logging.info("Creating autobox mask...")
    weight_mask_ab = os.path.join(output_path, "weight_mask_ab.nii.gz")
    Autobox(weight_mask_ab, weight_mask, npad=4)

    # resample each t1/t2 images to autobox grid
    logging.info("Autoboxing images...")
    t1_debias_ab = repath(output_path, append_suffix(t1_debias, "_ab"))
    t2_debias_ab = repath(output_path, append_suffix(t2_debias, "_ab"))
    anat_bet_mask_ab = repath(output_path, append_suffix(anat_bet_mask, "_ab"))
    resample(t1_debias_ab, weight_mask_ab, t1_debias)
    resample(t2_debias_ab, weight_mask_ab, t2_debias)
    resample(anat_bet_mask_ab, weight_mask_ab, anat_bet_mask)

    # saturate and lce each image
    logging.info("Saturate and localize contrast enhance images...")
    t1_debias_ab_sat_lce = append_suffix(t1_debias_ab, "_sat_lce")
    t2_debias_ab_sat_lce = append_suffix(t2_debias_ab, "_sat_lce")
    bet_mask_ab_img = nib.load(anat_bet_mask_ab)
    t1_debias_ab_img = nib.load(t1_debias_ab)
    t2_debias_ab_img = nib.load(t2_debias_ab)
    t1_debias_ab_sat_img = saturate(t1_debias_ab_img)
    t2_debias_ab_sat_img = saturate(t2_debias_ab_img)
    t1_debias_ab_sat_lce_img = localized_contrast_enhance(t1_debias_ab_sat_img, bet_mask_ab_img)
    t2_debias_ab_sat_lce_img = localized_contrast_enhance(t2_debias_ab_sat_img, bet_mask_ab_img)
    t1_debias_ab_sat_lce_img.to_filename(t1_debias_ab_sat_lce)
    t2_debias_ab_sat_lce_img.to_filename(t2_debias_ab_sat_lce)

    # get bet versions of sat/lce images
    t1_debias_ab_sat_lce_bet = append_suffix(t1_debias_ab_sat_lce, "_bet")
    t2_debias_ab_sat_lce_bet = append_suffix(t2_debias_ab_sat_lce, "_bet")
    nib.Nifti1Image(
        t1_debias_ab_sat_lce_img.get_fdata() * bet_mask_ab_img.get_fdata(),
        t1_debias_ab_sat_lce_img.affine,
        t1_debias_ab_sat_lce_img.header,
    ).to_filename(t1_debias_ab_sat_lce_bet)
    nib.Nifti1Image(
        t2_debias_ab_sat_lce_img.get_fdata() * bet_mask_ab_img.get_fdata(),
        t2_debias_ab_sat_lce_img.affine,
        t2_debias_ab_sat_lce_img.header,
    ).to_filename(t2_debias_ab_sat_lce_bet)

    # return masks and images
    return (
        weight_mask,
        weight_mask_ab,
        anat_bet_mask_ab,
        t1_debias_ab,
        t2_debias_ab,
        t1_debias_ab_sat_lce,
        t2_debias_ab_sat_lce,
        t1_debias_ab_sat_lce_bet,
        t2_debias_ab_sat_lce_bet,
    )


@create_output_path
def weight_mask_and_autobox2(
    output_path: str, t1_debias: str, t2_debias: str, anat_bet_mask: str, anat_eye_mask: str, dilation_size: int = 15
):
    """Generate an anatomical weight mask (improved version) and autobox the images.

    Parameters
    ----------
    output_path : str
        Output path to write out files to
    t1_debias : str
        T1 image.
    t2_debias : str
        T2 image.
    anat_bet_mask : str
        Anatomical brain mask
    anat_eye_mask : str
        Anatomical eye mask
    dilation_size : int
        Dilation size for the weight mask

    Returns
    -------
    str
        Weight mask
    str
        Weight mask + autobox
    str
        Brain mask + autobox
    str
        Debiased T1 + autobox
    str
        Debiased T2 + autobox
    str
        Debiased T1 + autobox + sat/lce
    str
        Debiased T2 + autobox + sat/lce
    str
        Debiased T1 + autobox + sat/lce + bet
    str
        Debiased T2 + autobox + sat/lce + bet
    """
    # load bet masks
    bet_mask_img = nib.load(anat_bet_mask)
    eye_mask_img = nib.load(anat_eye_mask)

    # load t1_debias
    t1_debias_img = nib.load(t1_debias)

    # get weight mask
    logging.info("Creating weight mask...")
    weight_mask_img = compute_weight_mask(t1_debias_img, bet_mask_img, eye_mask_img, dilation_size)

    # save the mask to file
    weight_mask = os.path.join(output_path, "weight_mask.nii.gz")
    weight_mask_img.to_filename(weight_mask)

    # autobox the weighted anatomical mask
    logging.info("Creating autobox mask...")
    weight_mask_ab = os.path.join(output_path, "weight_mask_ab.nii.gz")
    Autobox(weight_mask_ab, weight_mask)

    # resample each t1/t2 images to autobox grid
    logging.info("Autoboxing images...")
    t1_debias_ab = repath(output_path, append_suffix(t1_debias, "_ab"))
    t2_debias_ab = repath(output_path, append_suffix(t2_debias, "_ab"))
    anat_bet_mask_ab = repath(output_path, append_suffix(anat_bet_mask, "_ab"))
    resample(t1_debias_ab, weight_mask_ab, t1_debias)
    resample(t2_debias_ab, weight_mask_ab, t2_debias)
    resample(anat_bet_mask_ab, weight_mask_ab, anat_bet_mask)

    # saturate and lce each image
    logging.info("Saturate and localize contrast enhance images...")
    t1_debias_ab_sat_lce = append_suffix(t1_debias_ab, "_sat_lce")
    t2_debias_ab_sat_lce = append_suffix(t2_debias_ab, "_sat_lce")
    bet_mask_ab_img = nib.load(anat_bet_mask_ab)
    t1_debias_ab_img = nib.load(t1_debias_ab)
    t2_debias_ab_img = nib.load(t2_debias_ab)
    t1_debias_ab_sat_img = saturate(t1_debias_ab_img)
    t2_debias_ab_sat_img = saturate(t2_debias_ab_img)
    t1_debias_ab_sat_lce_img = localized_contrast_enhance(t1_debias_ab_sat_img, bet_mask_ab_img)
    t2_debias_ab_sat_lce_img = localized_contrast_enhance(t2_debias_ab_sat_img, bet_mask_ab_img)
    t1_debias_ab_sat_lce_img.to_filename(t1_debias_ab_sat_lce)
    t2_debias_ab_sat_lce_img.to_filename(t2_debias_ab_sat_lce)

    # get bet versions of sat/lce images
    t1_debias_ab_sat_lce_bet = append_suffix(t1_debias_ab_sat_lce, "_bet")
    t2_debias_ab_sat_lce_bet = append_suffix(t2_debias_ab_sat_lce, "_bet")
    nib.Nifti1Image(
        t1_debias_ab_sat_lce_img.get_fdata() * bet_mask_ab_img.get_fdata(),
        t1_debias_ab_sat_lce_img.affine,
        t1_debias_ab_sat_lce_img.header,
    ).to_filename(t1_debias_ab_sat_lce_bet)
    nib.Nifti1Image(
        t2_debias_ab_sat_lce_img.get_fdata() * bet_mask_ab_img.get_fdata(),
        t2_debias_ab_sat_lce_img.affine,
        t2_debias_ab_sat_lce_img.header,
    ).to_filename(t2_debias_ab_sat_lce_bet)

    # return masks and images
    return (
        weight_mask,
        weight_mask_ab,
        anat_bet_mask_ab,
        t1_debias_ab,
        t2_debias_ab,
        t1_debias_ab_sat_lce,
        t2_debias_ab_sat_lce,
        t1_debias_ab_sat_lce_bet,
        t2_debias_ab_sat_lce_bet,
    )
