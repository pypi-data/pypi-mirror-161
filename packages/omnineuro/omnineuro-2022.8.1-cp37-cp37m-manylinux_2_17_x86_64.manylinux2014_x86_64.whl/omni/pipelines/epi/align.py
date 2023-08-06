import os
from pathlib import Path
import logging
import shutil
from typing import List
import nibabel as nib
from scipy.ndimage import gaussian_filter
from memori.pathman import append_suffix, repath
from memori.helpers import create_output_path, create_symlink_to_path
from omni.interfaces.common import create_fov_masks
from omni.interfaces.afni import Allineate, NwarpApply, NwarpCat, resample
from omni.interfaces.fsl import flirt
from omni.interfaces.ants import antsRegistration, antsApplyTransform
from omni.preprocessing import clahe
from omni.io import convert_affine_file
from omni.masks import make_regression_mask
from omni.register import register

# Directory this file lives in
THISDIR = os.path.dirname(os.path.abspath(__file__))

# Get atlas directory
ATLASDIR = os.path.join(os.path.dirname(THISDIR), "atlas")


@create_output_path
def align_affine_epi_to_anat(
    output_path: str,
    ref_epi_bet: str,
    initial_synth_model: str = "rbf(0;4)+rbf(1;4)+rbf(0;4)*rbf(1;4)",
    t1_bet: str = None,
    t2_bet: str = None,
    program: str = "fsl",
    bandwidth: int = 16,
    initial_affine: str = None,
    skip_affine: bool = False,
    skip_synthtarget_affine: bool = False,
    resolution_pyramid: List[float] = [4, 2, 1],
    max_iterations: List[int] = [2000, 500, 100],
    err_tol: List[float] = [1e-4, 1e-4, 5e-4],
    step_size: List[float] = [1e-3, 1e-3, 1e-3],
):
    """Affine align func to anat

    Parameters
    ----------
    output_path: str
        Output path to write out files to.
    ref_epi_bet: str
        Reference EPI skullstripped.
    initial_synth_model: str
        Synth model.
    t1_bet: str
        T1 skullstripped.
    t2_bet: str
        T2 skullstripped.
    bandwidth: int
        Bandwidth for blurring kernel.
    program: str
        Program to use for affine alignment.
    initial_affine: str
        Initial affine to use instead of using internal flirt alignment.
    skip_affine: bool
        Skip affine alignment step.
    skip_synthtarget_affine: bool
        Skip synthtarget affine alignment step.
    resolution_pyramid: List[float]
        Resampling pyramid to use for affine alignment (mm).
    max_iterations: List[int]
        Max iterations for each SynthTarget call.
    err_tol: List[float]
        Error tolerance level for each SynthTarget call.
    step_size: List[float]
        Step size for gradient descent.

    Returns
    -------
    str
        Final func to anat affine (afni).
    str
        Final anat to func affine (afni).
    """
    # resample ref_func_bet images to specified image pyramid
    ref_epi_bet_res = list()
    for res in resolution_pyramid:
        res_str = ("%s" % res).replace(".", "d")
        ref_epi_bet_res.append(append_suffix(repath(output_path, ref_epi_bet), "_%smm" % res_str))
        resample(ref_epi_bet_res[-1], ref_epi_bet, ref_epi_bet, dxyz=res)

    # resample anat images to specified image pyramid
    t1_bet_res = list()
    t2_bet_res = list()
    for res in resolution_pyramid:
        res_str = ("%s" % res).replace(".", "d")
        t1_bet_res.append(append_suffix(repath(output_path, t1_bet), "_%smm" % res_str))
        t2_bet_res.append(append_suffix(repath(output_path, t2_bet), "_%smm" % res_str))
        resample(t1_bet_res[-1], t1_bet, t1_bet, dxyz=res)
        resample(t2_bet_res[-1], t2_bet, t2_bet, dxyz=res)

    # do not do initial affine alignment call if skip enabled
    # or if initial affine is already provided
    if not skip_affine and initial_affine is None:
        # create a symlinks to func and T2 for reference
        t2_bet_link = create_symlink_to_path(t2_bet, output_path)
        ref_bet_link = create_symlink_to_path(ref_epi_bet, output_path)

        # get an initial affine transform guess
        initial_func_to_t2_xfm = os.path.join(output_path, "initial_func_to_t2.aff12.1D")
        initial_func_to_t2 = os.path.join(output_path, "initial_func_to_t2.nii.gz")
        if program == "afni":
            Allineate(
                initial_func_to_t2,
                t2_bet_link,
                ref_bet_link,
                cost="mi",
                warp="shift_rotate",
                matrix_save=initial_func_to_t2_xfm,
                twopass=True,
            )
        elif program == "fsl":  # Use flirt
            initial_func_to_t2_flirt = os.path.join(output_path, "initial_func_to_t2.mat")
            flirt(
                initial_func_to_t2,
                t2_bet_link,
                ref_bet_link,
                out_matrix=initial_func_to_t2_flirt,
                dof=6,
                cost="mutualinfo",
            )
            convert_affine_file(
                initial_func_to_t2_xfm, initial_func_to_t2_flirt, "afni", target=t2_bet_link, source=ref_bet_link
            )
        else:
            raise ValueError("Invalid parameter set for program. " "Must be either 'afni' or 'fsl'.")

        # convert affine file to omni format and invert
        initial_t2_to_func_xfm = os.path.join(output_path, "initial_t2_to_func.affine")
        convert_affine_file(initial_t2_to_func_xfm, initial_func_to_t2_xfm, "omni", invert=True)

        # initialize the initial affine to use
        initial_affine = initial_t2_to_func_xfm
    elif skip_affine and initial_affine is None:  # if initial affine was not defined, but skip enabled
        initial_affine = None

    # get the resolution of the final resolution pyramid
    anat_res = resolution_pyramid[-1]

    # run SynthTarget
    output_pathobj = Path(output_path)
    synthtarget_params_res = list()
    synthtarget_affine_res = list()
    synthtarget_synthetic_res = list()
    for i, res in enumerate(resolution_pyramid):
        res_str = ("%s" % res).replace(".", "d")
        synthtarget_params_res.append(str(output_pathobj / ("synthtarget_params_%smm" % res_str)))
        synthtarget_affine_res.append(str(output_pathobj / ("synthtarget_params_%smm.affine" % res_str)))
        synthtarget_synthetic_res.append(str(output_pathobj / ("synthtarget_%smm.nii.gz" % res_str)))

        register(  # SynthTarget
            ref_epi_bet_res[i],
            initial_synth_model,
            [t1_bet_res[i], t2_bet_res[i]],
            output=synthtarget_params_res[i],
            aligned_output=synthtarget_synthetic_res[i],
            initial_affine=initial_affine,
            max_iterations=max_iterations[i],
            err_tol=err_tol[i],
            step_size=step_size[i],
            bandwidth=bandwidth / (res / anat_res),
            no_register=skip_affine or skip_synthtarget_affine,
        )

        # set next initial affine
        initial_affine = synthtarget_affine_res[i]

    # convert affine to afni
    final_epi_to_anat_affine = str(output_pathobj / "final_epi_to_anat.aff12.1D")
    final_anat_to_epi_affine = str(output_pathobj / "final_anat_to_epi.aff12.1D")
    convert_affine_file(final_epi_to_anat_affine, synthtarget_affine_res[-1], "afni", invert=True)
    convert_affine_file(final_anat_to_epi_affine, synthtarget_affine_res[-1], "afni", invert=False)

    # return affine
    return (final_epi_to_anat_affine, final_anat_to_epi_affine)


