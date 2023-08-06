import os
import shutil
import logging
import nibabel as nib
from memori.pathman import append_suffix, get_path_and_prefix, repath
from memori.helpers import create_output_path, create_symlink_to_path
from omni.affine import deoblique
from omni.interfaces.afni import Allineate, cat_matvec
from omni.interfaces.fsl import flirt
from omni.interfaces.common import run_process
from omni.io import convert_affine_file


# Directory this file lives in
THISDIR = os.path.dirname(os.path.abspath(__file__))

# Get atlas directory
ATLASDIR = os.path.join(os.path.dirname(THISDIR), "atlas")


@create_output_path
def deoblique_anat(output_path: str, t1: str = None, t2: str = None):
    """Deoblique images.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    t1 : str
        T1 image.
    t2 : str
        T2 image.

    Returns
    -------
    str
        T1 deobliqued.
    str
        T2 deobliqued.
    """
    logging.info("Deobliquing anatomical images...")

    # Deoblique t1
    if t1:
        t1_img = nib.load(t1)
        t1_do_img = deoblique(t1_img)
        t1_do = append_suffix(repath(output_path, t1), "_deobliqued")
        t1_do_img.to_filename(t1_do)
    else:
        t1_do = None

    # Deoblique t2
    if t2:
        t2_img = nib.load(t2)
        t2_do_img = deoblique(t2_img)
        t2_do = append_suffix(repath(output_path, t2), "_deobliqued")
        t2_do_img.to_filename(t2_do)
    else:
        t2_do = None

    # return images
    return (t1_do, t2_do)


@create_output_path
def align_anat(
    output_path: str, t1_debias: str, t2_debias: str, ref: str = "T1", program: str = "fsl", other_args: str = None
):
    """Align T1/T2 images.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    t1_debias : str
        Debiased T1 image.
    t2_debias : str
        Debiased T2 image.
    ref : str
        Set the image to use as a reference [T1/T2].
    program : str
        Program to use for alignment
        ('afni': AFNI 3dAllineate or 'fsl': fsl flirt).
    other_args : str
        Other arguments to pass to alignment program.

    Returns
    -------
    str
        Anatomical aligned T1 (aligned to ref)
    str
        Anatomical aligned T2 (aligned to ref).
    str
        Affine aligning T1/T2 (depends on what ref was set to).
    """
    # set the reference and source images to use
    logging.info("Using %s as reference image for " "T1/T2 anatomical alignment.", ref)
    if ref == "T1":
        reference_img = t1_debias
        source_img = t2_debias
        anat_align_affine = os.path.join(output_path, "t2_to_t1_xfm.aff12.1D")
        t1_anat = append_suffix(repath(output_path, t1_debias), "_t1space")
        t2_anat = append_suffix(repath(output_path, t2_debias), "_t1space")
        anat_align_img = t2_anat
    elif ref == "T2":
        reference_img = t2_debias
        source_img = t1_debias
        anat_align_affine = os.path.join(output_path, "t1_to_t2_xfm.aff12.1D")
        t2_anat = append_suffix(repath(output_path, t2_debias), "_t2space")
        t1_anat = append_suffix(repath(output_path, t1_debias), "_t2space")
        anat_align_img = t1_anat
    else:
        raise ValueError("Invalid parameters set for ref. " "Must be either 'T1' or 'T2'.")

    # generate edge images
    def edge(prefix: str, in_file: str) -> None:
        return run_process(f"3dedge3 -prefix {prefix} -input {in_file} -verbose -overwrite")

    reference_edge_img = repath(output_path, append_suffix(reference_img, "_edge"))
    source_edge_img = repath(output_path, append_suffix(source_img, "_edge"))
    edge(reference_edge_img, reference_img)
    edge(source_edge_img, source_img)
    anat_align_edge_img = append_suffix(anat_align_img, "_edge")

    # align t1/t2
    logging.info("Aligning anatomical images...")
    if program == "afni":  # Use 3dAllineate
        # align edge images
        Allineate(
            anat_align_edge_img,
            reference_edge_img,
            source_edge_img,
            matrix_save=anat_align_affine,
            warp="shift_rotate",
            cost="mi",
            fineblur=4,
            nmatch="100%",
            twopass=True,
            other_args=other_args,
        )

        # apply affine to anat image
        Allineate(
            anat_align_img,
            reference_img,
            source_img,
            matrix_apply=anat_align_affine,
        )

    elif program == "fsl":  # Use flirt
        # align edge images
        anat_align_fsl_affine = get_path_and_prefix(anat_align_affine) + ".mat"
        flirt(
            anat_align_edge_img,
            reference_edge_img,
            source_edge_img,
            out_matrix=anat_align_fsl_affine,
            dof=6,
            other_args=other_args,
        )

        # apply affine to anat image
        flirt(anat_align_img, reference_img, source_img, other_args=f"-applyxfm -init {anat_align_fsl_affine}")

        # convert the fsl affine to afni
        convert_affine_file(anat_align_affine, anat_align_fsl_affine, "afni", target=reference_img, source=source_img)
    else:
        raise ValueError("Invalid parameter set for program. " "Must be either 'afni' or 'fsl'.")

    # add symlinks to ref image
    if ref == "T1":
        # symlink to debias and rename
        t1_debias_symlink = create_symlink_to_path(t1_debias, output_path)
        shutil.move(t1_debias_symlink, t1_anat)
    elif ref == "T2":
        # symlink to debias and rename
        t2_debias_symlink = create_symlink_to_path(t2_debias, output_path)
        shutil.move(t2_debias_symlink, t2_anat)

    # return file paths
    return (t1_anat, t2_anat, anat_align_affine)


