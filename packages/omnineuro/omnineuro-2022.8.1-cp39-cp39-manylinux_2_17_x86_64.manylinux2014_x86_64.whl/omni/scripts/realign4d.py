from pathlib import Path
import argparse
import json
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Frontend for SpaceTimeRealign Algorithm",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 11/20/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_fourd_img(parser, positional_arg=True)
    arg_bids_sidecar(parser, positional_arg=True)
    arg_output_prefix(parser, positional_arg=True)
    arg_ref_idx(parser, "-r")
    arg_loops(parser, "-l")
    arg_subsample(parser, "-s")
    arg_borders(parser, "-b")

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

    # now call any numpy dependent libraries when openmp threads are set
    import nibabel as nib
    from omni import register, io

    # load img
    img = nib.load(args.fourd_img)

    # grab the slice encoding direction (it's probably 2)
    sed = register.grab_slice_encoding_dir(img)

    # get slice times/TR
    with open(args.bids_sidecar, "r") as f:
        js = json.load(f)
        slice_times = js["SliceTiming"]
        tr = js["RepetitionTime"]

    # align the image
    transforms, resampled = register.realign4d(
        img, args.ref_idx, tr, slice_times, sed, args.loops, args.subsample, args.borders
    )

    # construct output names
    output = Path(args.output_prefix).resolve()

    # construct output directory if no exist
    output.parent.mkdir(parents=True, exist_ok=True)

    # write out params data
    io.write_rb_params(str(output) + "_rb.params", transforms)

    # write out image
    resampled.to_filename(str(output) + ".nii.gz")
