import argparse
import nibabel as nib
from omni.pipelines.logging import setup_logging
from omni.masks import generate_noise_mask
from omni.interfaces.common import append_suffix
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Generates a noise mask",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 01/26/2021",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_epi(parser, positional_arg=True)
    arg_anat_bet_mask_epispace(parser, positional_arg=True)
    arg_synthnoisemask_output(parser, positional_arg=True)
    arg_noise_mask_iterations(parser, "-i")
    arg_noise_mask_dilation_size(parser, "-d")
    arg_noise_mask_sigma(parser, "-k")

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

    # setup logging
    setup_logging()

    # load up image files
    epi = nib.load(args.epi)
    mask = nib.load(args.anat_bet_mask_epispace)

    # generate noise mask
    noise_mask, noise_mask_smooth = generate_noise_mask(
        epi, mask, args.noise_mask_dilation_size, args.noise_mask_iterations, args.noise_mask_sigma
    )

    # save out files
    noise_mask.to_filename(args.output)
    noise_mask_smooth.to_filename(append_suffix(args.output, "_smooth"))