@create_output_path
def distortion_correction(
    output_path: str,
    epi_moco: str,
    ref_epi: str,
    t1: str,
    t2: str,
    anat_bet_mask: str,
    anat_weight_mask: str,
    final_anat_to_epi_affine: str,
    final_epi_to_anat_affine: str,
    final_synth_model: str = "rbf(0;12)+rbf(1;12)+rbf(0;12)*rbf(1;12)",
    bandwidth: int = 16,
    resample_resolution: float = 1,
    sigma_t2: float = 0.5,
    initial_warp_field: str = None,
    SyN_step_size: List[float] = [3, 1, 0.1],
    SyN_smoothing: str = "2x1x0x0",
    SyN_shrink_factors: str = "4x3x2x1",
    noise_mask_dilation_size: int = 2,
    noise_mask_iterations: int = 20,
    noise_mask_sigma: float = 2,
    warp_direction: str = "none",
    autobox_mask: str = None,
):
    """Distortion correction.

    Parameters
    ----------
    output_path: str
        Output path to write out files to.
    epi_moco : str
        EPI image that has been motion corrected/framewise aligned.
    ref_epi: str
        Reference EPI image.
    t1: str
        T1.
    t2: str
        T2.
    anat_bet_mask: str
        Anatomical brain mask.
    anat_weight_mask: str
        Anatomical weight mask.
    final_anat_to_epi_affine: str
        Final anat to epi affine (afni).
    final_epi_to_anat_affine: str
        Final epi to anat affine (afni).
    final_synth_model: str
        Synth model.
    bandwidth: int
        Bandwidth for blurring kernel.
    resample_resolution: float
        Resample resolution space to do warps on (mm).
    sigma_t2: float
        Parameter to smooth T2 for initial warp.
    initial_warp_field: str
        Uses this file as an initial warp field instead of computing it, this should be from ref_epi -> T2.
    SyN_step_size : List[float]
        Set the gradient descent step size for each iteration of warp.
    SyN_smoothing: str
        Smoothing kernel size for each level of optimization.
    SyN_shrink_factors: str
        Resampling factor for each level of optimization.
    noise_mask_dilation_size : int
        Dilation size for noise mask.
    noise_mask_iterations: int
        Number of iterations to run noise mask LDA.
    noise_mask_sigma: float
        Size of gaussian smoothing kernel for noise mask.
    warp_direction: str
        Warp direction
    autobox_mask: int
        mask defining the autobox

    Returns
    -------
    str
        Final synthetic to EPI warp (Distort synthetic to match EPI)
    str
        Final EPI to synthetic warp (Undistort EPI to match synthetic)
    """
    # get warp direction
    restrict_deform = {"x": "1x0x0", "y": "0x1x0", "z": "0x0x1", "none": "1x1x1"}[warp_direction]

    # create resample resolution string
    res_str = ("%s" % resample_resolution).replace(".", "d")

    # resample images
    ref_epi_res = append_suffix(repath(output_path, ref_epi), "_%smm" % res_str)
    t1_res = append_suffix(repath(output_path, t1), "_%smm" % res_str)
    t2_res = append_suffix(repath(output_path, t2), "_%smm" % res_str)
    resample(ref_epi_res, ref_epi, ref_epi, dxyz=resample_resolution)
    resample(t1_res, t1, t1, dxyz=resample_resolution)
    resample(t2_res, t2, t2, dxyz=resample_resolution)

    # run lce on ref epi
    ref_epi_res_img = nib.load(ref_epi_res)
    ref_epi_lce_res_img = clahe(ref_epi_res_img)
    ref_epi_lce_res = append_suffix(repath(output_path, ref_epi_res), "_clahe")
    ref_epi_lce_res = append_suffix(repath(output_path, ref_epi_res), "_clahe")
    ref_epi_lce_res_img.to_filename(ref_epi_lce_res)

    # get t2 in space of epi
    t2_res_epispace = append_suffix(t2_res, "_epispace")
    Allineate(t2_res_epispace, ref_epi_lce_res, t2_res, matrix_apply=final_anat_to_epi_affine)

    # smooth the t2
    t2_res_epispace_img = nib.load(t2_res_epispace)
    t2_res_smooth_data = gaussian_filter(t2_res_epispace_img.get_fdata(), sigma_t2)
    t2_res_epispace_smooth = append_suffix(t2_res_epispace, "_smooth")
    nib.Nifti1Image(t2_res_smooth_data, t2_res_epispace_img.affine, t2_res_epispace_img.header).to_filename(
        t2_res_epispace_smooth
    )

    # create_fov_masks
    ref_fov_mask = os.path.join(output_path, "ref_fov_mask.nii.gz")
    source_fov_mask = os.path.join(output_path, "source_fov_mask.nii.gz")
    create_fov_masks(ref_epi_lce_res, t2_res, final_anat_to_epi_affine, ref_fov_mask, source_fov_mask)

    # if an autobox was used on functional, then we need to account for it
    if autobox_mask:
        # resample to the ref_fov_mask
        resample(ref_fov_mask, ref_epi_lce_res, autobox_mask, rmode="NN")

    # setup initial warp names
    initial_warp_prefix = os.path.join(output_path, "initial_")
    initial_0warp = initial_warp_prefix + "0Warp.nii.gz"
    initial_0iwarp = initial_warp_prefix + "0InverseWarp.nii.gz"

    # if an initial warp field is provided, use it
    if initial_warp_field:
        # resample the initial warp field to the working resolution
        resample(initial_0iwarp, ref_epi_lce_res, initial_warp_field)
        # get the inverse of the iwarp to get the warp
        NwarpCat(initial_0warp, initial_0iwarp, True)
    else:  # get the initial warps running a crude nonlinear SyN registration
        # run initial ants warp
        antsRegistration(
            initial_warp_prefix,
            ref_epi_lce_res,
            t2_res_epispace_smooth,
            grad_step=1,
            metric="Mattes",
            rad_bin=50,
            update_field_var=2,
            total_field_var=2,
            convergence="500x0",
            smoothing="1x0",
            shrink_factors="2x1",
            threshold_window=20,
            restrict_deform=restrict_deform,
            reference_mask=ref_fov_mask,
            source_mask=source_fov_mask,
        )
    # apply warps to images for reference
    t2_res_epispace_warped = append_suffix(t2_res_epispace, "_initialwarped")
    NwarpApply(t2_res_epispace_warped, ref_epi_lce_res, t2_res_epispace_smooth, initial_0warp)
    ref_epi_lce_res_unwarped = append_suffix(ref_epi_lce_res, "_initialunwarped")
    NwarpApply(ref_epi_lce_res_unwarped, t2_res_epispace_smooth, ref_epi_lce_res, initial_0iwarp)
    # rename the warps from their temp name
    initial_warp = initial_warp_prefix + "Warp.nii.gz"
    initial_iwarp = initial_warp_prefix + "InverseWarp.nii.gz"
    shutil.move(initial_0warp, initial_warp)
    shutil.move(initial_0iwarp, initial_iwarp)

    # ensure warps have vector intent code for ANTs
    warp_img = nib.load(initial_warp)
    warp_img.header.set_intent("vector")
    warp_img.to_filename(initial_warp)
    iwarp_img = nib.load(initial_iwarp)
    iwarp_img.header.set_intent("vector")
    iwarp_img.to_filename(initial_iwarp)

    # get initial regression mask
    initial_prefix = os.path.join(output_path, "iteration0_")
    regression_mask = make_regression_mask(
        initial_prefix,
        epi_moco,
        anat_bet_mask,
        anat_weight_mask,
        final_anat_to_epi_affine,
        final_epi_to_anat_affine,
        initial_warp,
        initial_iwarp,
        noise_mask_dilation_size,
        noise_mask_iterations,
        noise_mask_sigma,
    )

    # resample regression mask
    regression_mask_res = append_suffix(regression_mask, "_%smm" % res_str)
    resample(regression_mask_res, regression_mask, regression_mask, dxyz=resample_resolution)

    # convert affine to omni type
    final_anat_to_epi_omni_affine = os.path.join(output_path, "final_anat_to_epi.affine")
    convert_affine_file(final_anat_to_epi_omni_affine, final_anat_to_epi_affine, "omni")

    # setup synth warp output name function
    # setting suffix to "" gives only the prefix
    def synth_warp(i, suffix):
        return os.path.join(output_path, "iteration%d_synth_%s" % (i, suffix))

    # Run iterative warp
    iterations = len(SyN_step_size)
    for n in range(iterations):
        logging.info("Running warp (Iteration %d)...", n)

        # generate synthetic image
        synthetic_epispace = os.path.join(output_path, "iteration%d_synthetic_epispace.nii.gz" % n)
        synthetic_anatspace = os.path.join(output_path, "iteration%d_synthetic_anatspace.nii.gz" % n)
        register(
            ref_epi_lce_res_unwarped,
            final_synth_model,
            [t1_res, t2_res],
            aligned_output=synthetic_epispace,
            blurred_regressed_output=synthetic_anatspace,
            initial_affine=final_anat_to_epi_omni_affine,
            regress_mask=regression_mask_res,
            no_register=True,
            bandwidth=bandwidth,
            tone_curve=True,
            tone_curve_mask=regression_mask_res,
        )

        # warp synthetic to functional
        antsRegistration(
            synth_warp(n, ""),
            ref_epi_lce_res,
            synthetic_epispace,
            grad_step=SyN_step_size[n],
            rad_bin=2,
            update_field_var=2,
            total_field_var=2,
            convergence="".join(["500x" for i in SyN_shrink_factors.split("x")[:-1]]) + "0",
            threshold_window=20,
            smoothing=SyN_smoothing,
            shrink_factors=SyN_shrink_factors,
            restrict_deform=restrict_deform,
            reference_mask=ref_fov_mask,
            source_mask=source_fov_mask,
            initial_warp=initial_warp if n == 0 else synth_warp(n - 1, "Warp.nii.gz"),
        )

        # concatenate with last warp
        antsApplyTransform(
            synth_warp(n, "Warp.nii.gz"),
            ref_epi_lce_res,
            synthetic_epispace,
            [initial_warp if n == 0 else synth_warp(n - 1, "Warp.nii.gz"), synth_warp(n, "1Warp.nii.gz")],
            composite_warp=True,
        )
        antsApplyTransform(
            synth_warp(n, "InverseWarp.nii.gz"),
            ref_epi_lce_res,
            synthetic_epispace,
            [
                initial_iwarp if n == 0 else synth_warp(n - 1, "InverseWarp.nii.gz"),
                synth_warp(n, "1InverseWarp.nii.gz"),
            ],
            composite_warp=True,
        )
        # delete temp warps
        os.remove(synth_warp(n, "0Warp.nii.gz"))
        os.remove(synth_warp(n, "1Warp.nii.gz"))
        os.remove(synth_warp(n, "1InverseWarp.nii.gz"))

        # get the warp applied to synthetic
        synthetic_warped = append_suffix(synthetic_epispace, "_warped")
        NwarpApply(synthetic_warped, ref_epi_lce_res, synthetic_epispace, synth_warp(n, "Warp.nii.gz"))

        # get the inverse warp applied to epi
        ref_epi_lce_res_unwarped = append_suffix(ref_epi_lce_res, "%d_unwarped" % n)
        NwarpApply(ref_epi_lce_res_unwarped, synthetic_epispace, ref_epi_lce_res, synth_warp(n, "InverseWarp.nii.gz"))

        # make symlink to unwarped epi for easy reference
        epi_unwarped = os.path.join(output_path, "iteration%d_epi_unwarped.nii.gz" % n)
        if os.path.islink(epi_unwarped):
            os.remove(epi_unwarped)
        os.symlink(os.path.basename(ref_epi_lce_res_unwarped), epi_unwarped)

        if n < iterations - 1:  # skip the last iteration for regression mask
            # get new regression mask from new warp
            mask_prefix = os.path.join(output_path, "iteration%d_" % (n + 1))
            regression_mask = make_regression_mask(
                mask_prefix,
                epi_moco,
                anat_bet_mask,
                anat_weight_mask,
                final_anat_to_epi_affine,
                final_epi_to_anat_affine,
                synth_warp(n, "Warp.nii.gz"),
                synth_warp(n, "InverseWarp.nii.gz"),
                noise_mask_dilation_size,
                noise_mask_iterations,
                noise_mask_sigma,
            )

            # resample regression mask
            regression_mask_res = append_suffix(regression_mask, "_%smm" % res_str)
            resample(regression_mask_res, regression_mask, regression_mask, dxyz=resample_resolution)

    # resample the forward warp to the EPI resolution
    ref_epi_img = nib.load(ref_epi)  # resolution of EPI
    # assumes voxels are isotropic
    data_resolution = ref_epi_img.header.get_zooms()[0]
    final_synth_to_epi_warp = os.path.join(output_path, "final_synth_to_epi_warp.nii.gz")
    resample(final_synth_to_epi_warp, synth_warp(n, "Warp.nii.gz"), synth_warp(n, "Warp.nii.gz"), dxyz=data_resolution)

    # get inverted final warp
    final_epi_to_synth_warp = os.path.join(output_path, "final_epi_to_synth_warp.nii.gz")
    NwarpCat(final_epi_to_synth_warp, final_synth_to_epi_warp, True)

    # return warps
    return (final_synth_to_epi_warp, final_epi_to_synth_warp)


