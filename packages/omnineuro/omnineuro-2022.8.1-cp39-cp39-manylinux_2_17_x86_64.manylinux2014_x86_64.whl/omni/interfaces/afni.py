from typing import Union, List
from .common import run_process


def NwarpCat(prefix: str, warps: Union[List[str], str], iwarps: Union[List[bool], bool] = False):
    """3dNwarpCat.

    Parameters
    ----------
    prefix: str
        Prefix for output warp.
    warps: Union[List, str]
        List of transforms to concatenate
        (or single transform string).
    iwarps: Union[List, bool]
        List of booleans to specify whether
        transform should be inverted (or
        singular boolean for single transform).
    """
    # make inputs lists
    if not isinstance(warps, list):
        warps = [warps]
    if not isinstance(iwarps, list):
        iwarps = [iwarps]

    # assert same length
    assert len(warps) == len(iwarps), "warps and iwarps must be same length."

    # construct warp string
    warp_string = ""
    for i, (warp, inverse) in enumerate(zip(warps, iwarps)):
        # append warp_string
        warp_string += "-warp%d %s%s " % (i + 1, warp, " -iwarp" if inverse else "")

    # run process
    return run_process("3dNwarpCat -prefix {} {}-verb -overwrite".format(prefix, warp_string))


def NwarpApply(prefix: str, master: str, source: str, nwarp: Union[List, str]):
    """3dNwarpApply

    Parameters
    ----------
    prefix: str
        Prefix for output image.
    master: str
        Reference image to align to.
    source: str
        Source image to align.
    nwarp: Union[List, str]
        List of transforms to apply.
    """
    return run_process(
        "3dNwarpApply -nwarp {} -prefix {} -master {} "
        "-source {} -overwrite".format(nwarp if isinstance(nwarp, str) else " ".join(nwarp), prefix, master, source)
    )


def Allineate(
    prefix: str,
    base: str,
    source: str,
    cost: str = None,
    final: str = "wsinc5",
    warp: str = None,
    matrix_save: str = None,
    matrix_apply: str = None,
    fineblur: int = None,
    nmatch: str = None,
    twopass: bool = False,
    other_args: str = None,
):
    """3dAllineate.

    Parameters
    ----------
    prefix: str
        Prefix for output image.
    base: str
        Reference image to align to.
    source: str
        Source image to align.
    cost: str
        Cost function to use.
    final: str
        Final interpolation method.
    warp: str
        Type of warp string (e.g. shift_rotate, shift_rotate_scale, etc).
    matrix_save: str
        Path to save affine matrix.
    matrix_apply: str
        Path to apply affine matrix.
    fineblur: int
        Size of fine blurring kernel to use.
    nmatch: str
        Percentage of voxels to match (e.g. "100%").
    twopass: bool
        Do twopass registration.
    other_args: str
        Other arguments to pass in.
    """
    return run_process(
        "3dAllineate "
        "-prefix {0} -base {1} -input {2} "
        "{3}{4}{5}{6}{7}{8}{9}{10}{11}-overwrite".format(
            prefix,
            base,
            source,
            "-final {} ".format(final) if final else "",
            "-warp {} ".format(warp) if warp else "",
            "-1Dmatrix_save {} ".format(matrix_save) if matrix_save else "",
            "-1Dmatrix_apply {} ".format(matrix_apply) if matrix_apply else "",
            "-cost {} ".format(cost) if cost else "",
            "-fineblur {} ".format(fineblur) if fineblur else "",
            "-nmatch {} ".format(nmatch) if nmatch else "",
            "-twopass " if twopass else "",
            "{} ".format(other_args) if other_args else "",
        )
    )


def Autobox(prefix: str, source: str, npad: int = None):
    """3dAutobox.

    Parameters
    ----------
    prefix: str
        Prefix for output image.
    source: str
        Input image.
    npad: int
        Padding.
    """
    return run_process(
        "3dAutobox -prefix {} -input {} {}-overwrite".format(prefix, source, "-npad {} ".format(npad) if npad else "")
    )


def cat_matvec(concatenated_affine: str, affine_matrices: str):
    """Concatenate affine transforms.

    Parameters
    ----------
    concatenated_affine: str
        Concatenated affine matrix.
    affine_matrices: str
        String of affine matrices to concatenate.
    """
    return run_process("cat_matvec {0} > {1}".format(affine_matrices, concatenated_affine))


def resample(prefix: str, master: str, source: str, rmode: str = "Cu", dxyz: float = None):
    """3dresample

    Parameters
    ----------
    prefix: str
        Prefix for output image.
    master: str
        Reference Image.
    source: str
        Input image.
    rmode: str
        Interpolation mode.
    dxyz: float
        Resolution to resample to.
    """
    return run_process(
        "3dresample -prefix {} -master {} -input {} -rmode {} {}"
        "-overwrite".format(prefix, master, source, rmode, "-dxyz {0} {0} {0} ".format(dxyz) if dxyz else "")
    )