@create_output_path
def align_atlas(
    output_path: str,
    t1_debias: str,
    t2_debias: str,
    t1_debias_bet: str,
    t2_debias_bet: str,
    anat_align_affine: str,
    atlas: str = "mni",
    atlas_label: str = "atlas",
    ref: str = "T1",
    program: str = "fsl",
    other_args: str = None,
):
    """Align T1/T2 images to atlas.

    Parameters
    ----------
    output_path : str
        Output path to write out files to.
    t1_debias : str
        Debiased T1 image.
    t2_debias : str
        Debiased T2 image.
    t1_debias_bet : str
        Debiased bet T1 image.
    t2_debias_bet : str
        Debiased bet T2 image.
    anat_align_affine : str
        Anatomical image to atlas.
    atlas : str
        Atlas to align to.
    atlas_label : str
        Label suffix for atlas outputs
    ref : str
        Set anatomical reference image that was used.
    program : str
        Program to use for alignment
        ('afni': AFNI 3dAllineate or 'fsl': fsl flirt).
    other_args : str
        Other arguments to pass to alignment program.

    Returns
    -------
    str
        Atlas aligned T1.
    str
        Atlas aligned T2.
    """
    # get atlas img
    if atlas == "mni":
        atlas_img = os.path.join(ATLASDIR, "mni_icbm152_t1_tal_nlin_sym_09c_bet.nii.gz")
    elif atlas == "trio":
        atlas_img = os.path.join(ATLASDIR, "TRIO_Y_NDC_bet.nii.gz")
    elif os.path.isfile(atlas):
        # Test if the atlas is a valid image file.
        nib.load(atlas)
        atlas_img = atlas
        atlas = atlas_label
    else:
        raise ValueError("Invalid atlas.")

    # create atlas aligned T1/T2 names
    t1_atlas_bet = append_suffix(repath(output_path, t1_debias_bet), "_" + atlas)
    atlas_align_affine = os.path.join(output_path, "atlas_align_affine.aff12.1D")

    # align T1 to mni atlas
    logging.info("Aligning anatomical images to atlas...")
    if program == "afni":
        Allineate(
            t1_atlas_bet,
            atlas_img,
            t1_debias_bet,
            warp="shift_rotate_scale",
            matrix_save=atlas_align_affine,
            cost="mi",
            fineblur=4,
            nmatch="100%",
            twopass=True,
            other_args=other_args,
        )
    elif program == "fsl":
        atlas_align_fsl_affine = get_path_and_prefix(atlas_align_affine) + ".mat"
        flirt(
            t1_atlas_bet,
            atlas_img,
            t1_debias_bet,
            out_matrix=atlas_align_fsl_affine,
            dof=9,
            cost="mutualinfo",
            other_args=other_args,
        )

        # convert the fsl affine to afni
        convert_affine_file(atlas_align_affine, atlas_align_fsl_affine, "afni", target=atlas_img, source=t1_debias_bet)
    else:
        raise ValueError("Invalid parameter set for program. " "Must be either 'afni' or 'fsl'.")

    # concatenate the affines transform
    concatenated_affine = os.path.join(output_path, "atlas_anat_align_affine.aff12.1D")
    cat_matvec(concatenated_affine, "{0} {1}".format(atlas_align_affine, anat_align_affine))

    # apply affine to T1/T2 to transform to affine
    t1_atlas = append_suffix(repath(output_path, t1_debias), "_" + atlas)
    t2_atlas = append_suffix(repath(output_path, t2_debias), "_" + atlas)
    if ref == "T1":
        t1_atlas_affine = atlas_align_affine
        t2_atlas_affine = concatenated_affine
    elif ref == "T2":
        t1_atlas_affine = concatenated_affine
        t2_atlas_affine = atlas_align_affine
    else:
        raise ValueError("Invalid ref.")
    Allineate(t1_atlas, atlas_img, t1_debias, matrix_apply=t1_atlas_affine)
    Allineate(t2_atlas, atlas_img, t2_debias, matrix_apply=t2_atlas_affine)

    # return T1/T2 atlas aligned images
    return (t1_atlas, t2_atlas, atlas_align_affine)
