from typing import Dict
from memori.helpers import *
from memori import Stage, Pipeline, redefine_result_key
from .align import align_atlas, align_anat, deoblique_anat
from .normalize import debias
from .segmentation import brain_extraction
from .masks import weight_mask_and_autobox, weight_mask_and_autobox2


@create_output_path
@use_abspaths
@use_output_path_working_directory
@create_symlinks_to_input_files()
def anat_proc(
    output_path: str,
    t1: str,
    t2: str,
    ref: str = "T1",
    program: str = "fsl",
    atlas: str = "mni",
    atlas_label: str = "atlas",
    use_eye_mask: bool = True,
    dilation_size: int = 30,
    debias_params_anat: str = "[100,3,1x1x1,3]",
    fractional_intensity_threshold_anat: float = 0.5,
    bet_method: str = "Norm",
    **kwargs,
) -> Dict:
    """Anatomical processing pipeline.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    t1 : str
        T1 image.
    t2 : str
        T2 image.
    ref : str
        Set the image to use as a reference [T1/T2].
    program : str
        Program to use for alignment
        ('afni': AFNI 3dAllineate or 'fsl': fsl flirt).
    atlas : str
        Atlas to align to.
    atlas_label : str
        Label suffix for atlas outputs.
    use_eye_mask : str
        Enhance anatomical weight mask with eye mask.
    dilation_size : int
        Size of dilation kernel for weight mask.
    debias_params_anat : str
        Custom spline fitting string.
    fractional_intensity_threshold_anat : float
        Set fractional intensity threshold for bet.
    bet_method : str
        Method of brain extraction.

    Returns
    -------
    Dict
        Dictionary of results.
    """
    # create stages
    deoblique_anat_stage = Stage(
        deoblique_anat,
        stage_outputs=["t1_do", "t2_do"],
        hash_output="anat_proc_0_deoblique_anat",
        output_path="anat_proc_0_deoblique_anat",
    )
    debias_stage = Stage(
        debias,
        stage_outputs=["t1_debias", "t2_debias"],
        hash_output="anat_proc_1_debias",
        output_path="anat_proc_1_debias",
        spline_fit=debias_params_anat,
    )
    align_anat_stage = Stage(
        align_anat,
        stage_outputs=["t1_debias", "t2_debias", "anat_align_affine"],
        hash_output="anat_proc_2_align_anat",
        output_path="anat_proc_2_align_anat",
        ref=ref,
        program=program,
    )
    brain_extraction_stage = Stage(
        brain_extraction,
        stage_outputs=["anat_bet_mask", "anat_eye_mask", "t1_debias_bet", "t2_debias_bet"],
        hash_output="anat_proc_3_brain_extraction",
        output_path="anat_proc_3_brain_extraction",
        use_eye_mask=use_eye_mask,
        fractional_intensity_threshold=fractional_intensity_threshold_anat,
        method=bet_method,
    )
    align_atlas_stage = Stage(
        align_atlas,
        stage_outputs=["t1_atlas", "t2_atlas", "atlas_align_affine"],
        hash_output="anat_proc_4_align_atlas",
        output_path="anat_proc_4_align_atlas",
        atlas=atlas,
        atlas_label=atlas_label,
        ref=ref,
        program=program,
    )
    weight_mask_and_autobox_stage = Stage(
        weight_mask_and_autobox2,
        stage_outputs=[
            "weight_mask",
            "weight_mask_ab",
            "anat_bet_mask_ab",
            "t1_debias_ab",
            "t2_debias_ab",
            "t1_debias_ab_sat_lce",
            "t2_debias_ab_sat_lce",
            "t1_debias_ab_sat_lce_bet",
            "t2_debias_ab_sat_lce_bet",
        ],
        hash_output="anat_proc_5_weight_mask_and_autobox",
        output_path="anat_proc_5_weight_mask_and_autobox",
        dilation_size=dilation_size,
    )

    # create pipeline
    anat_pipeline = Pipeline(
        [
            ("start", deoblique_anat_stage),
            (deoblique_anat_stage, debias_stage),
            (debias_stage, align_anat_stage),
            (align_anat_stage, brain_extraction_stage),
            ((brain_extraction_stage, align_anat_stage, debias_stage), align_atlas_stage),
            ((brain_extraction_stage, align_anat_stage), weight_mask_and_autobox_stage),
        ]
    )

    # run pipeline
    anat_pipeline.run(t1=t1, t2=t2)

    # results
    return anat_pipeline.results


def anat_to_epi_results(results: Dict) -> Dict:
    """Converts results of anatomical pipeline for input into EPI pipeline.

    Parameters
    ----------
    results : Dict
        Results dictionary from anatomical pipeline.

    Returns
    -------
    Dict
        Converted dictionary for EPI pipeline input.
    """
    # change keys
    results = redefine_result_key(results, "weight_mask_ab", "anat_weight_mask")
    results = redefine_result_key(results, "anat_bet_mask_ab", "anat_bet_mask")
    results = redefine_result_key(results, "t1_debias_ab_sat_lce", "t1")
    results = redefine_result_key(results, "t2_debias_ab_sat_lce", "t2")
    results = redefine_result_key(results, "t1_debias_ab_sat_lce_bet", "t1_bet")
    results = redefine_result_key(results, "t2_debias_ab_sat_lce_bet", "t2_bet")

    # return new results
    return results
