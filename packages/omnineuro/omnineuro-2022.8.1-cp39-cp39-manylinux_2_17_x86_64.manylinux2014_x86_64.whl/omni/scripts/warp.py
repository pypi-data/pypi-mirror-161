"""
    Script to manipulate affine transformations
"""
import argparse
import nibabel as nib
from .common import command
from .common.arguments import *
from .common.help import *
from omni.warp import convert_warp


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Script for converting/inverting nonlinear transforms.",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 06/10/2022",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_input(parser, positional_arg=True)
    arg_output(parser, positional_arg=True)
    arg_in_warp_type(parser, "-i", required=True)
    arg_out_warp_type(parser, "-o", required=True)
    arg_target(parser, "-t")
    arg_invert(parser, "-n")

    # set common arguments
    command.set_common(parser, threads=False, config=False)

    # return parser
    return parser


def main():
    # generate the parser
    parser = generate_parser()

    # call parser
    args = parser.parse_args()

    # call common parser
    command.parse_common(args, parser)

    # load the input warp
    in_warp = nib.load(args.input)

    # target image
    target_img = nib.load(args.target) if args.target else None

    # call the conversion function
    out_warp = convert_warp(in_warp, args.in_warp_type, args.out_warp_type, args.invert, target_img)

    # save the output warp
    out_warp.to_filename(args.output)
