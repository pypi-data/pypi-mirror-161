"""Functions for image mask creation.
"""
import os
import logging
from typing import Tuple
import numpy as np
import nibabel as nib
from memori.helpers import hashable
from skimage.filters import threshold_otsu
from scipy.ndimage import binary_dilation, binary_closing, binary_fill_holes
from scipy.linalg import eig
from scipy.ndimage import gaussian_filter
from scipy.stats import zscore
from scipy.ndimage import binary_dilation, binary_opening, generate_binary_structure, iterate_structure
from omni.interfaces.common import append_suffix, repath, normalize
from omni.interfaces.afni import Allineate, NwarpApply


# @hashable
def compute_weight_mask(
    brain: nib.Nifti1Image, brain_mask: nib.Nifti1Image, eye_mask: nib.Nifti1Image = None, dilation_size: int = 15
) -> nib.Nifti1Image:
    """Compute a weight mask for a given brain mask.

    This function computes a weight mask for a given brain mask.
    The weight mask is computed by dilating the brain mask by `dilation_size`
    and then finding the non-brain portions through the use of otsu's method +
    thresholding + morphology

    The weight mask is weighted by the number of voxels in brain vs. non-brain.

    Parameters
    ----------
    brain: nib.Nifti1Image
        Brain image.
    brain_mask: nib.Nifti1Image
        Brain mask.
    eye_mask: nib.Nifti1Image, optional
        Eye mask.
    dilation_size: int
        Size to dilate brain mask by.

    Returns
    -------
    nib.Nifti1Image
        Weight mask.

    """
    # get the data for the brain mask
    brain_mask_data = brain_mask.get_fdata().astype(bool)

    # get the brain data
    brain_data = brain.get_fdata()

    # ensure they are the same size
    assert brain_mask_data.shape == brain_data.shape, "Brain mask and brain data must be the same size"

    # pad the data so later operations don't go out of bounds
    padded_brain_data = np.pad(brain_data, pad_width=dilation_size, mode="constant")
    padded_brain_mask_data = np.pad(brain_mask_data, pad_width=dilation_size, mode="constant")

    # create structural element for dilation
    strel = generate_binary_structure(3, 3)

    # now dilate the brain_mask
    dilated_brain_mask_data = binary_dilation(padded_brain_mask_data, structure=strel, iterations=dilation_size)

    # now take the difference between the dilated and brain_mask
    non_brain_mask_data = np.logical_not(padded_brain_mask_data)

    # within the non-brain mask, find the otsu's method threshold / 2
    threshold = threshold_otsu(padded_brain_data[non_brain_mask_data]) / 2

    # threshold the brain image
    thresholded_brain_data = padded_brain_data > threshold

    # now compute the intersection of the thresholded brain and the non-brain mask
    non_brain_mask_data2 = np.logical_and(
        np.logical_and(thresholded_brain_data, dilated_brain_mask_data), non_brain_mask_data
    )

    # now apply a sphere to the non-brain mask with a closing operation
    strel2 = generate_binary_structure(3, 1)
    non_brain_mask_data3 = binary_closing(non_brain_mask_data2, structure=strel2, iterations=dilation_size)

    # and dilate out the mask a bit
    non_brain_mask_data4 = binary_dilation(non_brain_mask_data3, structure=strel2, iterations=1)

    # fill in any holes in the mask
    non_brain_mask_data5 = binary_fill_holes(non_brain_mask_data4)

    # get the data for the eye mask if available
    if eye_mask:
        eye_mask_data = eye_mask.get_fdata()
        # pad the eye mas
        padded_eye_mask_data = np.pad(eye_mask_data, pad_width=dilation_size, mode="constant")
        # and add it to the brain mask
        padded_brain_data = np.logical_or(padded_brain_data, padded_eye_mask_data)

    # remove part of non-brain mask overlapping with the brain mask (and eye mask)
    non_brain_mask_data6 = np.logical_and(non_brain_mask_data5, np.logical_not(padded_brain_mask_data))

    # get number of voxels in each mask
    num_brain_voxels = np.sum(padded_brain_mask_data)
    num_non_brain_voxels = np.sum(non_brain_mask_data6)

    # combine the images
    weight_mask_data = (padded_brain_mask_data / num_brain_voxels) + (0.5 * non_brain_mask_data6 / num_non_brain_voxels)
    # normalize 0 to 1
    weight_mask_data = normalize(weight_mask_data)[
        dilation_size:-dilation_size, dilation_size:-dilation_size, dilation_size:-dilation_size
    ]

    # return image
    return nib.Nifti1Image(weight_mask_data, brain_mask.affine)


