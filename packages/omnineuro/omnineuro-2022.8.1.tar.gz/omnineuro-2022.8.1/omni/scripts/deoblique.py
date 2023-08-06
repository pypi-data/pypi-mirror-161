#!/usr/bin/env python3
"""
    Script to deoblique images
"""
import argparse
import nibabel as nib
from omni import affine
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Deobliques an image",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 02/25/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_input_image(parser, positional_arg=True, help="Image to deoblique.")
    arg_output_image(parser, positional_arg=True, help="Deobliqued image.")

    # set common arguments
    command.set_common(parser, threads=False, config=False)

    # return parser
    return parser


def main():
    # generate the parser
    parser = generate_parser()

    # parse arguments
    args = parser.parse_args()

    # call common parser
    command.parse_common(args, parser)

    # call deoblique function
    img_deobliqued = affine.deoblique(nib.load(args.input_image))

    # save deobliqued image
    img_deobliqued.to_filename(args.output_image)
