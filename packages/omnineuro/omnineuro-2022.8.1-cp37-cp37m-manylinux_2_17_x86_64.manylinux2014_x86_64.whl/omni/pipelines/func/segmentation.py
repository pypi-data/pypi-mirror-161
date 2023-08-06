import logging
from memori.pathman import append_suffix, repath
from memori.helpers import create_output_path
from omni.interfaces.afni import NwarpApply
from omni.interfaces.fsl import bet


@create_output_path
def brain_extraction(
    output_path: str, ref_func_debias: str, fractional_intensity_threshold: float = 0.5, initial_warp_field: str = None
):
    """Brain extraction

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    ref_func_debias : str
        Reference functional.
    fractional_intensity_threshold : float
        Fractional intensity threshold for bet.
    initial_warp_field : str
        An initial distortion correction that should be applied before brain extraction

    Returns
    -------
    str
        Functional mask.
    str
        Brain extracted functional.
    """
    # if distortion correction is provided, apply it
    if initial_warp_field:
        ref_func_debias_warped = repath(output_path, append_suffix(ref_func_debias, "warped"))
        NwarpApply(ref_func_debias_warped, ref_func_debias, ref_func_debias, initial_warp_field)
        ref_func_debias = ref_func_debias_warped

    # run bet based on method selected
    logging.info("Running brain extraction...")
    ref_func_debias_bet = append_suffix(repath(output_path, ref_func_debias), "_bet")
    _, ref_func_debias_mask = bet(
        ref_func_debias_bet,  # pylint: disable=unbalanced-tuple-unpacking
        ref_func_debias,
        fractional_intensity_threshold,
        mask=True,
    )

    # return files
    return (ref_func_debias_mask, ref_func_debias_bet)
