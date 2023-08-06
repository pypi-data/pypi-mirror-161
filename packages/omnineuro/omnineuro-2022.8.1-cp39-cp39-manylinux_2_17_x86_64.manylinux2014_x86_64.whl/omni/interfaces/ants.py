from typing import List, Union
from .common import run_process


def antsRegistration(
    warp_prefix: str,
    reference: str,
    source: str,
    warped: str = None,
    inverse_warped: str = None,
    grad_step: float = 1,
    update_field_var: float = 0,
    total_field_var: float = 0,
    metric: str = "CC",
    rad_bin: int = 10,
    convergence: str = "500x200x200x0",
    threshold: float = 1e-6,
    threshold_window: int = 15,
    smoothing: str = "2x1x0x0",
    shrink_factors: str = "4x3x2x1",
    restrict_deform: str = "1x1x1",
    reference_mask: str = None,
    source_mask: str = None,
    initial_warp: str = None,
    other_args: str = None,
):
    """antsRegistration interface for Ants Syn Warp

    Parameters
    ----------
    warp_prefix: str
        Prefix of output warp.
    reference: str
        Reference image to align.
    source: str
        Source image to align.
    warped: str
        Warped source image.
    inverse_warped: str
        Inverse Warped reference image.
    grad_step: float
        Gradient step size for optimization.
    update_field_var: float
        Update field variance for Syn algorithm.
    total_field_var: float
        Total field variance for SyN algorithm.
    metric: str
        Optimization metric to use.
    rad_bin: int
        Radius or number of bins of metric.
    convergence: str
        Number of iterations to use at each level of optimization.
    threshold: float
        Stopping criterion for optimization.
    threshold_window: int
        Window size for optimization.
    smoothing: str
        Smoothing kernel size for each level of optimization.
    shrink_factors: str
        Resampling factor for each level of optimization.
    restrict_deform: str
        1 to allow warp in a direction; 0 to restrict warp in a direction.
    reference_mask: str
        Path to a reference extent mask.
    source_mask: str
        Path to a source extent mask.
    initial_warp: str
        Initializes SyN registration with a warp.
    other_args: str
        Other arguments to pass in.
    """
    return run_process(
        "antsRegistration "
        "-d 3 "
        "-u 1 "
        "-o [{0}{1}{2}] "
        "-n BSpline[5] "
        "-w [0.005,0.995] "
        "--transform Syn[{3},{18},{4}] "
        "--metric {5}[{6},{7},1,{8}] "
        "-c [{9},{10},{11}] "
        "-s {12} "
        "-f {13} "
        "-g {14} "
        "{15}{16}{17}-v 1".format(
            warp_prefix,  # required arg
            ",{}".format(warped) if warped else "",
            ",{}".format(inverse_warped) if inverse_warped else "",
            grad_step,
            total_field_var,
            metric,
            reference,  # required arg
            source,  # required arg
            rad_bin,
            convergence,
            threshold,
            threshold_window,
            smoothing,
            shrink_factors,
            restrict_deform,
            "-x [{},{}] ".format(reference_mask, source_mask) if reference_mask and source_mask else "",
            "-r {} ".format(initial_warp) if initial_warp else "",
            "{} ".format(other_args) if other_args else "",
            update_field_var,
        )
    )


def antsApplyTransform(
    prefix: str,
    reference: str,
    source: str,
    transforms: Union[List, str],
    composite_warp: bool = False,
    other_args: str = None,
):
    """Apply a transform with antsApplyTransforms.

    Parameters
    ----------
    prefix: str
        Prefix of output image/warp
    reference: str
        Reference image to transform.
    source: str
        Source image to transform.
    transforms: Union[List, str]
        String of transforms to apply.
    composite_warp: bool
        Boolean indicating whether to output the image
        (False) or warp (True).
    other_args: str
        Other arguments to pass in.
    """
    return run_process(
        "antsApplyTransforms "
        "-d 3 "
        "-o {0} "
        "-r {1} "
        "-i {2} "
        "-n BSpline[5] "
        "-t {3} "
        "{4}-v 1".format(
            "[{},1]".format(prefix) if composite_warp else prefix,
            reference,
            source,
            " ".join(transforms) if isinstance(transforms, list) else transforms,
            "{} ".format(other_args) if other_args else "",
        )
    )


def N4BiasFieldCorrection(out_file: str, in_file: str, bspline_fit: str = None, other_args: str = None):
    """Bias Field Correction.

    Parameters
    ----------
    out_file: str
        Bias field corrected file.
    in_file: str
        File to bias field correct.
    bspline_fit: str
        Custom spline fit string.
    other_args: str
        Other arguments to pass in.
    """
    return run_process(
        "N4BiasFieldCorrection -d 3 -i {} -o {} {}{}-v 1".format(
            in_file,
            out_file,
            "-b {} ".format(bspline_fit) if bspline_fit else "",
            "{} ".format(other_args) if other_args else "",
        )
    )
