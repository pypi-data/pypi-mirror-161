from typing import List
from memori import Stage, Pipeline
from memori.helpers import *
from .align import align_affine_epi_to_anat, combine_transforms, distortion_correction


@create_output_path
@use_abspaths
@use_output_path_working_directory
@create_symlinks_to_input_files()
def epi_proc(
    output_path: str,  # pylint: disable=dangerous-default-value
    epi: str,
    epi_moco: str,
    ref_epi: str,
    ref_epi_bet: str,
    ref_epi_bet_mask: str,
    anat_bet_mask: str,
    anat_weight_mask: str,
    atlas_align_affine: str,
    t1: str = None,
    t2: str = None,
    t1_bet: str = None,
    t2_bet: str = None,
    initial_synth_model: str = "rbf(0;4)+rbf(1;4)+rbf(0;4)*rbf(1;4)",
    final_synth_model: str = "rbf(0;12)+rbf(1;12)+rbf(0;12)*rbf(1;12)",
    program: str = "fsl",
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
    distortion_correction_step_size: List[float] = [3, 1, 0.1],
    distortion_correction_smoothing: str = "2x1x0x0",
    distortion_correction_shrink_factors: str = "4x3x2x1",
    warp_direction: str = "none",
    noise_mask_dilation_size: int = 2,
    noise_mask_iterations: int = 20,
    noise_mask_sigma: float = 2,
    data_resolution: float = None,
    atlas: str = "mni",
    atlas_label: str = "atlas",
    use_allineate: bool = False,
    rigid_body_params: str = None,
    **kwargs,
):
    """EPI pipeline.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    epi : str
        EPI image to apply final transforms to.
    epi_moco : str
        EPI image that has been motion corrected/framewise aligned.
    ref_epi : str
        Reference EPI image.
    ref_epi_bet : str
        Skullstripped reference EPI image.
    ref_epi_bet_mask : str
        Reference EPI brain mask.
    anat_bet_mask : str
        Anatomical brain mask.
    anat_weight_mask : str
        Anatomical weight mask.
    atlas_align_affine : str
        Affine alignment file for anat to atlas (afni)
    t1: str
        T1.
    t2 : str
        T2.
    t1_bet : str
        T1 skullstripped.
    t2_bet : str
        T2 skullstripped.
    inital_synth_model : str
        Initial model used to generate synthetic image.
    final_synth_model : str
        Final model used to generate synthetic image.
    program : str
        Program to use for affine alignment.
    bandwidth : int
        Bandwidth for Epanechnikov kernel.
    initial_affine : str
        Initial affine alignment file.
    skip_affine : bool
        Skip affine alignment step.
    skip_synthtarget_affine : bool
        Skip synthtarget affine alignment step.
    resolution_pyramid : List[float]
        Resampling pyramid to use for affine alignment (mm).
    synthtarget_max_iterations : List[int]
        Max iterations for each SynthTarget call.
    synthtarget_err_tol: List[float]
        Error tolerance level for each SynthTarget call.
    synthtarget_step_size: List[float]
        Step size for gradient descent.
    resample_resolution : float
        Resample resolution space to do warps on (mm).
    sigma_t2 : float
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
    atlas : str
        Set atlas to align to.
    atlas_label : str
        Label suffix for atlas outputs.
    data_resolution : float
        Resolution to resample the data for output (mm).
    use_allineate: bool
        Specifies that 3DAllineate was used for framewise alignment.
    rigid_body_params: str
        Rigid body transform to use if 3DAllineate enabled.

    Returns
    -------
    Dict
        Dictionary of results.
    """
    # create stages
    align_affine_epi_to_anat_stage = Stage(
        align_affine_epi_to_anat,
        stage_outputs=["final_epi_to_anat_affine", "final_anat_to_epi_affine"],
        hash_output="epi_proc_0_align_affine_epi_to_anat",
        output_path="epi_proc_0_align_affine_epi_to_anat",
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
        hash_output="epi_proc_1_distortion_correction",
        output_path="epi_proc_1_distortion_correction",
        epi_moco=epi_moco,
        ref_epi=ref_epi,
        t1=t1,
        t2=t2,
        anat_bet_mask=anat_bet_mask,
        anat_weight_mask=anat_weight_mask,
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
    )
    combine_transforms_stage = Stage(
        combine_transforms,
        stage_outputs=["raw_epi_atlas"],
        hash_output="epi_proc_2_combine_transforms",
        output_path="epi_proc_2_combine_transforms",
        raw_epi=epi,
        atlas_align_affine=atlas_align_affine,
        atlas=atlas,
        atlas_label=atlas_label,
        data_resolution=data_resolution,
        use_allineate=use_allineate,
        rigid_body_params=rigid_body_params,
    )

    # create EPI processing pipeline
    epi_pipeline = Pipeline(
        [
            ("start", align_affine_epi_to_anat_stage),
            (align_affine_epi_to_anat_stage, distortion_correction_stage),
            ((align_affine_epi_to_anat_stage, distortion_correction_stage), combine_transforms_stage),
        ]
    )

    # run the pipeline
    epi_pipeline.run(ref_epi_bet=ref_epi_bet, t1_bet=t1_bet, t2_bet=t2_bet)

    # return results
    return epi_pipeline.results
