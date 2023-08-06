"""
    Script to manipulate affine transformations
"""
from pathlib import Path
import argparse
import nibabel as nib
from omni import io
from omni.affine import convert_affine, generate_rigid_transform
from .common import command
from .common.arguments import *
from .common.help import *


# create command line parser
def generate_parser():
    parser = argparse.ArgumentParser(
        description="Script for creating/inverting affine transforms.",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 09/22/2020",
        formatter_class=CustomTextHelpFormatter,
    )
    arg_output(parser, positional_arg=True)
    arg_input_affine(parser, "-i")
    conversion_ops = parser.add_mutually_exclusive_group()
    arg_omnify(conversion_ops, "-o")
    arg_afnify(conversion_ops, "-a")
    arg_fslify(conversion_ops, "-f")
    arg_target(parser, "-t")
    arg_source(parser, "-s")
    arg_rigid_transform(conversion_ops, "-r")
    arg_six_body(conversion_ops, "-b")
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

    # if input defined
    if args.input_affine and not args.rigid_transform and not args.six_body:
        # load the affine file and detect type
        input_affine, in_atype = io.read_affine_file(args.input_affine)

        # print types
        print("Input affine type: {}".format(in_atype))

        # load in the fsl target/source if specified
        if args.target and args.source:
            target = nib.load(args.target)
            source = nib.load(args.source)
        else:
            target = None
            source = None

        # omnify
        if args.omnify:
            print("Output affine type: {}".format("omni"))
            output_affine = convert_affine(input_affine, in_atype, "omni", args.invert, target, source)
            out_atype = "omni"

        # afnify
        if args.afnify:
            print("Output affine type: {}".format("afni"))
            output_affine = convert_affine(input_affine, in_atype, "afni", args.invert, target, source)
            out_atype = "afni"

        # fslify
        if args.fslify:
            print("Output affine type: {}".format("fsl"))
            output_affine = convert_affine(input_affine, in_atype, "fsl", args.invert, target, source)
            out_atype = "fsl"

    # rigid transform generation
    elif not args.input_affine and args.rigid_transform and not args.six_body:
        # turn inputs into affine matrix
        output_affine = generate_rigid_transform(
            args.rigid_transform[0],
            args.rigid_transform[1],
            args.rigid_transform[2],
            [args.rigid_transform[3], args.rigid_transform[4], args.rigid_transform[5]],
        )

        # default output atype to omni
        out_atype = "omni"

    # affine to rigid body conversion
    elif args.input_affine and not args.rigid_transform and args.six_body:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        io.convert_framewise_affine_to_rigid_body(output, args.input_affine)
        return

    # specify either input or rigid transform separately
    else:
        raise ValueError("You are specifying mutually exclusive options! Check your inputs and try again.")

    # save the affine to file
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    io.write_affine_file(str(output), output_affine, out_atype)
