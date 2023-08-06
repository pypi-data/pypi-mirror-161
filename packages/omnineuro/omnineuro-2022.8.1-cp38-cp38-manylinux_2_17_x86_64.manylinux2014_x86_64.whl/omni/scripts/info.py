#!/usr/bin/env python3
import argparse
import nibabel as nib
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Get image info",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 10/20/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_input_image(parser, positional_arg=True)

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

    # read image
    img = nib.load(args.input_image)

    # print header
    print(img.header)
