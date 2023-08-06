import sys
import argparse
import nibabel as nib
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Extracts a subset of an image",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 10/20/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_input_image(parser, positional_arg=True)
    arg_output_image(parser, positional_arg=True)
    arg_limits(parser, "-l")

    # set common arguments
    command.set_common(parser, False, config=False)

    # return parser
    return parser


def main():
    # generate the parser
    parser = generate_parser()

    # call parser
    args = parser.parse_args()

    # call common parser
    command.parse_common(args, parser)

    # parse limits
    lims = args.limits.split("[")[1].split("]")[0].split(",")

    # load the image
    img = nib.load(args.input_image)

    # check if same dim as image
    assert len(lims) == len(img.shape), "Limit input not same dimension as image!"

    # sanitize the limit inputs to ensure they are all integers, empty string, or :
    try:
        arg_pos = 0
        for limit in lims:
            for x in limit.split(":"):
                True if x == "" else int(x)  # pylint: disable=expression-not-assigned
            arg_pos += 1
    except ValueError:
        print("Invalid Input Detected: {}".format(lims[arg_pos]))
        sys.exit(1)

    # use eval to get the extracted image
    img_array = eval("img.dataobj{}".format(args.limits))  # pylint: disable=eval-used

    # write out new image
    nib.Nifti1Image(img_array, img.affine, img.header).to_filename(args.output_image)
