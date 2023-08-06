import os
import logging
import shutil
from typing import List
import nibabel as nib
import numpy as np
from scipy.stats import zscore
import scipy.signal as ss
from memori.pathman import append_suffix, repath
from memori.helpers import create_output_path
from omni.affine import deoblique
from omni.interfaces.common import run_process
from omni.interfaces.afni import Allineate
from omni.io import write_rb_params
from omni.register import realign4d


# choices for motion correction
moco = ["allineate", "realign4d"]


@create_output_path
def deoblique_func(output_path: str, func: str):
    """Deoblique functional image.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    func : str
        Functional image.

    Returns
    -------
    str
        Functional image deobliqued.
    """
    logging.info("Deobliquing functional image...")

    # deoblique functional
    func_img = nib.load(func)
    func_deoblique_img = deoblique(func_img)

    # write out deobliqued
    func_do = append_suffix(repath(output_path, func), "_deobliqued")
    func_deoblique_img.to_filename(func_do)

    # return deobliqued functional image
    return func_do


@create_output_path
def create_reference_and_moco(
    output_path: str,
    func_do: str,
    TR: float,
    slice_times: List[float],
    sed: int,
    loops: List[int] = [1, 1, 1],
    subsample: List[int] = [5, 3, 1],
    borders: List[int] = [1, 1, 1],
    use_allineate: bool = False,
):
    """Create reference image and motion correction.

    This function computes a quick intensity mask to get rid of voxels
    that are way outside the skull. It then computes an initial DVARs
    estimate to exclude volumes. It finds the worst 5% of volumes by DVARs
    and excludes volumes adjacent to those worst volumes (a centered window
    of size 3). The DVARs time course is then smooothed to find long
    stretches (~100 frames) of minimal motion, excluding the
    first/last 10% of the scan.

    We use these extracted frames to create a reference functional image
    for further processing.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    func_do : str
        Deobliqued functional image.
    TR : float
        Repetition time of scan.
    slice_times : List[float]
        List of slice times.
    sed : int
        Axis of slice encoding direction.
    loops : List[int]
        Number of loops for SpaceTimeRealign.
    subsample : List[int]
        Subsampling for SpaceTimeRealign.
    borders : List[int]
        Borders for SpaceTimeRealign.
    use_allineate : bool
        Sets whether to use 3dAllineate for framewise alignment instead.

    Returns
    -------
    str
        Path to motion corrected functional.
    str
        Path to reference functional.
    """
    logging.info("Creating reference image...")

    # load functional image
    func_do_img = nib.load(func_do)
    func_do_data = func_do_img.get_fdata()

    # get the mean functional
    mean_data = np.mean(func_do_data, axis=3)

    # get a quick intensity mask
    quick_intensity_mask = (mean_data > (np.max(mean_data.ravel()) / 100)).astype(mean_data.dtype)
    vectorized_func_data = func_do_data.reshape(np.multiply.reduce(func_do_data.shape[:3]), func_do_data.shape[3])
    vectorized_mask = quick_intensity_mask.ravel()
    mask_indices = np.squeeze(np.argwhere(vectorized_mask.astype("?")))
    masked_vectorized_func_data = vectorized_func_data[mask_indices, :]

    # calculate DVARs
    dvars = np.mean(np.abs(zscore(np.diff(masked_vectorized_func_data, axis=1), ddof=1, axis=1)), axis=0)
    dvars = np.insert(dvars, 0, dvars[0], axis=0)

    # sort DVARs and threshold
    sorted_dvars = np.sort(dvars)
    threshold = sorted_dvars[np.floor(sorted_dvars.shape[0] * 0.9).astype(np.int)]
    invalid_idx = np.squeeze(np.argwhere(dvars > threshold))
    # for arrays that only have a single value
    invalid_idx = invalid_idx[np.newaxis] if len(invalid_idx.shape) == 0 else invalid_idx
    invalid_idx = np.tile(invalid_idx, (3, 1)) + np.tile([-1, 0, 1], (invalid_idx.shape[0], 1)).T
    invalid_idx = invalid_idx.ravel()
    invalid_idx = invalid_idx[np.logical_and(invalid_idx >= 0, invalid_idx < sorted_dvars.shape[0])]

    # low pass filter DVARs
    b, a = ss.butter(1, 0.16, "lowpass")
    filtered_dvars = ss.filtfilt(b, a, dvars)
    first_scan_idx = np.arange(dvars.shape[0] * 0.1)
    last_scan_idx = (dvars.shape[0] - 1) - first_scan_idx
    exclude_idx = np.unique(np.concatenate((invalid_idx, first_scan_idx, last_scan_idx))).astype(int)
    include_idx = np.delete(np.arange(dvars.shape[0]), exclude_idx)
    filtered_dvars = filtered_dvars[include_idx]
    filtered_sort_idx = np.squeeze(include_idx[np.argsort(filtered_dvars)])

    # return the lowest dvars frame to align to
    ref_frame_nums = [f for f in filtered_sort_idx[:100]]
    logging.info("100 low DVARs frames:")
    logging.info(ref_frame_nums)

    # get rigid body parameters and alignment
    rigid_body_params = os.path.join(output_path, "rigid_body.params")
    func_do_moco = append_suffix(repath(output_path, func_do), "_moco")
    if use_allineate:
        # align the low DVARs volume set to initial target volume
        logging.info("Aligning all low DVARs frames...")
        best_aligned_func = os.path.join(output_path, "func_lowDVARs.nii.gz")
        Allineate(
            prefix=best_aligned_func,
            base=f"{func_do}[{ref_frame_nums[0]}]",
            source=f"{func_do}[{','.join([str(n) for n in ref_frame_nums])}]",
            warp="shift_rotate",
            fineblur=4,
            cost="ls",
            nmatch="75%",
            other_args="-autoweight",
        )

        # spatial blur (FWHM)
        best_aligned_func_blur = append_suffix(best_aligned_func, "_blur")
        run_process(f"3dBlurInMask -prefix {best_aligned_func_blur} -input {best_aligned_func} -FWHM 12 -overwrite")
        # get high spatial freqs
        best_aligned_func_hispf = append_suffix(best_aligned_func, "_hispf")
        run_process(
            f"3dcalc -prefix {best_aligned_func_hispf} "
            f"-a {best_aligned_func} -b {best_aligned_func_blur} -expr 'a-b' -overwrite"
        )
        # get mean of best aligned functional frames
        best_aligned_func_img = nib.load(best_aligned_func)
        data = np.mean(best_aligned_func_img.get_fdata(), axis=3)
        ref_func_img = nib.Nifti1Image(data, best_aligned_func_img.affine)
        ref_func = append_suffix(repath(output_path, func_do), "_reference")
        ref_func_img.to_filename(ref_func)

        # prepare reference for framewise alignment
        ref_func_blur = append_suffix(ref_func, "_blur")
        run_process(f"3dBlurInMask -prefix {ref_func_blur} -input {ref_func} -FWHM 12 -overwrite")
        ref_func_hispf = append_suffix(ref_func, "_hispf")
        run_process(f"3dcalc -prefix {ref_func_hispf} -a {ref_func} -b {ref_func_blur} -expr 'a-b' -overwrite")

        # prepare functional for framewise alignment
        func_do_blur = repath(output_path, append_suffix(func_do, "_blur"))
        run_process(f"3dBlurInMask -prefix {func_do_blur} -input {func_do} -FWHM 12 -overwrite")
        func_do_hispf = repath(output_path, append_suffix(func_do, "_hispf"))
        run_process(f"3dcalc -prefix {func_do_hispf} -a {func_do} -b {func_do_blur} -expr 'a-b' -overwrite")

        # framewise align hispf images
        logging.info("Running framewise alignment of functional image...")
        func_do_hispf_moco = append_suffix(func_do_hispf, "_moco")
        Allineate(
            prefix=func_do_hispf_moco,
            base=ref_func_hispf,
            source=func_do_hispf,
            matrix_save=os.path.join(output_path, "matrix_save.aff12.1D"),
            warp="shift_rotate",
            fineblur=4,
            cost="ls",
            nmatch="75%",
            other_args="-autoweight",
        )
        # copy and rename
        shutil.copy2(os.path.join(output_path, "matrix_save.aff12.1D"), rigid_body_params)

        logging.info("Apply framewise alignment to functional image...")
        Allineate(
            prefix=func_do_moco,
            base=ref_func,
            source=func_do,
            matrix_apply=os.path.join(output_path, "matrix_save.aff12.1D"),
        )
    else:
        # run realign4d
        transforms, resampled = realign4d(
            func_do_img, ref_frame_nums[0], TR, slice_times, sed, loops, subsample, borders
        )

        # write rb params
        write_rb_params(rigid_body_params, transforms)

        # write moco func to disk
        resampled.to_filename(func_do_moco)

        # create reference functional
        func_do_moco_img = nib.load(func_do_moco)
        data = np.mean(func_do_moco_img.get_fdata()[:, :, :, ref_frame_nums], axis=3)
        ref_func_img = nib.Nifti1Image(data, func_do_moco_img.affine)
        ref_func = append_suffix(repath(output_path, func_do), "_reference")
        ref_func_img.to_filename(ref_func)

    # return processed
    return (func_do_moco, ref_func, rigid_body_params)
