import os
import shutil
from glob import glob
from .common import run_process, append_suffix


def flirt(
    out_file: str,
    reference: str,
    source: str,
    out_matrix: str = None,
    dof: int = 12,
    cost: str = "corratio",
    interp: str = "sinc",
    other_args: str = None,
):
    """Affine alignment with fsl flirt.

    Parameters
    ----------
    out_file: str
        Aligned output image.
    reference: str
        Reference image to align.
    source: str
        Source image to align.
    out_matrix: str
        Affine matrix file.
    dof: str
        Degrees of freedom to use for alignment.
    cost: str
        Cost function to use for optimization.
    interp: str
        Interpolation to use for output image.
    other_args: str
        Other arguments to pass in.
    """
    return run_process(
        "flirt "
        "-out {} "
        "-ref {} "
        "-in {} "
        "-dof {} "
        "-cost {} "
        "-interp {} "
        "{}{}-v".format(
            out_file,
            reference,
            source,
            dof,
            cost,
            interp,
            "-omat {} ".format(out_matrix) if out_matrix else "",
            "{} ".format(other_args) if other_args else "",
        )
    )


def bet(
    out_file: str,
    in_file: str,
    fractional_intensity_threshold: float = 0.5,
    mask: bool = False,
    eye: bool = False,
    neck: bool = False,
    other_args: str = None,
):
    """Brain extraction tool.

    Parameters
    ----------
    out_file: str
        Brain extracted output image.
    in_file: str
        Image to brain extract
    fractional_intensity_threshold: float
        Fractional intensity threshold for bet.
    mask: bool
        Controls whether a binary mask should be output
    eye: bool
        Generate eye mask (mutually exclusive with neck option)
    neck: bool
        Neck cleanup (mutually exclusive with eye option)
    other_args: str
        Other arguments to pass in.
    """
    # Cannot have two mutually exclusive options enabled
    if eye and neck:
        raise ValueError("eye and neck options are mutually exclusive.")

    # run bet
    process_string = run_process(
        "bet "
        "{0} {1} -f {2} "
        "{3}{4}{5}{6}-v".format(
            in_file,
            out_file,
            fractional_intensity_threshold,
            "-m " if mask else "",
            "-S -d " if eye else "",
            "-B -d " if neck else "",
            "{} ".format(other_args) if other_args else "",
        )
    )

    # generate output list
    output_list = [
        process_string,
    ]

    # add mask outputs if enabled
    if mask:
        output_list.append(append_suffix(out_file, "_mask"))
    if eye:
        shutil.move(append_suffix(out_file, "_tmp_eye_mask"), append_suffix(out_file, "_eye_mask"))
        output_list.append(append_suffix(out_file, "_eye_mask"))

    # cleanup tmp files
    output_dir = os.path.dirname(out_file)
    if glob(os.path.join(output_dir, "*tmp*")):
        run_process("rm {}".format(os.path.join(output_dir, "*tmp*")), stdout=False)

    # return output list
    return output_list
