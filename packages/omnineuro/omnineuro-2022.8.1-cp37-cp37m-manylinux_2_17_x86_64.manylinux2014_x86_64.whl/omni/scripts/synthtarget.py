"""
    Script to run SynthTarget
"""
import logging
import argparse
from .common import command
from .common.arguments import *
from .common import help as helptxt


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="The SynthTarget algorithm. Solves the joint synthetic transformation/affine registration problem."
        " See algorithm 1 of the Synth paper.\n{0}".format(BASE_DOC_URL + "synth/utilities/synthtarget.html"),
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 03/29/2021",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_target_image(parser, positional_arg=True, help=helptxt.synthtarget_target_image)
    arg_interaction_model(parser, positional_arg=True, help=helptxt.synthtarget_interaction_model)
    arg_input_images(parser, positional_arg=True, help=helptxt.synthtarget_input_images)
    arg_regression_weight_mask(parser, "-w", help=helptxt.synthtarget_regression_weight_mask)
    arg_affine(parser, "-a", help="Initial affine transform to use for optimization.")
    arg_output_prefix(parser, "-o", help=helptxt.synthtarget_output_prefix)
    arg_regression_output(parser, "-r", help=helptxt.synthtarget_regression_output)
    arg_synth_image(parser, "-b", help=helptxt.synthtarget_synth_image)
    arg_synth_image_target_space(parser, "-f", help=helptxt.synthtarget_synth_image_target_space)
    arg_err_tol(parser, "-e")
    arg_step_size(parser, "-d")
    arg_max_iterations(parser, "-i")
    arg_tone_curve(parser, "-c")
    arg_tone_curve_mask(parser, "-u")
    kernel_args = parser.add_mutually_exclusive_group()
    arg_bandwidth(kernel_args, "-p", help=helptxt.synthtarget_bandwidth)
    arg_fixed_regress(parser)
    arg_no_register(parser, help=helptxt.synthtarget_no_register)
    arg_output_intmat(parser, help=helptxt.synthtarget_output_intmat)

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

    # set environment variables
    command.set_env(args)

    # call register function
    from omni import register

    register.register(
        target=args.target_image,
        interaction=args.interaction_model,
        source=args.input_images,
        regress_mask=args.regression_weight_mask,
        initial_affine=args.affine,
        output=args.output_prefix,
        regressed_output=args.regression_output,
        blurred_regressed_output=args.synth_image,
        aligned_output=args.synth_image_target_space,
        err_tol=args.err_tol,
        step_size=args.step_size,
        max_iterations=args.max_iterations,
        tone_curve=args.tone_curve,
        tone_curve_mask=args.tone_curve_mask,
        bandwidth=args.bandwidth,
        fixed_regress=args.fixed_regress,
        no_register=args.no_register,
        output_intmat=args.output_intmat,
    )
