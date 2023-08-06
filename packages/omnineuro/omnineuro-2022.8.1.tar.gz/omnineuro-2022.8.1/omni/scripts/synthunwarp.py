import argparse
from omni.pipelines.logging import setup_logging
from memori.pathman import PathManager
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="""
        Runs the SynthUnwarp distortion correction algorithm. See algorithm 2 of the
        Synth paper. This algorithm will produce the following outputs:

            [OUTPUT_PATH]/final_epi2anat_xfm.aff12.1D # affine from epi to anat
            [OUTPUT_PATH]/final_synth2epi_warp.nii.gz # warp from synth to epi
            [OUTPUT_PATH]/final_epi2synth_warp.nii.gz # warp from epi to synth

        The order of the transforms is as follows:

            anat_space <- final_epi2anat_xfm <- final_epi2synth_warp <- epi_space

        For example, to undistort the epi and align it to the anatomical:

            3dNwarpApply -warp final_epi2anat_xfm.aff12.1D \\
            final_epi2synth_warp.nii.gz -source [epi_image] \\
            -master [anat_image] -prefix [unwarped_aligned_epi_image]

        In general, the computed forward warp (final_synth2epi_warp.nii.gz) is provided for
        reference purposes and you will likely not need to use it.

        Note that each of these files are in AFNI format, and are meant to be
        used with AFNI tools.
        """,
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 03/27/2021",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_output_path(parser, "-o", required=True)
    arg_t1_debias(parser, "-x", required=True)
    arg_t2_debias(parser, "-y", required=True)
    arg_anat_bet_mask(parser, "-m", required=True)
    arg_anat_eye_mask(parser, "-i")
    arg_ref_epi(parser, "-r", required=True)
    arg_ref_epi_bet_mask(parser, "-b", required=True)
    arg_epi(parser, "-e", required=True)
    arg_program(parser)
    arg_dilation_size(parser)
    arg_initial_synth_model(parser)
    arg_final_synth_model(parser)
    arg_bandwidth(parser, "-p")
    arg_initial_affine(parser)
    arg_skip_affine(parser)
    arg_skip_synthtarget_affine(parser)
    arg_resolution_pyramid(parser)
    arg_synthtarget_max_iterations(parser, "-d")
    arg_synthtarget_err_tol(parser)
    arg_synthtarget_step_size(parser)
    arg_resample_resolution(parser)
    arg_sigma_t2(parser)
    arg_initial_warp_field(parser)
    arg_distortion_correction_smoothing(parser)
    arg_distortion_correction_shrink_factors(parser)
    arg_distortion_correction_step_size(parser)
    arg_warp_direction(parser)
    arg_noise_mask_dilation_size(parser)
    arg_noise_mask_iterations(parser)
    arg_noise_mask_sigma(parser, "-s")

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

    # setup env before importing registration pipelines
    command.set_env(args)

    # setup logging
    setup_logging()

    # call synthunwarp pipeline
    from omni.pipelines.preprocessing import synthunwarp

    results = synthunwarp(**vars(args))

    # get relevant outputs
    output_path = PathManager(args.output_path)
    final_epi_to_anat_affine_path = PathManager(results["final_epi_to_anat_affine"])
    final_synth_to_epi_warp_path = PathManager(results["final_synth_to_epi_warp"])
    final_epi_to_synth_warp_path = PathManager(results["final_epi_to_synth_warp"])

    # get relative paths
    final_epi_anat_affine_target = final_epi_to_anat_affine_path.relative_to(output_path.absolute())
    final_synth_to_epi_warp_target = final_synth_to_epi_warp_path.relative_to(output_path.absolute())
    final_epi_to_synth_warp_target = final_epi_to_synth_warp_path.relative_to(output_path.absolute())

    # create paths to symlinks
    final_epi_anat_affine_link = output_path / final_epi_to_anat_affine_path.name
    final_synth_to_epi_warp_link = output_path / final_synth_to_epi_warp_path.name
    final_epi_to_synth_warp_link = output_path / final_epi_to_synth_warp_path.name

    # generate symlinks
    try:
        final_epi_anat_affine_link.unlink()
    except FileNotFoundError:
        pass
    try:
        final_synth_to_epi_warp_link.unlink()
    except FileNotFoundError:
        pass
    try:
        final_epi_to_synth_warp_link.unlink()
    except FileNotFoundError:
        pass
    final_epi_anat_affine_link.symlink_to(final_epi_anat_affine_target)
    final_synth_to_epi_warp_link.symlink_to(final_synth_to_epi_warp_target)
    final_epi_to_synth_warp_link.symlink_to(final_epi_to_synth_warp_target)
