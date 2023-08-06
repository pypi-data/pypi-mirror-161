import os
import shutil
import logging
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import nibabel as nib
from memori.helpers import create_output_path
from memori.pathman import append_suffix, repath, replace_suffix
from omni.interfaces.common import normalize
from omni.interfaces.fsl import bet


@create_output_path
def brain_extraction(
    output_path: str,
    t1_debias: str = None,
    t2_debias: str = None,
    fractional_intensity_threshold: float = 0.5,
    method: str = "Norm",
    use_eye_mask: bool = True,
):
    """Brain extraction

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    t1_debias : str
        T1 image.
    t2_debias : str
        T2 image.
    fractional_intensity_threshold : float
        Fractional intensity threshold for bet.
    method : str
        Method for brain extraction (T1/Norm).
    use_eye_mask : bool
        Use eye mask for anatomical mask.

    Returns
    -------
    str
        Eye mask.
    str
        Anatomical mask.
    str
        Brain extracted T1 debiased.
    str
        Brain extracted T2 debiased.
    """
    # ensure a t1/t2 is defined
    if not (t1_debias or t2_debias):
        raise ValueError("A t1/t2 input is required.")

    with ProcessPoolExecutor(max_workers=2) as executor:
        # generate eye mask if enabled
        if use_eye_mask:
            # generate tmp directory for eye mask data
            eye_path = os.path.join(output_path, "eye")
            os.makedirs(eye_path, exist_ok=True)

            # Run bet for eye mask
            t1_eye_bet = append_suffix(repath(eye_path, t1_debias), "_bet")
            logging.info("Extracting eye mask...")
            anat_eye_mask_future = executor.submit(
                bet, t1_eye_bet, t1_debias, fractional_intensity_threshold, mask=True, eye=True
            )

        # run bet based on method selected
        logging.info("Running brain extraction...")
        anat_bet = os.path.join(output_path, "anat_bet.nii.gz")
        if method == "Norm":
            # load debiased images
            t1_debias_img = nib.load(t1_debias)
            t2_debias_img = nib.load(t2_debias)

            # get L2 norm sum of T1/T2
            norm_anat = os.path.join(output_path, "norm_anat.nii.gz")
            nib.Nifti1Image(
                10000 * np.sqrt(normalize(t1_debias_img.get_fdata()) + normalize(t2_debias_img.get_fdata())),
                t1_debias_img.affine,
                t1_debias_img.header,
            ).to_filename(norm_anat)

            # run bet on norm image
            anat_bet_future = executor.submit(
                bet, anat_bet, norm_anat, fractional_intensity_threshold, mask=True, neck=True
            )

        elif method == "T1":
            # run bet on T1 image
            anat_bet_future = executor.submit(
                bet, anat_bet, t1_debias, fractional_intensity_threshold, mask=True, neck=True
            )
        else:
            raise ValueError("Invalid method: %s selected." % method)

        # get futures
        logging.info("Waiting for bet call(s) to finish...")
        if use_eye_mask:  # await eye mask results
            _, _, anat_eye_mask = anat_eye_mask_future.result()
            # move eye mask to output path and delete temp eye directory
            if os.path.exists(repath(output_path, anat_eye_mask)):
                os.remove(repath(output_path, anat_eye_mask))
            shutil.move(anat_eye_mask, output_path)
            shutil.rmtree(eye_path)
            anat_eye_mask = repath(output_path, anat_eye_mask)
            shutil.move(anat_eye_mask, replace_suffix(anat_bet, "_eye_mask"))
            anat_eye_mask = replace_suffix(anat_bet, "_eye_mask")
        else:  # generate a non-mask if use_eye_mask disabled
            anat_eye_mask = replace_suffix(anat_bet, "_eye_mask")
            if t1_debias:
                img = nib.load(t1_debias)
            elif t2_debias:
                img = nib.load(t2_debias)
            # create zero array
            zeros_data = np.zeros(img.shape, dtype="f4")
            # save fake eye mask
            nib.Nifti1Image(zeros_data, img.affine, img.header).to_filename(anat_eye_mask)

        # await bet results
        _, anat_bet_mask = anat_bet_future.result()
        os.remove(anat_bet)  # remove anat_bet.nii.gz
        logging.info("bet call(s) done!")

    # generate a function for applying masks
    def apply_mask(out_file, img, mask):
        return nib.Nifti1Image(
            nib.load(img).get_fdata() * nib.load(mask).get_fdata(), nib.load(img).affine, nib.load(img).header
        ).to_filename(out_file)

    # apply mask to anatomical data
    t1_debias_bet = append_suffix(repath(output_path, t1_debias), "_bet")
    apply_mask(t1_debias_bet, t1_debias, anat_bet_mask)
    t2_debias_bet = append_suffix(repath(output_path, t2_debias), "_bet")
    apply_mask(t2_debias_bet, t2_debias, anat_bet_mask)

    # return files
    return (anat_bet_mask, anat_eye_mask, t1_debias_bet, t2_debias_bet)
