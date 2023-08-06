# pylint: disable=unused-wildcard-import
from typing import List, Dict
import nibabel as nib
from memori import Stage, Pipeline, redefine_result_key
from memori.helpers import *
from omni.register import grab_slice_encoding_dir
from .align import deoblique_func, create_reference_and_moco
from .normalize import debias
from .segmentation import brain_extraction
from .masks import autobox_and_normalize


@create_output_path
@use_abspaths
@use_output_path_working_directory
@create_symlinks_to_input_files()
def func_proc(
    output_path: str,  # pylint: disable=dangerous-default-value
    func: str,
    TR: float,
    moco: str = "allineate",
    use_allineate: bool = True,
    slice_times: List = None,
    fractional_intensity_threshold_func: float = 0.5,
    debias_params_func: str = "[200,3,1x1x1,3]",
    loops: List[int] = [1, 1, 1],
    subsample: List[int] = [5, 3, 1],
    borders: List[int] = [1, 1, 1],
    initial_warp_field: str = None,
    **kwargs,
) -> Dict:
    """Functional processing pipeline

    Parameters
    ----------
    output_path: str
        Output path to write out files to.
    func: str
        Functional image.
    TR: float
        Repetition time of scan.
    moco: str
        Motion correction method to use.
    use_allineate : bool
        Sets whether to use 3dAllineate for framewise alignment instead.
    slice_times: List
        List of slice times.
    fractional_intensity_threshold: float
        Fractional intensity threshold for bet.
    debias_params_func: str
        Custom spline fitting string.
    loops: List[int]
        Number of loops for SpaceTimeRealign.
    subsample: List[int]
        Subsampling for SpaceTimeRealign.
    borders: List[int]
        borders for SpaceTimeRealign
    initial_warp_field: str
        An initial warp field for distortion correction, to be used to provide more accurate brain extraction.

    Returns
    -------
    Dict
        Dictionary of results.
    """
    # grab the slice encoding direction (it's probably 2)
    sed = grab_slice_encoding_dir(nib.load(func))

    # create stages
    deoblique_func_stage = Stage(
        deoblique_func,
        stage_outputs=[
            "func_do",
        ],
        hash_output="func_proc_0_deoblique_func",
        output_path="func_proc_0_deoblique_func",
    )
    create_reference_and_moco_stage = Stage(
        create_reference_and_moco,
        stage_outputs=["func_do_moco", "ref_func", "rigid_body_params"],
        hash_output="func_proc_1_create_reference_and_moco",
        output_path="func_proc_1_create_reference_and_moco",
        TR=TR,
        use_allineate=(moco == "allineate"),
        slice_times=slice_times,
        sed=sed,
        loops=loops,
        subsample=subsample,
        borders=borders,
    )
    debias_stage = Stage(
        debias,
        stage_outputs=["ref_func_debias"],
        hash_output="func_proc_2_debias",
        output_path="func_proc_2_debias",
        spline_fit=debias_params_func,
    )
    brain_extraction_stage = Stage(
        brain_extraction,
        stage_outputs=["ref_func_debias_mask", "ref_func_debias_bet"],
        hash_output="func_proc_3_brain_extraction",
        output_path="func_proc_3_brain_extraction",
        fractional_intensity_threshold=fractional_intensity_threshold_func,
        initial_warp_field=initial_warp_field,
    )
    autobox_and_normalize_stage = Stage(
        autobox_and_normalize,
        stage_outputs=[
            "ref_func_debias_ab",
            "ref_func_debias_bet_ab",
            "ref_func_debias_mask_ab",
            "func_do_moco_ab",
            "func_do_ab",
        ],
        hash_output="func_proc_4_autobox_and_normalize",
        output_path="func_proc_4_autobox_and_normalize",
    )

    # create pipeline
    func_pipeline = Pipeline(
        [
            ("start", deoblique_func_stage),
            (deoblique_func_stage, create_reference_and_moco_stage),
            (create_reference_and_moco_stage, debias_stage),
            (debias_stage, brain_extraction_stage),
            (
                (deoblique_func_stage, create_reference_and_moco_stage, debias_stage, brain_extraction_stage),
                autobox_and_normalize_stage,
            ),
        ]
    )

    # run pipeline
    func_pipeline.run(func=func)

    # return results
    return func_pipeline.results


def func_to_epi_results(results: Dict, use_allineate: bool) -> Dict:
    """Converts results of functional pipeline for input into EPI pipeline.

    Parameters
    ----------
    results: Dict
        Results dictionary from functional pipeline.
    use_allineate: bool
        Specify inputs when 3dAllineate used for framewise alignment.

    Returns
    -------
    Dict
        Converted dictionary for EPI pipeline input.
    """
    # change keys
    results = redefine_result_key(results, "ref_func_debias_ab", "ref_epi")
    results = redefine_result_key(results, "ref_func_debias_bet_ab", "ref_epi_bet")
    results = redefine_result_key(results, "ref_func_debias_mask_ab", "ref_epi_bet_mask")
    if use_allineate:  # if allineate enabled set raw epi to deobliques/autoboxed
        results = redefine_result_key(results, "func_do_ab", "epi")
    else:  # in realign4d mode, use post transformed epi
        results = redefine_result_key(results, "func_do_moco_ab", "epi")
    results = redefine_result_key(results, "func_do_moco_ab", "epi_moco")

    # return new results
    return results
