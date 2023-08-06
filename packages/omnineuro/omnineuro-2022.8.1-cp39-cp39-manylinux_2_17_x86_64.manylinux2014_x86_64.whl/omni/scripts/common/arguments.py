"""
    Module containing functions for adding arguments to scripts.

    Some scripts will have similar arguments. By combining all
    available arguments in one file, we can create a common interface
    for all scripts.
"""
from argparse import ArgumentParser
from typing import Callable
from omni import warp
from omni.pipelines.func.align import moco
from .help import *
from omni.version import __version__


class Argument:  # pylint: disable=too-few-public-methods
    """Argument for ArgumentParser.

    Methods
    -------
    create:
        Creates a callable that adds an argument to a given parser.
    """

    @classmethod
    def create(cls, flag_name: str, default_help: str = "", **kwargs) -> Callable:
        """Create an argument for ArgumentParser.

        Parameters
        ----------
        flag_name: str
            Name of argument flag to add.
        default_help: str
            Default help text to use.

        Returns
        -------
        Callable
            A function to call with parser to add the argument.
        """
        # rename class kwargs to not conflict with function kwargs
        class_kwargs = kwargs

        # construct add_argument function
        def add_argument(parser: ArgumentParser, *args, positional_arg: bool = False, **kwargs):
            # remove help from kwargs if it exists
            func_kwargs = kwargs.copy()
            if "help" in func_kwargs:
                del func_kwargs["help"]

            # add argument to parser
            parser.add_argument(
                *args,
                "--%s" % flag_name if not positional_arg else flag_name,
                help=default_help if "help" not in kwargs else kwargs["help"],
                **class_kwargs,
                **func_kwargs,
            )

        # return the argument function
        return add_argument


