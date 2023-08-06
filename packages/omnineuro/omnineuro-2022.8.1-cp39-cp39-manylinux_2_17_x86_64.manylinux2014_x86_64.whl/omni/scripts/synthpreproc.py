import logging
import argparse
from omni.pipelines.logging import setup_logging
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Run a full preprocessing pipeline with Synth distortion correction.\n{0}".format(
            BASE_DOC_URL + "synth/pipelines/synthpreproc.html"
        ),
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 03/28/2021",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_output_path(parser, "-o", required=True, help=synthpreproc_output_path)
    arg_t1(parser, "-x", required=True, help=synthpreproc_t1)
    arg_t2(parser, "-y", required=True, help=synthpreproc_t2)
    arg_func(parser, "-f", required=True, help=synthpreproc_func)
    arg_bids_sidecar(parser, "-b", required=True, help=synthpreproc_bids_sidecar)
    arg_log_file(parser)
    arg_ref(parser)
    arg_bet_method(parser)
    arg_program(parser)
    arg_dilation_size(parser)
    arg_debias_params_anat(parser)
    arg_debias_params_func(parser)
    arg_fractional_intensity_threshold_anat(parser)
    arg_fractional_intensity_threshold_func(parser)
    arg_moco(parser)
    arg_use_allineate(parser)
    arg_loops(parser, "-l")
    arg_subsample(parser)
    arg_borders(parser)
    arg_initial_synth_model(parser)
    arg_final_synth_model(parser)
    arg_bandwidth(parser, "-p")
    arg_skip_affine(parser)
    arg_skip_synthtarget_affine(parser)
    arg_resolution_pyramid(parser)
    arg_synthtarget_max_iterations(parser, "-d")
    arg_synthtarget_err_tol(parser)
    arg_synthtarget_step_size(parser)
    arg_resample_resolution(parser)
    arg_sigma_t2(parser)
    arg_distortion_correction_smoothing(parser)
    arg_distortion_correction_shrink_factors(parser)
    arg_distortion_correction_step_size(parser)
    arg_warp_direction(parser)
    arg_data_resolution(parser)
    arg_noise_mask_iterations(parser)
    arg_noise_mask_dilation_size(parser)
    arg_noise_mask_sigma(parser, "-s")
    arg_atlas(parser)
    arg_atlas_label(parser)

    # set common arguments
    command.set_common(parser)

    # return parser
    return parser


def main():
    # generate the parser
    parser = generate_parser()

    # call parser
    args = parser.parse_args()

    # call common parser
    command.parse_common(args, parser)

    # setup env
    command.set_env(args)

    # setup logging
    setup_logging(args.log_file)

    # log arguments
    logging.info(args)

    # import pipeline after we set the threads
    from omni.pipelines.preprocessing import pre_proc

    # argument checks
    if len(args.loops) != len(args.subsample):
        raise ValueError("loops and subsample must have equal length.")
    if len(args.resolution_pyramid) != len(args.synthtarget_max_iterations):
        raise ValueError("resolution_pyramid and synthtarget_max_iterations must have equal length.")
    if len(args.synthtarget_max_iterations) != len(args.synthtarget_err_tol):
        raise ValueError("synthtarget_max_iterations and synthtarget_err_tol must have equal length.")
    if len(args.synthtarget_max_iterations) != len(args.synthtarget_step_size):
        raise ValueError("synthtarget_max_iterations and synthtarget_step_size must have equal length.")

    # run pre_proc
    pre_proc(**vars(args))
