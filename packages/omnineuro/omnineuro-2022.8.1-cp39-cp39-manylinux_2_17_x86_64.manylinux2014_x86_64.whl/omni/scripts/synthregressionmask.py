from pathlib import Path
import argparse
import tempfile
import numpy as np
import nibabel as nib
from omni.io import convert_affine_file
from omni.interfaces.afni import NwarpCat
from omni.pipelines.logging import setup_logging
from omni.masks import make_regression_mask
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Generates a weighted regression mask for use in Synth.",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 03/29/2021",
        formatter_class=CustomTextHelpFormatter,
    )

    arg_synthregressionmask_dil_anat_weight_mask(parser, positional_arg=True)
    arg_synthregressionmask_anat_bet_mask(parser, positional_arg=True)
    arg_epi(parser, positional_arg=True, help=common_epi)
    arg_synthregressionmask_affine(parser, positional_arg=True)
    arg_output_path(parser, positional_arg=True)
    arg_synthregressionmask_warp(parser, "-w")
    arg_noise_mask_dilation_size(parser, "-d")
    arg_noise_mask_iterations(parser, "-i")
    arg_noise_mask_sigma(parser, "-s")

    # set common arguments
    command.set_common(parser, threads=False)

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

    # create a temp directory context
    with tempfile.TemporaryDirectory() as d:
        # create an inverse affine filename
        args.iaffine = str(Path(d) / "inverse_affine.aff12.1D")

        # get the inverse of the affine file
        convert_affine_file(args.iaffine, args.anat_to_epi_affine, "afni", invert=True)

        # if warp not specfied, create an empty warp field
        if not args.warp:
            # get epi image 3D shape
            epi_img = nib.load(args.epi)
            epi_img_shape = epi_img.shape[:3] + (3,)

            # make empty numpy array with shape
            warp_data = np.zeros(epi_img_shape)
            warp_img = nib.Nifti1Image(warp_data, epi_img.affine, epi_img.header)
            args.warp = str(Path(d) / "warp.nii.gz")
            warp_img.to_filename(args.warp)

        # make inverse warp
        args.iwarp = str(Path(d) / "iwarp.nii.gz")
        NwarpCat(args.iwarp, args.warp, True)

        # make output path folders
        Path(args.output_path).mkdir(parents=True, exist_ok=True)

        # call make regression mask
        args.output_prefix = str(Path(args.output_path) / "synth_")
        regression_mask = make_regression_mask(
            output_prefix=args.output_prefix,
            epi=args.epi,
            anat_weight_mask=args.dil_anat_bet_mask,
            anat_bet_mask=args.anat_bet_mask,
            affine=args.anat_to_epi_affine,
            iaffine=args.iaffine,
            warp=args.warp,
            iwarp=args.iwarp,
            noise_mask_dilation_size=args.noise_mask_dilation_size,
            noise_mask_sigma=args.noise_mask_sigma,
            noise_mask_iterations=args.noise_mask_iterations,
        )

        print("Regression mask at: %s" % regression_mask)
