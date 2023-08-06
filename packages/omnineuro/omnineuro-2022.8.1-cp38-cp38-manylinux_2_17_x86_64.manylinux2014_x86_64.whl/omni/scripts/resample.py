"""
    Script to resample images
"""
import argparse
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Resamples an image",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 09/22/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_target_image(parser, positional_arg=True)
    arg_input_image(parser, positional_arg=True)
    arg_output_image(parser, positional_arg=True)
    affine_ops = parser.add_mutually_exclusive_group()
    arg_affine(affine_ops, "-a")
    arg_rigid_transform(affine_ops, "-r")

    # set common arguments
    command.set_common(parser, config=False)

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

    # import libraries after setting threads
    import numpy as np
    from omni import io, resample
    from omni.affine import generate_rigid_transform

    # load images
    target_img, source_img = io.load_target_source(args.target_image, args.input_image)

    # check if affine defined
    if args.affine:
        affine_mat = io.read_affine_file(args.affine)[0]
    elif args.rigid_transform:
        affine_mat = generate_rigid_transform(
            args.rigid_transform[0],
            args.rigid_transform[1],
            args.rigid_transform[2],
            [args.rigid_transform[3], args.rigid_transform[4], args.rigid_transform[5]],
        )
    else:  # use identity matrix
        affine_mat = np.eye(4)

    # call resample
    output = resample.resample(target_img, source_img, affine_mat)

    # write image to file
    output.to_filename(args.output_image)
