import os
import json
import shutil
from typing import Dict, List
import nibabel as nib
import numpy as np
from memori.helpers import *
from memori.pathman import append_suffix, repath
from memori import Pipeline, Stage
from omni.interfaces.afni import NwarpApply
from omni.pipelines.anat.masks import weight_mask_and_autobox2
from omni.pipelines.epi.align import align_affine_epi_to_anat, distortion_correction
from .anat.processing import anat_proc, anat_to_epi_results
from .func.processing import func_proc, func_to_epi_results
from .epi.processing import epi_proc


@create_output_path
def pre_proc(
    output_path: str, anat_path: str = "anat", func_path: str = "func", epi_path: str = "epi", **kwargs
) -> None:
    """Run Synth preprocessing pipeline.

    Parameters
    ----------
    output_path: str
        Output path to write out files to.
    anat_path: str
        Subpath for anatomical outputs.
    func_path: str
        Subpath for functional outputs.
    epi_path: str
        Subpath for EPI outputs.
    kwargs: dict
        Various keyword Arguments.
    """
    # run anatomical pipeline
    anat_output = os.path.join(output_path, anat_path)
    anat_results = anat_proc(anat_output, **kwargs)

    # copy anatomically aligned atlas files to an output_data folder
    anat_output_data = os.path.join(anat_output, "output_data")
    os.makedirs(anat_output_data, exist_ok=True)
    if anat_results["t1_atlas"]:
        shutil.copy2(anat_results["t1_atlas"], anat_output_data)
    if anat_results["t2_atlas"]:
        shutil.copy2(anat_results["t2_atlas"], anat_output_data)

    # open the metadata from the bids sidecar, if metadata not defined.
    if "metadata" not in kwargs:
        with open(kwargs["bids_sidecar"], "r") as metadata_file:
            metadata = json.load(metadata_file)
    else:
        metadata = kwargs["metadata"]

    # run functional pipeline
    func_output = os.path.join(output_path, func_path)
    func_results = func_proc(
        func_output,
        TR=metadata["RepetitionTime"],
        slice_times=metadata["SliceTiming"] if "SliceTiming" in metadata else [],
        **kwargs,
    )

    # copy moco func and rigid body params to output_data folder
    func_output_data = os.path.join(func_output, "output_data")
    os.makedirs(func_output_data, exist_ok=True)
    shutil.copy2(func_results["func_do_moco"], func_output_data)
    shutil.copy2(func_results["rigid_body_params"], func_output_data)

    # delete old values
    ckwargs = kwargs.copy()
    del ckwargs["t1"]
    del ckwargs["t2"]

    # run EPI pipeline
    epi_output = os.path.join(output_path, epi_path)
    epi_results = epi_proc(
        epi_output,
        **anat_to_epi_results(anat_results),
        **func_to_epi_results(func_results, (ckwargs["moco"] == "allineate")),
        **ckwargs,
    )

    # copy atlas aligned epi to output_data folder
    epi_output_data = os.path.join(epi_output, "output_data")
    os.makedirs(epi_output_data, exist_ok=True)
    shutil.copy2(epi_results["raw_epi_atlas"], epi_output_data)


@create_output_path
def make_ref_epi_bet(output_path: str, ref_epi: str, ref_epi_bet_mask: str, initial_warp_field: str, **kwargs):
    """Function for applying mask to ref epi

    Parameters
    ----------
    ref_epi: str
        Reference EPI.
    ref_epi_bet_mask: str
        Brain mask for EPI. (NOTE: if initial_warp_field provided this should be a mask after that warp)
    initial_warp_field: str
        Initial distortion correction warp field.

    Returns
    -------
    str
        Brain extracted EPI.
    """
    # if a warp field is provided, then apply it to the ref_epi
    if initial_warp_field:
        ref_epi_warped = repath(output_path, ref_epi)
        NwarpApply(ref_epi_warped, ref_epi, ref_epi, initial_warp_field)
        ref_epi = ref_epi_warped

    # create path
    ref_epi_bet = repath(output_path, append_suffix(ref_epi, "_bet"))

    # load data
    ref_epi_img = nib.load(ref_epi)
    ref_epi_bet_mask_img = nib.load(ref_epi_bet_mask)

    # write masked image to file
    nib.Nifti1Image(
        ref_epi_img.get_fdata() * ref_epi_bet_mask_img.get_fdata(), ref_epi_img.affine, ref_epi_img.header
    ).to_filename(ref_epi_bet)

    # return
    return ref_epi_bet


