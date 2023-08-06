#!/usr/bin/env python3
import os
import argparse
import h5py
import nibabel as nib
import numpy as np
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Script for parsing an interaction matrix h5 file and converting its columns to NIFTI files.",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 04/23/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_input(parser, positional_arg=True, help="Path to input h5 file.")
    arg_output_path(parser, positional_arg=True, help="Folder to output Nifti Images.")
    arg_dims(parser, "-d")

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

    # get the absolute path for the input/output
    input_file = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output_path)

    # open the input h5 file
    with h5py.File(input_file, "r") as h5file:
        # get key
        key = [k for k in h5file.keys()][0]

        # get data
        data = h5file[key]

        # make directories if not exist
        os.makedirs(output_dir, exist_ok=True)

        # loop over columns and output them to NIFTI
        for c in range(data.shape[0]):
            print("Writing out column {}...".format(c))
            voxels = data[c, :]
            img = nib.Nifti1Image(voxels.reshape(*args.dims).T, np.eye(4))
            img.to_filename(os.path.join(output_dir, "col{:03d}.nii.gz".format(c)))

    # Done!
    print("Done!")