@hashable
def lda(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Linear Discriminant Analysis for time series data.

    Parameters
    ----------
    X: np.ndarray
        The data in a numpy array. Where rows are samples,
        cols are features.
    labels: np.ndarray
        Labels for data. Corresponds to samples.

    Returns
    -------
    np.ndarray
        Projected data.
    """
    # get the mean over all time for each voxel
    u = np.mean(X, axis=1)[:, np.newaxis]
    exclude_mask = np.all(X == u, axis=1)

    # save original array
    origX = X.copy()

    # filter voxel using exclude mask
    X = X[~exclude_mask, :]
    labels = labels[~exclude_mask]

    # get mean of each voxel time series (And for each class)
    M = np.mean(X, axis=0)  # mean time series
    M0 = np.mean(X[labels, :], axis=0)  # mean time series of brain voxels
    M1 = np.mean(X[~labels, :], axis=0)  # mean time series of non-brain voxels

    # get number of nonzero voxels and number of zero voxels
    N0 = np.count_nonzero(labels)
    N1 = np.count_nonzero(~labels)

    # get demeaned time series for each class
    demean0 = X[labels, :] - M0[np.newaxis, :]
    demean1 = X[~labels, :] - M1[np.newaxis, :]

    # get within/between class covariance matrices
    within_cov = np.matmul(demean0.T, demean0) + np.matmul(demean1.T, demean1)
    between_cov = N0 * np.matmul((M0 - M)[:, np.newaxis], (M0 - M)[:, np.newaxis].T) + N1 * np.matmul(
        (M1 - M)[:, np.newaxis], (M1 - M)[:, np.newaxis].T
    )

    # do eigendecomposition
    W, R = eig(between_cov, within_cov)
    idx = np.argsort(-W)  # sort from largest to smallest eigenvalue
    orderedR = R[:, idx]

    # project data onto eigenvectors (only grab real values)
    return np.real(np.matmul(origX, orderedR))


@hashable
def generate_noise_mask(
    img: nib.Nifti1Image, mask: nib.Nifti1Image, size: int = 2, iterations: int = 20, sigma: float = 3
) -> Tuple[np.ndarray, np.ndarray]:
    """Generates a mask identifying noise and signal voxels.

    Parameters
    ----------
    img: nib.Nifti1Image
        Image to construct noise mask on.
    mask: nib.Nifti1Image
        Mask outlining a prior guess between noise/signal voxels.
    size: int
        Size to dilate noise mask by.
    iterations: int
        Number of iterations to run LDA.
    sigma: float
        Size of smoothing kernel for weight mask.

    Returns
    -------
    np.ndarray
        Noise mask.
    np.ndarray
        Signal weight mask.
    """
    # get data; reshape to voxels x time
    img_data = img.get_fdata()
    voxel_time = img_data.reshape(np.multiply.reduce(img_data.shape[:3]), img_data.shape[3])

    # get class for voxels between brain and skull
    labels = (mask.get_fdata().ravel() > 0.5).astype(bool)

    # get z-scored functional time series
    z_voxel_time = zscore(voxel_time, axis=1)

    # remove NaN voxels
    z_voxel_time[np.where(np.isnan(z_voxel_time))] = 0

    # do lda to find noisy voxels
    signal_label = labels
    num_voxels = 0
    for i in range(iterations):
        logging.info("Iteration %d", i)
        # get lda on functional data
        Y0 = lda(voxel_time, signal_label)
        Y1 = lda(z_voxel_time, signal_label)
        Y2 = Y0 * Y1

        # do lda on second level of lda on first components
        Y = lda(np.stack((Y0[:, 0], Y1[:, 0], Y2[:, 0]), axis=1), signal_label)

        # get otsu threshold
        threshold = threshold_otsu(Y[:, 0])

        # get classes separated by otsu's method
        class1 = Y[:, 0] < threshold
        class2 = Y[:, 0] > threshold

        # identify the class corresponding to non-signal
        non_signal_array = (
            class1 if np.sum(np.logical_and(class1, labels)) < np.sum(np.logical_and(class2, labels)) else class2
        )

        # take intersection between bet mask to get signal dropout areas only
        signal_drop_out_array = np.logical_and(labels, non_signal_array)
        current_num_voxels = np.count_nonzero(signal_drop_out_array)
        logging.info(f"Number of voxels in mask: {current_num_voxels}")
        if current_num_voxels == num_voxels:
            logging.info(f"Optimized mask found after {i} iterations.")
            break
        num_voxels = current_num_voxels

        # format noise mask
        noise_mask_array = signal_drop_out_array
        noise_mask_data = noise_mask_array.reshape(img.shape[:3])

        # get new signal labels
        signal_label = np.logical_and(signal_label, np.logical_not(noise_mask_data.ravel()))

    # do opening on noise mask + dilation
    opened_noise_mask_data = binary_opening(noise_mask_data, generate_binary_structure(3, 1))
    dilated_opened_noise_mask_data = binary_dilation(
        opened_noise_mask_data, iterate_structure(generate_binary_structure(3, 1), size)
    )

    # construct noise mask image
    noise_mask_img = nib.Nifti1Image(dilated_opened_noise_mask_data.astype("f8"), img.affine, img.header)

    # smooth noise mask
    smooth_noise_mask = nib.Nifti1Image(
        gaussian_filter(noise_mask_img.get_fdata(), sigma), noise_mask_img.affine, noise_mask_img.header
    )

    # return noise mask, signal weight mask
    return (noise_mask_img, smooth_noise_mask)


@hashable
def make_regression_mask(
    output_prefix: str,
    epi: str,
    anat_bet_mask: str,
    anat_weight_mask: str,
    affine: str,
    iaffine: str,
    warp: str,
    iwarp: str,
    noise_mask_dilation_size: int = 2,
    noise_mask_iterations: int = 20,
    noise_mask_sigma: float = 2,
):
    """Make regression mask.

    Parameters
    ----------
    output_prefix: str
        Set prefix for output files.
    epi: str
        EPI file to apply LDA.
    anat_bet_mask: str
        Anatomical brain mask.
    anat_weight_mask: str
        Anatomical weight mask.
    affine: str
        Affine transform (anat to func) (afni).
    iaffine: str
        Inverse affine transform (func to anat) (afni).
    warp: str
        Forward warp (anat to func).
    iwarp: str
        Inverse warp (func to anat).
    noise_mask_dilation_size: int
        Size to dilate noise mask by.
    noise_mask_iterations: int
        Number of iterations to run LDA.
    noise_mask_sigma: float
        Size of smoothing kernel for weight mask.

    Returns
    -------
    str
        Regression mask.
    """
    # get output path
    output_path = os.path.dirname(output_prefix)

    # apply affine to anat mask
    anat_bet_mask_epispace = append_suffix(repath(output_path, anat_bet_mask), "_epispace")
    Allineate(anat_bet_mask_epispace, epi, anat_bet_mask, matrix_apply=affine)

    # warp the anat bet mask
    anat_bet_mask_epispace_warped = append_suffix(anat_bet_mask_epispace, "_warped")
    NwarpApply(anat_bet_mask_epispace_warped, epi, anat_bet_mask_epispace, warp)

    # create noise mask
    epi_img = nib.load(epi)
    anat_bet_mask_epispace_warped_img = nib.load(anat_bet_mask_epispace_warped)
    _, noise_mask_smooth_img = generate_noise_mask(
        epi_img, anat_bet_mask_epispace_warped_img, noise_mask_dilation_size, noise_mask_iterations, noise_mask_sigma
    )
    noise_mask_smooth = output_prefix + "noise_mask_smooth.nii.gz"
    noise_mask_smooth_img.to_filename(noise_mask_smooth)

    # unwarp the noise mask
    noise_mask_smooth_unwarped = append_suffix(noise_mask_smooth, "_unwarped")
    NwarpApply(noise_mask_smooth_unwarped, epi, noise_mask_smooth, iwarp)

    # align back to anat space
    noise_mask_smooth_unwarped_anatspace = append_suffix(noise_mask_smooth_unwarped, "_anatspace")
    Allineate(noise_mask_smooth_unwarped_anatspace, anat_bet_mask, noise_mask_smooth_unwarped, matrix_apply=iaffine)

    # load up weight mask/noise mask
    anat_weight_mask_img = nib.load(anat_weight_mask)
    noise_mask_smooth_unwarped_anatspace_img = nib.load(noise_mask_smooth_unwarped_anatspace)
    regression_mask_data = (
        1 - normalize(noise_mask_smooth_unwarped_anatspace_img.get_fdata())
    ) * anat_weight_mask_img.get_fdata()
    regression_mask = output_prefix + "regression_mask.nii.gz"
    nib.Nifti1Image(regression_mask_data, anat_weight_mask_img.affine, anat_weight_mask_img.header).to_filename(
        regression_mask
    )

    # return regression mask
    return regression_mask