@create_output_path
@use_abspaths
@use_output_path_working_directory
@create_symlinks_to_input_files()
def synthunwarp(
    output_path: str,
    epi: str,
    ref_epi: str,
    ref_epi_bet_mask: str,
    anat_bet_mask: str,
    anat_eye_mask: str,
    t1_debias: str = None,
    t2_debias: str = None,
    initial_synth_model: str = "rbf(0;4)+rbf(1;4)+rbf(0;4)*rbf(1;4)",
    final_synth_model: str = "rbf(0;12)+rbf(1;12)+rbf(0;12)*rbf(1;12)",
    program: str = "fsl",
    dilation_size: int = 30,
    bandwidth: int = 16,
    initial_affine: str = None,
    skip_affine: bool = False,
    skip_synthtarget_affine: bool = False,
    resolution_pyramid: List[float] = [4, 2, 1],
    synthtarget_max_iterations: List[int] = [2000, 500, 100],
    synthtarget_err_tol: List[float] = [1e-4, 1e-4, 5e-4],
    synthtarget_step_size: List[float] = [1e-3, 1e-3, 1e-3],
    resample_resolution: float = 1,
    sigma_t2: float = 0.5,
    initial_warp_field: str = None,
    distortion_correction_smoothing: str = "2x1x0x0",
    distortion_correction_shrink_factors: str = "4x3x2x1",
    distortion_correction_step_size: List[float] = [3, 1, 0.1],
    warp_direction: str = "none",
    noise_mask_dilation_size: int = 2,
    noise_mask_iterations: int = 20,
    noise_mask_sigma: float = 2,
    autobox_mask: str = None,
    **kwargs,
) -> Dict:
    """SynthUnwarp Pipeline.

    Parameters
    ----------
    output_path: str
        Output path to write out files to.
    epi: str
        EPI image.
    ref_epi: str
        Reference EPI image.
    ref_epi_bet_mask: str
        Reference EPI brain mask.
    anat_bet_mask: str
        Anatomical brain mask.
    anat_eye_mask: str
        Anatomical eye mask.
    t1_debias: str
        Bias field corrected T1 image.
    t2_debias: str
        Bias field corrected T2 image.
    inital_synth_model: str
        Initial model used to generate synthetic image.
    final_synth_model: str
        Final model used to generate synthetic image.
    program: str
        Program to use for affine alignment.
    dilation_size: int
        Size of dilation kernel for weight mask.
    bandwidth: int
        Bandwidth for Epanechnikov kernel.
    initial_affine: str
        Initial affine transformation.
    skip_affine: bool
        Skip affine alignment step.
    skip_synthtarget_affine : bool
        Skip synthtarget affine alignment step.
    resolution_pyramid: List[float]
        Resampling pyramid to use for affine alignment (mm).
    synthtarget_max_iterations: List[int]
        Max iterations for each SynthTarget call.
    synthtarget_err_tol: List[float]
        Error tolerance level for each SynthTarget call.
    synthtarget_step_size: List[float]
        Step size for gradient descent.
    resample_resolution: float
        Resample resolution space to do warps on (mm).
    sigma_t2: float
        Parameter to smooth T2 for initial warp.
    initial_warp_field: str
        Uses this file as an initial warp field instead of computing it, this should be from ref_epi -> T2.
    distortion_correction_step_size : List[float]
        Set the gradient descent step size for each iteration of warp.
    distortion_correction_smoothing: str
        Smoothing kernel size for each level of optimization.
    distortion_correction_shrink_factors: str
        Resampling factor for each level of optimization.
    warp_direction: str
        Warp direction
    noise_mask_dilation_size : int
        Dilation size for noise mask.
    noise_mask_iterations : int
        Number of iterations to run noise mask LDA.
    noise_mask_sigma : float
        Size of gaussian smoothing kernel for noise mask.
    autobox_mask : str
        Mask of autobox on functional

    Returns
    -------
    Dict
        Results of pipeline.
    """
    # make dummy eye mask if not specified
    if anat_eye_mask is None:
        # set default flag
        compute_mask = False
        # set path for the eye mask
        anat_eye_mask = os.path.join("input_data", "dummy_eye_mask.nii.gz")
        # load the brain mask
        brain_mask = nib.load(anat_bet_mask)
        # check if dummy eye mask already exists
        if os.path.exists(anat_eye_mask):
            # check that the mask is the same size as the bet mask
            if brain_mask.shape != nib.load(anat_eye_mask).shape:
                # recompute the mask if it is not the same size
                compute_mask = True
        else:  # if not, make one
            compute_mask = True

        # make the mask if flag raised
        if compute_mask:
            dummy_data = np.zeros(brain_mask.shape)
            nib.Nifti1Image(dummy_data, brain_mask.affine, brain_mask.header).to_filename(anat_eye_mask)

    # make stages
    make_ref_epi_bet_stage = Stage(
        make_ref_epi_bet,
        stage_outputs=["ref_epi_bet"],
        hash_output="synthunwarp_0_make_ref_epi_bet",
        output_path="synthunwarp_0_make_ref_epi_bet",
        ref_epi=ref_epi,
        ref_epi_bet_mask=ref_epi_bet_mask,
        initial_warp_field=initial_warp_field,
    )
    weight_mask_and_autobox_stage = Stage(
        weight_mask_and_autobox2,
        stage_outputs=[
            "notused0",
            "anat_weight_mask",
            "anat_bet_mask",
            "notused1",
            "notused2",
            "t1",
            "t2",
            "t1_bet",
            "t2_bet",
        ],
        hash_output="synthunwarp_1_weight_mask_and_autobox",
        output_path="synthunwarp_1_weight_mask_and_autobox",
        t1_debias=t1_debias,
        t2_debias=t2_debias,
        anat_bet_mask=anat_bet_mask,
        anat_eye_mask=anat_eye_mask,
        dilation_size=dilation_size,
    )
    align_affine_epi_to_anat_stage = Stage(
        align_affine_epi_to_anat,
        stage_outputs=["final_epi_to_anat_affine", "final_anat_to_epi_affine"],
        hash_output="synthunwarp_2_align_affine_epi_to_anat",
        output_path="synthunwarp_2_align_affine_epi_to_anat",
        initial_synth_model=initial_synth_model,
        program=program,
        bandwidth=bandwidth,
        initial_affine=initial_affine,
        skip_affine=skip_affine,
        skip_synthtarget_affine=skip_synthtarget_affine,
        resolution_pyramid=resolution_pyramid,
        max_iterations=synthtarget_max_iterations,
        err_tol=synthtarget_err_tol,
        step_size=synthtarget_step_size,
    )
    distortion_correction_stage = Stage(
        distortion_correction,
        stage_outputs=["final_synth_to_epi_warp", "final_epi_to_synth_warp"],
        hash_output="synthunwarp_3_distortion_correction",
        output_path="synthunwarp_3_distortion_correction",
        epi_moco=epi,
        ref_epi=ref_epi,
        final_synth_model=final_synth_model,
        bandwidth=bandwidth,
        resample_resolution=resample_resolution,
        sigma_t2=sigma_t2,
        initial_warp_field=initial_warp_field,
        SyN_step_size=distortion_correction_step_size,
        SyN_smoothing=distortion_correction_smoothing,
        SyN_shrink_factors=distortion_correction_shrink_factors,
        noise_mask_dilation_size=noise_mask_dilation_size,
        noise_mask_iterations=noise_mask_iterations,
        noise_mask_sigma=noise_mask_sigma,
        warp_direction=warp_direction,
        autobox_mask=autobox_mask,
    )

    # create pipeline
    pipeline = Pipeline(
        [
            ("start", make_ref_epi_bet_stage),
            ("start", weight_mask_and_autobox_stage),
            ((make_ref_epi_bet_stage, weight_mask_and_autobox_stage), align_affine_epi_to_anat_stage),
            ((weight_mask_and_autobox_stage, align_affine_epi_to_anat_stage), distortion_correction_stage),
        ]
    )

    # run pipeline
    pipeline.run()

    # return results
    return pipeline.results