arg_affine = Argument.create("affine", default_help="Affine tranform (omni format).")
arg_afnify = Argument.create("afnify", default_help="Convert input to afni affine format.", action="store_true")
arg_anat_bet_mask = Argument.create("anat_bet_mask", default_help="Brain mask in anatomical space.")
arg_anat_bet_mask_epispace = Argument.create(
    "anat_bet_mask_epispace", default_help=synthnoisemask_anat_bet_mask_epispace
)
arg_anat_eye_mask = Argument.create("anat_eye_mask", default_help="Eye mask in anatomical space.")
arg_anat_weight_mask = Argument.create(
    "anat_weight_mask", default_help="An anatomical brain mask that is weighted around the skull."
)
arg_atlas = Argument.create("atlas", default_help=common_atlas, default="mni")
arg_atlas_label = Argument.create(
    "atlas_label",
    default_help="Label suffix for atlas aligned files in output when a custom path is specified.",
    default="atlas",
)
arg_bandwidth = Argument.create("bandwidth", default_help=common_bandwidth, default=8, type=float)
arg_bet_method = Argument.create("bet_method", default_help=common_bet_method, default="Norm", choices=["Norm", "T1"])
arg_bids_path = Argument.create(
    "bids_path", default_help="The directory with the input dataset formatted according to the BIDS standard."
)
arg_bids_sidecar = Argument.create(
    "bids_sidecar", default_help="A BIDS sidecar .json file containing metadata related to the EPI image."
)
arg_borders = Argument.create(
    "borders", default_help="Sets the border width for SpaceTimeRealign.", nargs=3, type=int, default=[1, 1, 1]
)
arg_combine_sessions = Argument.create(
    "combine_sessions",
    default_help="Combine sessions if a session is missing an anatomical image.",
    action="store_true",
)
arg_database = Argument.create(
    "database", default_help="Set database path for BIDS input (Default is to use BIDS input path)."
)
arg_data_resolution = Argument.create("data_resolution", default_help=common_data_resolution, type=float)
arg_debias_params_anat = Argument.create(
    "debias_params_anat", default_help=common_debias_params_anat, default="[100,3,1x1x1,3]"
)
arg_debias_params_dwi = Argument.create(
    "debias_params_dwi", default_help="BSpline fit option for N4BiasFieldCorrection (Dwi).", default="[200,3,3x3x3,3]"
)
arg_debias_params_func = Argument.create(
    "debias_params_func", default_help=common_debias_params_func, default="[200,3,3x3x3,3]"
)
arg_dilation_size = Argument.create("dilation_size", default_help=common_dilation_size, default=30, type=int)
arg_dims = Argument.create(
    "dims", default_help="Dims to reshape columns into.", nargs=3, default=[256, 256, 224], type=int
)
arg_distortion_correction_smoothing = Argument.create(
    "distortion_correction_smoothing", default_help="Smoothing factors for SyN warp.", default="2x1x0x0"
)
arg_distortion_correction_shrink_factors = Argument.create(
    "distortion_correction_shrink_factors", default_help="Shrink factors for SyN warp.", default="4x3x2x1"
)
arg_distortion_correction_step_size = Argument.create(
    "distortion_correction_step_size",
    default_help="Gradient descent step sizes for distortion correction.",
    default=[3.0, 1.0, 0.1],
    nargs="+",
    type=float,
)
arg_dryrun = Argument.create("dryrun", default_help="Run pipeline without any outputs.", action="store_true")
arg_epi = Argument.create("epi", default_help=common_epi)
arg_err_tol = Argument.create("err_tol", default_help=common_err_tol, default=1e-4, type=float)
arg_final_dwi_resolution = Argument.create(
    "final_dwi_resolution",
    default_help="Specify final resample resolution for dwi images (Use 0 for Native Resolution).",
    default=0,
    type=float,
)
arg_final_func_res = Argument.create(
    "final_func_resolution",
    default_help="Specify final resample resolution for functional images (Use 0 for Native Resolution).",
    default=0,
    type=float,
)
arg_final_synth_model = Argument.create(
    "final_synth_model", default_help=common_final_synth_model, default="rbf(0;12)+rbf(1;12)+rbf(0;12)*rbf(1;12)"
)
arg_initial_affine = Argument.create(
    "initial_affine", default_help="Initial affine transform (omni format) for registration.", default=None
)
arg_fix_initial_warp_field = Argument.create(
    "fix_initial_warp_field", default_help="fix initial warp field", action="store_true"
)
arg_fixed_regress = Argument.create(
    "fixed_regress",
    default_help="Fix the regression parameters with given regress file "
    "(must be dimensionally consistent with the model).",
)
arg_fourd_img = Argument.create("fourd_img", "A 4D image for joint slice time/motion correction.")
arg_fractional_intensity_threshold_anat = Argument.create(
    "fractional_intensity_threshold_anat",
    default_help=common_fractional_intensity_threshold_anat,
    default=0.5,
    type=float,
)
arg_fractional_intensity_threshold_dwi = Argument.create(
    "fractional_intensity_threshold_dwi",
    "Fractional intensity threshold for brain extraction tool (Dwi).",
    default=0.5,
    type=float,
)
arg_fractional_intensity_threshold_func = Argument.create(
    "fractional_intensity_threshold_func",
    default_help=common_fractional_intensity_threshold_func,
    default=0.5,
    type=float,
)
arg_fslify = Argument.create(
    "fslify",
    default_help="Convert input to fsl affine format (must provide target/source arguments).",
    action="store_true",
)
arg_func = Argument.create("func", "Functional Image.")
arg_initial_synth_model = Argument.create(
    "initial_synth_model", default_help=common_initial_synth_model, default="rbf(0;4)+rbf(1;4)+rbf(0;4)*rbf(1;4)"
)
arg_initial_warp_field = Argument.create("initial_warp_field", default_help=common_initial_warp_field)
arg_in_warp_type = Argument.create("in_warp_type", default_help="Input warp type.", choices=warp.CHOICES)
arg_input = Argument.create("input", default_help="Path to input file.")
arg_input_affine = Argument.create("input_affine", default_help="Input affine file to convert.")
arg_input_image = Argument.create("input_image", default_help="Input image.")
arg_input_images = Argument.create(
    "input_images", default_help="Input images to construct interaction matrix on.", nargs="+"
)
arg_interaction_model = Argument.create(
    "interaction_model",
    default_help="A string or .model file specifying how " "the interation operator should be constructed (F).",
)
arg_invert = Argument.create("invert", "Invert the provided affine file.", action="store_true")
arg_limits = Argument.create(
    "limits",
    default_help="Extraction limits (should be specified as '[x1:x2,y1:y2,z1:y2,...]'"
    "Must match the dimensions of the source image, this basically just uses numpy indexing.",
)
arg_log_file = Argument.create("log_file", default_help=common_log_file)
arg_loops = Argument.create("loops", default_help=common_loops, default=[1, 1, 1], nargs="+", type=int)
arg_max_iterations = Argument.create("max_iterations", default_help=common_max_iterations, default=200, type=int)
arg_moco = Argument.create("moco", default_help=common_moco, default="allineate", choices=moco)
arg_noise_mask_dilation_size = Argument.create(
    "noise_mask_dilation_size", default_help=common_noise_mask_dilation_size, default=2, type=int
)
arg_noise_mask_iterations = Argument.create(
    "noise_mask_iterations", default_help=common_noise_mask_iterations, default=12, type=int
)
arg_noise_mask_sigma = Argument.create("noise_mask_sigma", default_help=common_noise_mask_sigma, default=2, type=float)
arg_no_register = Argument.create("no_register", default_help="Skips registration procedure.", action="store_true")
arg_omnify = Argument.create("omnify", default_help="Convert input to omni affine format.", action="store_true")
arg_out_warp_type = Argument.create("out_warp_type", default_help="Output warp type.", choices=warp.CHOICES)
arg_output = Argument.create("output", default_help="Path to output file.")
arg_output_image = Argument.create("output_image", default_help="Output image.")
arg_output_intmat = Argument.create("output_intmat", default_help="Output interaction matrices.", action="store_true")
arg_output_path = Argument.create("output_path", default_help="The directory where output files should be stored.")
arg_output_prefix = Argument.create("output_prefix", default_help="A prefix for all the output files.")
arg_participant_label = Argument.create(
    "participant_label",
    default_help="The label(s) of the participant(s) that should be analyzed. The label "
    "corresponds to sub-<participant_label> from the BIDS spec "
    '(so it does not include "sub-"). If this parameter is not '
    "provided all subjects should be analyzed. Multiple "
    "participants can be specified with a space separated list.",
    nargs="+",
)
arg_phase_encoding_direction = Argument.create(
    "phase_encoding_direction",
    default_help="Sets the phase encoding direction.",
    choices=["x", "y", "z", "none"],
    default="none",
)
arg_program = Argument.create("program", default_help=common_program, choices=["fsl", "afni"], default="fsl")
arg_ref = Argument.create("ref", default_help=common_ref, default="T1")
arg_ref_epi = Argument.create("ref_epi", default_help="Reference EPI image (Single frame and [0,1] normalized).")
arg_ref_epi_bet_mask = Argument.create("ref_epi_bet_mask", default_help="Brain mask of reference EPI image.")
arg_ref_idx = Argument.create(
    "ref_idx", default_help="Index of reference to use for SpaceTimeRealign.", default=0, type=int
)
arg_regression_weight_mask = Argument.create(
    "regression_weight_mask", default_help="Regression weight mask for regression model."
)
arg_regression_output = Argument.create(
    "regression_output", default_help="SynthTarget regression output (Before blurring operator)."
)
arg_reset_database = Argument.create(
    "reset_database", default_help="Delete BIDS database files if they exist.", action="store_true"
)
arg_resample_resolution = Argument.create(
    "resample_resolution",
    default_help="Resample resolution space to do warps on (mm). It is recommended you use the same resolution as the "
    "anatomical images (T1w/T2w images).",
    default=1,
    type=float,
)
arg_resolution_pyramid = Argument.create(
    "resolution_pyramid", default_help=common_resolution_pyramid, default=[4, 2, 1], nargs="+", type=float
)
arg_rigid_transform = Argument.create(
    "rigid_transform",
    default_help="Generates a omni affine that does the specified transform (angles are in degrees, "
    "translations in physical coordinates (usually mm).",
    metavar=("ANGLEX", "ANGLEY", "ANGLEZ", "TX", "TY", "TZ"),
    nargs=6,
    type=float,
)
arg_sigma_t2 = Argument.create("sigma_t2", default_help=common_sigma_t2, default=0.5, type=float)
arg_single_rest_run = Argument.create(
    "single_rest_run",
    default_help="Replicates the paper and does only single rest run per subject.",
    action="store_true",
)
arg_six_body = Argument.create("six_body", default_help="convert affine list to rigid body list", action="store_true")
arg_skip_affine = Argument.create("skip_affine", default_help=common_skip_affine, action="store_true")
arg_skip_synthtarget_affine = Argument.create(
    "skip_synthtarget_affine", default_help=common_skip_synthtarget_affine, action="store_true"
)
arg_skip_database = Argument.create("skip_database", default_help="Skip database construction.", action="store_true")
arg_skip_validation = Argument.create(
    "skip_validation", default_help="Skip validation of BIDS input.", action="store_true"
)
arg_source = Argument.create("source", default_help="Specifies source image to calculate fsl affine over.")
arg_step_size = Argument.create("step_size", default_help=common_step_size, default=1e-3, type=float)
arg_subsample = Argument.create("subsample", default_help=common_subsample, default=[5, 3, 1], nargs="+", type=int)
arg_synthtarget_err_tol = Argument.create(
    "synthtarget_err_tol", default_help=common_err_tol, default=[1e-4, 1e-4, 5e-4], nargs="+", type=float
)
arg_synthtarget_max_iterations = Argument.create(
    "synthtarget_max_iterations", default_help=common_max_iterations, default=[2000, 500, 100], nargs="+", type=int
)
arg_synthtarget_step_size = Argument.create(
    "synthtarget_step_size", default_help=common_step_size, default=[1e-3, 1e-3, 1e-3], nargs="+", type=float
)
arg_synthnoisemask_output = Argument.create("output", default_help=synthnoisemask_output)
# Arguments for omni_synthregressionmask
arg_synthregressionmask_dil_anat_weight_mask = Argument.create(
    "dil_anat_bet_mask", default_help=synthregressionmask_dil_anat_weight_mask
)
arg_synthregressionmask_anat_bet_mask = Argument.create("anat_bet_mask", default_help=synthregressionmask_anat_bet_mask)
arg_synthregressionmask_affine = Argument.create("anat_to_epi_affine", default_help=synthregressionmask_affine)
arg_synthregressionmask_warp = Argument.create("warp", default_help=synthregressionmask_warp)
arg_synth_image = Argument.create("synth_image", default_help="Synthetic image.")
arg_synth_image_target_space = Argument.create(
    "synth_image_target_space", default_help="Synthetic image aligned to target space."
)
arg_t1 = Argument.create("t1", default_help="A T1 image.")
arg_t2 = Argument.create("t2", default_help="A T2 image.")
arg_t1_debias = Argument.create("t1_debias", default_help="A T1 image that is bias field corrected.")
arg_t2_debias = Argument.create("t2_debias", default_help="A T2 image that is bias field corrected.")
arg_target = Argument.create("target", default_help="Specifies target image to calculate fsl affine over.")
arg_target_image = Argument.create("target_image", default_help="Target image.")
arg_test_mode = Argument.create("test_mode", default_help="Runs a single session, then quits.", action="store_true")
arg_tone_curve = Argument.create("tone_curve", default_help=common_tone_curve, action="store_true")
arg_tone_curve_mask = Argument.create("tone_curve_mask", default_help=common_tone_curve_mask)
arg_use_allineate = Argument.create("use_allineate", default_help=common_use_allineate, action="store_true")
arg_use_default_anatomical = Argument.create(
    "use_default_anatomical",
    default_help="If an anatomical image is missing in a session, enabling this flag will assign the "
    "first availiable anatomical to the session.",
    action="store_true",
)
arg_version = Argument.create(
    "version", default_help="Show program's version and exit.", action="version", version=__version__
)
arg_warp = Argument.create(
    "warp", default_help="Forward warp (anat to epi; from the space where anat is affine aligned " "to the epi)."
)
arg_warp_direction = Argument.create(
    "warp_direction", default_help="Warp direction (x, y, z, or none)", default="none", choices=["x", "y", "z", "none"]
)
