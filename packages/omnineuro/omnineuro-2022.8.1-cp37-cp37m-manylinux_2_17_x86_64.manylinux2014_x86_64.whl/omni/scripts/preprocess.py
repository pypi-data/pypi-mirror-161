from pathlib import Path
import argparse
from ast import literal_eval
import nibabel as nib
from omni import preprocessing
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Applies preprocessing procedure to image.",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 03/29/2021",
        formatter_class=CustomTextHelpFormatter,
    )
    parser.add_argument(
        "procedure",
        choices=["saturate", "equalize", "localized_contrast_enhance", "clahe", "normalization"],
        help="Preprocessing procedure to apply.",
    )
    arg_output_image(parser, positional_arg=True)
    parser.add_argument(
        "--options",
        "-o",
        nargs="+",
        default=list(),
        help="Arguments to preprocessing procedure (as arg1=value1 arg2=value2 etc.)."
        "See omni.preprocessing for method parameters.",
    )

    # set common arguments
    command.set_common(parser, threads=False, config=False)

    # return parser
    return parser


def main():
    # generate the parser
    parser = generate_parser()

    # parse args
    args = parser.parse_args()

    # call common parser
    command.parse_common(args, parser)

    # loop over options (if any)
    options = dict()
    for op in args.options:
        # get argument
        key, value = op.split("=")

        # load image file if value is one.
        if ".nii" in value:
            value = nib.load(value)
        else:  # try getting the actual value type
            try:
                value = literal_eval(value)
            except ValueError:  # just leave it as a string
                pass

        # store in options
        options[key] = value

    # get the method to call
    method = getattr(preprocessing, args.procedure)

    # call the method with options
    print("Running: %s" % args.procedure)
    print("With options: %s" % options)
    output_img = method(**options)

    # save to file
    output_img.to_filename(Path(args.output_image).resolve())