@create_output_path
def combine_transforms(
    output_path: str,
    raw_epi: str,
    final_epi_to_synth_warp: str,
    final_epi_to_anat_affine: str,
    atlas_align_affine: str,
    atlas: str = "mni",
    atlas_label: str = "atlas",
    data_resolution: float = None,
    use_allineate: bool = False,
    rigid_body_params: str = None,
):
    """Combine transforms to produce preprocessed files.

    Parameters
    ----------
    output_path: str
        Output path to write out files to.
    raw_epi: str
        EPI to align to atlas.
    final_epi_to_synth_warp: str
        Undistorting warp for EPI.
    final epi_to_anat_affine: str
        Affine transform from EPI to anat.
    atlas_align_affine: str
        Affine transform from anat to atlas.
    atlas: str
        Atlas being aligned to (must match to affine provided).
    atlas_label : str
        Label suffix for atlas outputs.
    use_allineate: bool
        Specifies that 3dAllineate was used for framewise alignment.
    rigid_Body_params: str
        Rigid body transform to use if allineate enabled.

    Returns
    -------
    str
        Atlas aligned EPI.
    """
    # get data resolution of raw_epi if not specified
    if not data_resolution:
        raw_epi_img = nib.load(raw_epi)
        data_resolution = raw_epi_img.header.get_zooms()[0]

    # get the atlas
    if atlas == "mni":
        atlas_path = os.path.join(ATLASDIR, "mni_icbm152_t1_tal_nlin_sym_09c.nii.gz")
    elif atlas == "trio":
        atlas_path = os.path.join(ATLASDIR, "TRIO_Y_NDC.nii.gz")
    elif os.path.isfile(atlas):
        # Test if the atlas is a valid image file.
        nib.load(atlas)
        atlas_path = atlas
        atlas = atlas_label
    else:
        raise ValueError("Invalid atlas.")

    # resample atlas to data resolution
    atlas_resampled = append_suffix(repath(output_path, atlas_path), "_resampled")
    resample(atlas_resampled, atlas_path, atlas_path, dxyz=data_resolution)

    # setup transforms list
    transforms = [atlas_align_affine, final_epi_to_anat_affine, final_epi_to_synth_warp]
    if use_allineate:
        # add framewise alignment if 3dAllineate was used
        rigid_body_params_afni = os.path.join(output_path, "rigid_body.aff12.1D")
        shutil.copy2(rigid_body_params, rigid_body_params_afni)
        transforms.append(rigid_body_params_afni)

    # apply transforms to data
    raw_epi_atlas = append_suffix(repath(output_path, raw_epi), "_%s" % atlas)
    NwarpApply(raw_epi_atlas, atlas_resampled, raw_epi, transforms)

    # fix header information in atlas aligned epi
    # this adds 4th pixdim and descrip info from the original epi image
    # TODO: Not sure why AFNI 3dNwarpApply is not adding this, investigate further in future
    raw_epi_atlas_img = nib.load(raw_epi_atlas)
    raw_epi_img = nib.load(raw_epi)
    raw_epi_atlas_img.header["pixdim"][4] = raw_epi_img.header["pixdim"][4]
    raw_epi_atlas_img.header["descrip"] = raw_epi_img.header["descrip"]
    nib.Nifti1Image(raw_epi_atlas_img.get_fdata(), raw_epi_atlas_img.affine, raw_epi_atlas_img.header).to_filename(
        raw_epi_atlas
    )

    # return atlas aligned EPI
    return raw_epi_atlas
