import argparse
import logging
import os
import shutil
from pathlib import Path
from bids import BIDSLayout
import nibabel as nib
import numpy as np
from omni.affine import deoblique
from omni.interfaces.afni import NwarpApply
from omni.interfaces.common import run_process, append_suffix, repath
from omni.interfaces.fsl import bet
from omni.io import convert_affine_file
from omni.path import create_output_path, use_abspaths, working_directory, create_symlink_to_folder
from omni.pipelines.anat.align import ATLASDIR
from omni.pipelines.bids import bids_proc
from omni.pipelines.common import Stage, Pipeline
from omni.pipelines.logging import setup_logging
from omni.scripts.common import command

try:
    from nipype import config, Node, Workflow
    from nipype import logging as nilogging
    from nipype.interfaces.io import DataSink
    from sdcflows.workflows.apply.correction import init_unwarp_wf
    from sdcflows.workflows.fit.syn import init_syn_preprocessing_wf, init_syn_sdc_wf
except ImportError:
    import warnings

    warnings.warn("Could not import nipype and sdcflows dependencies! fmapless pipeline will not work.")


def create_pipeline_symlinks(output_path: str, kwargs: dict) -> tuple[Path]:
    # get the pipeline output path
    pipeline_output_path = Path(kwargs["pipeline_output_path"])

    # get epi and anat paths
    anat_path = Path(kwargs["anat_path"])
    epi_path = Path(kwargs["epi_path"])

    # make epi and anat output folders
    with working_directory(output_path, suppress_log=True):
        anat_path.mkdir(parents=True, exist_ok=True)
        epi_path.mkdir(parents=True, exist_ok=True)

    # symlink existing results
    # anat
    anat_proc_link_root = output_path / anat_path
    anat_input_data_path = pipeline_output_path / anat_path / "input_data"
    anat_output_data_path = pipeline_output_path / anat_path / "output_data"
    anat_proc_0_path = pipeline_output_path / anat_path / "anat_proc_0_deoblique_anat"
    anat_proc_1_path = pipeline_output_path / anat_path / "anat_proc_1_debias"
    anat_proc_2_path = pipeline_output_path / anat_path / "anat_proc_2_align_anat"
    anat_proc_3_path = pipeline_output_path / anat_path / "anat_proc_3_brain_extraction"
    anat_proc_4_path = pipeline_output_path / anat_path / "anat_proc_4_align_atlas"
    anat_proc_5_path = pipeline_output_path / anat_path / "anat_proc_5_weight_mask_and_autobox"
    anat_input_data = create_symlink_to_folder(anat_input_data_path, anat_proc_link_root, "input_data")
    anat_output_data = create_symlink_to_folder(anat_output_data_path, anat_proc_link_root, "output_data")
    anat_proc_0 = create_symlink_to_folder(anat_proc_0_path, anat_proc_link_root, "anat_proc_0_deoblique_anat")
    anat_proc_1 = create_symlink_to_folder(anat_proc_1_path, anat_proc_link_root, "anat_proc_1_debias")
    anat_proc_2 = create_symlink_to_folder(anat_proc_2_path, anat_proc_link_root, "anat_proc_2_align_anat")
    anat_proc_3 = create_symlink_to_folder(anat_proc_3_path, anat_proc_link_root, "anat_proc_3_brain_extraction")
    anat_proc_4 = create_symlink_to_folder(anat_proc_4_path, anat_proc_link_root, "anat_proc_4_align_atlas")
    anat_proc_5 = create_symlink_to_folder(anat_proc_5_path, anat_proc_link_root, "anat_proc_5_weight_mask_and_autobox")
    # epi
    epi_proc_link_root = output_path / epi_path
    epi_proc_input_data_path = pipeline_output_path / epi_path / "input_data"
    func_proc_0_path = pipeline_output_path / epi_path / "func_proc_0_deoblique_func"
    func_proc_1_path = pipeline_output_path / epi_path / "func_proc_1_create_reference_and_moco"
    func_proc_2_path = pipeline_output_path / epi_path / "func_proc_2_debias"
    func_proc_3_path = pipeline_output_path / epi_path / "func_proc_3_brain_extraction"
    func_proc_4_path = pipeline_output_path / epi_path / "func_proc_4_autobox_and_normalize"
    epi_proc_0_path = pipeline_output_path / epi_path / "epi_proc_0_align_affine_epi_to_anat"
    epi_proc_1_path = pipeline_output_path / epi_path / "epi_proc_1_distortion_correction"
    epi_proc_2_path = pipeline_output_path / epi_path / "epi_proc_2_combine_transforms"
    epi_proc_input_data = create_symlink_to_folder(epi_proc_input_data_path, epi_proc_link_root, "input_data")
    func_proc_0 = create_symlink_to_folder(func_proc_0_path, epi_proc_link_root, "func_proc_0_deoblique_func")
    func_proc_1 = create_symlink_to_folder(
        func_proc_1_path, epi_proc_link_root, "func_proc_1_create_reference_and_moco"
    )
    func_proc_2 = create_symlink_to_folder(func_proc_2_path, epi_proc_link_root, "func_proc_2_debias")
    func_proc_3 = create_symlink_to_folder(func_proc_3_path, epi_proc_link_root, "func_proc_3_brain_extraction")
    func_proc_4 = create_symlink_to_folder(func_proc_4_path, epi_proc_link_root, "func_proc_4_autobox_and_normalize")
    epi_proc_0 = create_symlink_to_folder(epi_proc_0_path, epi_proc_link_root, "epi_proc_0_align_affine_epi_to_anat")
    epi_proc_1 = create_symlink_to_folder(epi_proc_1_path, epi_proc_link_root, "epi_proc_1_distortion_correction")
    epi_proc_2 = create_symlink_to_folder(epi_proc_2_path, epi_proc_link_root, "epi_proc_2_combine_transforms")

    # resolve the bids path
    bids_path = Path(kwargs["bids_path"]).resolve().as_posix()

    # get T1 debias and T1 bet
    with working_directory(anat_proc_link_root, suppress_log=True):
        # get t1 images
        t1 = Path([f for f in Path(anat_proc_0).iterdir() if "T1w" in f.name][0]).resolve()
        t1_debias = Path([f for f in Path(anat_proc_2).iterdir() if "T1w" in f.name][0]).resolve()
        t1_bet = Path([f for f in Path(anat_proc_3).iterdir() if "T1w" in f.name][0]).resolve()
        # get t1 brain mask
        t1_mask = Path([f for f in Path(anat_proc_3).iterdir() if "anat_bet_mask.nii.gz" in f.name][0]).resolve()
        # get atlas transform
        atlas_xfm = Path(
            [f for f in Path(anat_proc_4).iterdir() if "atlas_align_affine.aff12.1D" in f.name][0]
        ).resolve()

    # get ref_func
    with working_directory(epi_proc_link_root, suppress_log=True):
        # reference epi images
        ref_epi_basic = Path([f for f in Path(func_proc_1).iterdir() if "reference." in f.name][0]).resolve()
        ref_epi = Path(
            [f for f in Path(epi_proc_input_data).iterdir() if "reference_debias_ab." in f.name][0]
        ).resolve()
        ref_epi_bet = Path(
            [f for f in Path(epi_proc_input_data).iterdir() if "reference_debias_bet_ab." in f.name][0]
        ).resolve()
        ref_epi_mask = Path(
            [f for f in Path(epi_proc_input_data).iterdir() if "reference_debias_bet_mask_ab." in f.name][0]
        ).resolve()
        # get framewise alignment
        rigid_body_params = Path(
            [f for f in Path(epi_proc_input_data).iterdir() if "rigid_body.params" in f.name][0]
        ).resolve()
        # get functional to apply transforms to
        func_ab = Path([f for f in Path(epi_proc_input_data).iterdir() if "_deobliqued_ab." in f.name][0]).resolve()
        # get atlas
        atlas_resampled = Path(
            [f for f in Path(epi_proc_2).iterdir() if "TRIO_Y_NDC_resampled." in f.name][0]
        ).resolve()

    # return paths
    return (
        bids_path,
        anat_path,
        epi_path,
        t1,
        t1_debias,
        t1_bet,
        t1_mask,
        ref_epi_basic,
        ref_epi,
        ref_epi_bet,
        ref_epi_mask,
        atlas_xfm,
        rigid_body_params,
        func_ab,
        atlas_resampled,
    )


@create_output_path
def pd_setup(output_path: str, func: str, metadata: dict, bids_path: str, subject: str, session: str) -> tuple[str]:
    # get phase and magnitude images
    layout = BIDSLayout(bids_path)
    phasediff_files = layout.get(datatype="fmap", subject=subject, session=session, suffix="phasediff")
    magnitude_files = layout.get(datatype="fmap", subject=subject, session=session, suffix=["magnitude1", "magnitude2"])

    # get echo time difference (ms)
    echo_time_diff = np.abs(phasediff_files[0].entities["EchoTime1"] - phasediff_files[0].entities["EchoTime2"]) * 1000

    # get 1st files from list and deoblique them
    phasediff_do_file = repath(output_path, append_suffix(phasediff_files[0].path, "_do"))
    phasediff_do_img = deoblique(phasediff_files[0].get_image())
    phasediff_do_img.to_filename(phasediff_do_file)
    magnitude_do_file = repath(output_path, append_suffix(magnitude_files[0].path, "_do"))
    magnitude_do_img = deoblique(magnitude_files[0].get_image())
    magnitude_do_img.to_filename(magnitude_do_file)

    # skullstrip the magnitude image
    magnitude_do_bet_file = append_suffix(magnitude_do_file, "_bet")
    bet(magnitude_do_bet_file, magnitude_do_file, 0.7)

    # run fsl_prepare_fieldmap
    fmap_file = (Path(output_path) / "fieldmap.nii.gz").as_posix()
    run_process(
        f"fsl_prepare_fieldmap SIEMENS {phasediff_do_file} {magnitude_do_bet_file} {fmap_file} {echo_time_diff}"
    )

    # get phase encoding direction from data
    ped = {"i": "x", "j": "y", "k": "z", "i-": "x-", "j-": "y-", "k-": "z-"}[
        phasediff_files[0].entities["PhaseEncodingDirection"]
    ]

    # get echo spacing
    echo_spacing = metadata["EffectiveEchoSpacing"]

    # return files
    return (fmap_file, magnitude_do_file, magnitude_do_bet_file, echo_spacing, ped)


@create_output_path
def pd_epi_reg(
    output_path: str,
    epi: str,
    t1: str,
    t1brain: str,
    fmap: str,
    fmapmag: str,
    fmapmagbrain: str,
    echospacing: float,
    pedir: str,
) -> tuple[str]:
    # run epi_reg
    epi_reg_files = (Path(output_path) / "epi_reg_out").as_posix()
    run_process(
        f"epi_reg --epi={epi} --t1={t1} --t1brain={t1brain} --out={epi_reg_files} "
        f"--fmap={fmap} --fmapmag={fmapmag} --fmapmagbrain={fmapmagbrain} --echospacing={echospacing} --pedir={pedir}"
    )

    # convert shiftmap to afni
    shiftmap = epi_reg_files + "_fieldmaprads2epi_shift.nii.gz"
    fsl_warp = (Path(output_path) / "fsl_warp.nii.gz").as_posix()
    run_process(f"convertwarp --ref={epi} --out={fsl_warp} --shiftmap={shiftmap} --shiftdir={pedir} --rel --relout")
    afni_warp = (Path(output_path) / "afni_warp.nii.gz").as_posix()
    epi_img = nib.load(epi)
    warp_img = nib.load(fsl_warp)
    nib.Nifti1Image(warp_img.get_fdata()[:, :, :, np.newaxis, :] * -1, epi_img.affine).to_filename(afni_warp)

    # convert rigid body transform
    epi_reg_xfm = epi_reg_files + ".mat"
    epi_reg_xfm_afni = epi_reg_files + ".aff12.1D"
    convert_affine_file(epi_reg_xfm_afni, epi_reg_xfm, "afni", target=t1, source=epi)

    # return output files
    return (epi_reg_xfm_afni, afni_warp)


@create_output_path
def pd_combine_transforms(
    output_path: str,
    atlas_xfm: str,
    epi_to_anat_xfm_afni: str,
    afni_warp: str,
    rigid_body_params: str,
    func: str,
    atlas_resampled: str,
    final_dir: str,
    jacobian: str = None,
    disable_jac_mod: bool = False,
) -> None:
    # make sure rigid body params named correctly
    rigid_body_xfm = (Path(output_path) / "rigid_body.aff12.1D").as_posix()
    shutil.copy2(rigid_body_params, rigid_body_xfm)

    # apply warps to func
    Path(final_dir).mkdir(exist_ok=True)
    func_atlas = repath(final_dir, append_suffix(func, "_trio"))
    NwarpApply(
        func_atlas,
        atlas_resampled,
        func,
        [atlas_xfm, epi_to_anat_xfm_afni, afni_warp, rigid_body_xfm],
    )

    # if jacobian defined, modulate by jacobian
    if jacobian and not disable_jac_mod:
        jacobian_atlas = repath(output_path, append_suffix(jacobian, "_trio"))
        # get jacobian in correct space
        NwarpApply(
            jacobian_atlas,
            atlas_resampled,
            jacobian,
            [atlas_xfm, epi_to_anat_xfm_afni, f"'IDENT({jacobian})'"],
        )
        run_process(f"fslmaths {func_atlas} -mul {jacobian_atlas} {func_atlas}")


@create_output_path
@use_abspaths
def pd_proc(output_path: str, **kwargs) -> None:
    # make symlinks to pipeline outputs
    (
        bids_path,
        anat_path,
        epi_path,
        t1,
        t1_debias,
        t1_bet,
        t1_mask,
        ref_epi_basic,
        ref_epi,
        ref_epi_bet,
        ref_epi_mask,
        atlas_xfm,
        rigid_body_params,
        func_ab,
        atlas_resampled,
    ) = create_pipeline_symlinks(output_path, kwargs)

    # use epi_path as working directory
    with working_directory((Path(output_path) / epi_path).as_posix()):
        # create stages
        setup_stage = Stage(
            pd_setup,
            stage_outputs=["fmap", "fmapmag", "fmapmagbrain", "echospacing", "pedir"],
            hash_output="0_setup",
            stage_name="0_setup",
            output_path="0_setup",
            func=kwargs["func"],
            metadata=kwargs["metadata"],
            bids_path=bids_path,
            subject=kwargs["subject"],
            session=kwargs["session"],
        )
        epi_reg_stage = Stage(
            pd_epi_reg,
            stage_outputs=["epi_to_anat_xfm_afni", "afni_warp"],
            hash_output="1_epi_reg",
            stage_name="1_epi_reg",
            output_path="1_epi_reg",
            epi=ref_epi.as_posix(),
            t1=t1_debias.as_posix(),
            t1brain=t1_bet.as_posix(),
        )
        combine_transforms_stage = Stage(
            pd_combine_transforms,
            stage_outputs=["0"],
            hash_output="2_combine_transforms",
            stage_name="2_combine_transforms",
            output_path="2_combine_transforms",
            atlas_xfm=atlas_xfm.as_posix(),
            rigid_body_params=rigid_body_params.as_posix(),
            func=func_ab.as_posix(),
            atlas_resampled=atlas_resampled.as_posix(),
            final_dir="output_data",
            disable_jac_mod=DISABLE_JAC_MOD,
        )

        # define pipleine
        pipeline = Pipeline(
            [("start", setup_stage), (setup_stage, epi_reg_stage), (epi_reg_stage, combine_transforms_stage)]
        )

        # run pipeline
        pipeline.run()


@create_output_path
def rpe_setup(output_path: str, func: str, metadata: dict, bids_path: str, subject: str, session: str) -> tuple[str]:
    # grab ped for functional image from metadata
    img = nib.load(func)
    ped = metadata["PhaseEncodingDirection"]
    ocode = "".join(nib.aff2axcodes(img.affine))
    odirection = {"i": ocode[0], "j": ocode[1], "k": ocode[2]}[ped[0]]
    idirection = {"R": "L", "L": "R", "A": "P", "P": "A", "I": "S", "S": "I"}
    direction = idirection[odirection] if ped[-1] == "-" else odirection
    ped = idirection[direction] + direction

    # get fieldmap data
    layout = BIDSLayout(bids_path)
    fmaps_AP = layout.get(datatype="fmap", direction="AP", subject=subject, session=session, extension=".nii.gz")
    fmaps_PA = layout.get(datatype="fmap", direction="PA", subject=subject, session=session, extension=".nii.gz")
    fmaps_AP.sort(key=lambda x: x.filename)
    fmaps_PA.sort(key=lambda x: x.filename)

    # setup ped info for datain file
    ped_dict = {"i": "1 0 0", "j": "0 1 0", "k": "0 0 1", "i-": "-1 0 0", "j-": "0 -1 0", "k-": "0 0 -1"}

    # create the imain file
    concat_data = list()
    datain_string = ""
    for ap, pa in zip(fmaps_AP, fmaps_PA):
        # get readouttime
        pedAP = ap.entities["PhaseEncodingDirection"]
        pedPA = pa.entities["PhaseEncodingDirection"]
        try:
            readouttimeAP = ap.entities["TotalReadoutTime"]
            readouttimePA = pa.entities["TotalReadoutTime"]
        except KeyError:
            logging.info("No TotalReadoutTime exists. Falling back to EffectiveEchoSpacing computation")
            readouttimeAP = (ap.entities["ReconMatrixPE"] - 1) * ap.entities["EffectiveEchoSpacing"]
            readouttimePA = (pa.entities["ReconMatrixPE"] - 1) * pa.entities["EffectiveEchoSpacing"]

        # load fieldmap images
        ap_img = nib.load(ap.path)
        pa_img = nib.load(pa.path)

        # check to make sure if fmaps are the same size as first fmap entry
        # if not just skip it
        if len(concat_data) > 0:
            dshape = concat_data[0].shape
            ap_shape = ap_img.shape
            pa_shape = pa_img.shape
            if not (np.all(dshape == ap_shape) and np.all(dshape == pa_shape)):
                continue

        # append fmap data to list
        if len(ap_img.shape) == 4:
            concat_data.append(ap_img.get_fdata()[:, :, :, 0])
        else:
            concat_data.append(ap_img.get_fdata())
        if len(pa_img.shape) == 4:
            concat_data.append(pa_img.get_fdata()[:, :, :, 0])
        else:
            concat_data.append(pa_img.get_fdata())

        # append datain string
        datain_string += "{} {}\n".format(ped_dict[pedAP], readouttimeAP)
        datain_string += "{} {}\n".format(ped_dict[pedPA], readouttimePA)

    # concatenate data and write to image
    data = np.stack(concat_data, axis=3)
    imain_file = (Path(output_path) / "imain.nii.gz").as_posix()
    deoblique(nib.Nifti1Image(data, ap_img.affine)).to_filename(imain_file)

    # write datain in file
    datain_file = (Path(output_path) / "datain.txt").as_posix()
    with open(datain_file, "w") as f:
        f.write(datain_string)

    # format fieldmap paths
    fmaps_AP_list = [f.path for f in fmaps_AP]
    fmaps_PA_list = [f.path for f in fmaps_PA]

    # return files
    return (imain_file, datain_file, ped, fmaps_AP_list, fmaps_PA_list)


@create_output_path
def topup(output_path: str, imain_file: str, datain_file: str) -> tuple[str]:
    # setup output paths
    output_path = Path(output_path)
    out_files = (output_path / "out").as_posix()
    iout_file = (output_path / "iout.nii.gz").as_posix()
    dfout_files = (output_path / "dfout").as_posix()
    fout_file = (output_path / "fout.nii.gz").as_posix()
    rbmout_files = (output_path / "rbmout").as_posix()
    jacout_files = (output_path / "jacout").as_posix()

    # topup
    run_process(
        f"topup --imain={imain_file} --datain={datain_file} --config=b02b0.cnf "
        f"--out={out_files} --iout={iout_file} --dfout={dfout_files} --fout={fout_file} "
        f"--rbmout={rbmout_files} --jacout={jacout_files} -v"
    )

    # return top up outputs
    return (iout_file, dfout_files, fout_file, rbmout_files, jacout_files)


@create_output_path
def epi_reg(
    output_path: str,
    ref_epi: str,
    t1_debias: str,
    t1_bet: str,
    ped: str,
    imain_file: str,
    fmaps_AP: list[str],
    fmaps_PA: list[str],
    dfout_files: str,
    jacout_files: str,
    disable_jac_mod: bool = False,
) -> tuple[str]:
    # align func to fmap
    if ped in Path(fmaps_AP[0]).name:
        fmap_idx = 1
    elif ped in Path(fmaps_PA[0]).name:
        fmap_idx = 2
    else:
        raise ValueError("Well this is awkward... this error should not occur, and yet it has...")

    # create the reference fieldmap file to use based off the func ped
    imain_img = nib.load(imain_file)
    fmap_ref = (Path(output_path) / "fmap_ref.nii.gz").as_posix()
    nib.Nifti1Image(imain_img.get_fdata()[:, :, :, fmap_idx - 1], imain_img.affine, imain_img.header).to_filename(
        fmap_ref
    )

    # convert the warp to afni format
    fmap_ref_img = nib.load(fmap_ref)
    # load correct warp based on idx
    warp_img = nib.load(dfout_files + "_{:0>2d}.nii.gz".format(fmap_idx))
    afni_warp = (Path(output_path) / "afni_warp.nii.gz").as_posix()
    nib.Nifti1Image(warp_img.get_fdata()[:, :, :, np.newaxis, :] * -1, fmap_ref_img.affine).to_filename(afni_warp)

    # add affine info to the jacobian
    jacobian_img = nib.load(jacout_files + "_{:0>2d}.nii.gz".format(fmap_idx))
    jacobian = (Path(output_path) / "jacmag.nii.gz").as_posix()
    nib.Nifti1Image(jacobian_img.get_fdata(), fmap_ref_img.affine).to_filename(jacobian)

    # align the reference to the fmap ref
    ref_epi_fmapaligned = repath(output_path, append_suffix(ref_epi, "_fmapaligned"))
    ref_to_fmap_xfm = (Path(output_path) / "ref_to_fmap_xfm.mat").as_posix()
    run_process(f"flirt -dof 6 -in {ref_epi} -ref {fmap_ref} -omat {ref_to_fmap_xfm} -out {ref_epi_fmapaligned}")

    # convert the affine file to afni format
    ref_to_fmap_xfm_afni = (Path(output_path) / "ref_to_fmap_xfm.aff12.1D").as_posix()
    convert_affine_file(ref_to_fmap_xfm_afni, ref_to_fmap_xfm, "afni", target=fmap_ref, source=ref_epi)

    # combine transforms and apply to ref epi
    ref_epi_fmapaligned_unwarped = append_suffix(ref_epi_fmapaligned, "_unwarped")
    NwarpApply(ref_epi_fmapaligned_unwarped, fmap_ref, ref_epi, [afni_warp, ref_to_fmap_xfm_afni])

    # and modulate the jacobian
    if not disable_jac_mod:
        run_process(f"fslmaths {ref_epi_fmapaligned_unwarped} -mul {jacobian} {ref_epi_fmapaligned_unwarped}")

    # run epi_reg
    epi_reg_files = (Path(output_path) / "epi_reg_out").as_posix()
    run_process(
        f"epi_reg --epi={ref_epi_fmapaligned_unwarped} --t1={t1_debias} --t1brain={t1_bet} --out={epi_reg_files} -v"
    )
    fmap_to_anat_xfm = (Path(output_path) / "fmap_to_anat_xfm.mat").as_posix()
    shutil.copy2(epi_reg_files + ".mat", fmap_to_anat_xfm)

    # convert the fmap to anat transform to afni format
    fmap_to_anat_xfm_afni = (Path(output_path) / "fmap_to_anat_xfm.aff12.1D").as_posix()
    convert_affine_file(
        fmap_to_anat_xfm_afni, fmap_to_anat_xfm, "afni", target=t1_debias, source=ref_epi_fmapaligned_unwarped
    )

    # return outputs
    return (epi_reg_files, fmap_to_anat_xfm_afni, afni_warp, ref_to_fmap_xfm_afni, jacobian)


@create_output_path
def combine_transforms(
    output_path: str,
    atlas_xfm: str,
    fmap_to_anat_xfm_afni: str,
    afni_warp: str,
    ref_to_fmap_xfm_afni: str,
    rigid_body_params: str,
    func: str,
    atlas_resampled: str,
    final_dir: str,
    jacobian: str = None,
    disable_jac_mod: bool = False,
) -> None:
    # make sure rigid body params named correctly
    rigid_body_xfm = (Path(output_path) / "rigid_body.aff12.1D").as_posix()
    shutil.copy2(rigid_body_params, rigid_body_xfm)

    # apply warps to func
    Path(final_dir).mkdir(exist_ok=True)
    func_atlas = repath(final_dir, append_suffix(func, "_trio"))
    NwarpApply(
        func_atlas,
        atlas_resampled,
        func,
        [atlas_xfm, fmap_to_anat_xfm_afni, afni_warp, ref_to_fmap_xfm_afni, rigid_body_xfm],
    )

    # if jacobian defined, modulate by jacobian
    if jacobian and not disable_jac_mod:
        jacobian_atlas = repath(output_path, append_suffix(jacobian, "_trio"))
        # get jacobian in correct space
        NwarpApply(
            jacobian_atlas,
            atlas_resampled,
            jacobian,
            [atlas_xfm, fmap_to_anat_xfm_afni, f"'IDENT({jacobian})'"],
        )
        run_process(f"fslmaths {func_atlas} -mul {jacobian_atlas} {func_atlas}")


@create_output_path
@use_abspaths
def topup_proc(output_path: str, **kwargs) -> None:
    # make symlinks to pipeline outputs
    (
        bids_path,
        anat_path,
        epi_path,
        t1,
        t1_debias,
        t1_bet,
        t1_mask,
        ref_epi_basic,
        ref_epi,
        ref_epi_bet,
        ref_epi_mask,
        atlas_xfm,
        rigid_body_params,
        func_ab,
        atlas_resampled,
    ) = create_pipeline_symlinks(output_path, kwargs)

    # use epi_path as working directory
    with working_directory((Path(output_path) / epi_path).as_posix()):
        # create stages
        setup_stage = Stage(
            rpe_setup,
            stage_outputs=["imain_file", "datain_file", "ped", "fmaps_AP", "fmaps_PA"],
            hash_output="0_setup",
            stage_name="0_setup",
            output_path="0_setup",
            func=kwargs["func"],
            metadata=kwargs["metadata"],
            bids_path=bids_path,
            subject=kwargs["subject"],
            session=kwargs["session"],
        )
        topup_stage = Stage(
            topup,
            stage_outputs=["iout_file", "dfout_files", "fout_file", "rbmout_files", "jacout_files"],
            hash_output="1_topup",
            stage_name="1_topup",
            output_path="1_topup",
        )
        epi_reg_stage = Stage(
            epi_reg,
            stage_outputs=["epi_reg_files", "fmap_to_anat_xfm_afni", "afni_warp", "ref_to_fmap_xfm_afni", "jacobian"],
            hash_output="2_epi_reg",
            stage_name="2_epi_reg",
            output_path="2_epi_reg",
            ref_epi=ref_epi.as_posix(),
            t1_debias=t1_debias.as_posix(),
            t1_bet=t1_bet.as_posix(),
            disable_jac_mod=DISABLE_JAC_MOD,
        )
        combine_transforms_stage = Stage(
            combine_transforms,
            stage_outputs=["0"],
            hash_output="3_combine_transforms",
            stage_name="3_combine_transforms",
            output_path="3_combine_transforms",
            atlas_xfm=atlas_xfm.as_posix(),
            rigid_body_params=rigid_body_params.as_posix(),
            func=func_ab.as_posix(),
            atlas_resampled=atlas_resampled.as_posix(),
            final_dir="output_data",
            disable_jac_mod=DISABLE_JAC_MOD,
        )

        # define pipleine
        pipeline = Pipeline(
            [
                ("start", setup_stage),
                (setup_stage, topup_stage),
                ((setup_stage, topup_stage), epi_reg_stage),
                ((topup_stage, epi_reg_stage), combine_transforms_stage),
            ]
        )

        # run pipeline
        pipeline.run()


@create_output_path
def qwarp_setup(output_path: str, func: str, metadata: dict, bids_path: str, subject: str, session: str) -> tuple[str]:
    # grab ped for functional image from metadata
    img = nib.load(func)
    ped = metadata["PhaseEncodingDirection"]
    ocode = "".join(nib.aff2axcodes(img.affine))
    odirection = {"i": ocode[0], "j": ocode[1], "k": ocode[2]}[ped[0]]
    idirection = {"R": "L", "L": "R", "A": "P", "P": "A", "I": "S", "S": "I"}
    direction = idirection[odirection] if ped[-1] == "-" else odirection
    ped = idirection[direction] + direction

    # get fieldmap data
    layout = BIDSLayout(bids_path)
    fmaps_AP = layout.get(datatype="fmap", direction="AP", subject=subject, session=session, extension=".nii.gz")
    fmaps_PA = layout.get(datatype="fmap", direction="PA", subject=subject, session=session, extension=".nii.gz")
    fmaps_AP.sort(key=lambda x: x.filename)
    fmaps_PA.sort(key=lambda x: x.filename)

    # format fieldmap paths
    fmap_AP = fmaps_AP[0]
    fmap_PA = fmaps_PA[0]

    # deoblique the fieldmaps
    fmap_AP_do_file = repath(output_path, append_suffix(fmap_AP.path, "_do"))
    deoblique(fmap_AP.get_image()).to_filename(fmap_AP_do_file)
    fmap_PA_do_file = repath(output_path, append_suffix(fmap_PA.path, "_do"))
    deoblique(fmap_PA.get_image()).to_filename(fmap_PA_do_file)

    # detect which fieldmap to align to
    if ped in fmap_AP.filename:
        ref_fmap = fmap_AP_do_file
        source_fmap = fmap_PA_do_file
    elif ped in fmap_PA.filename:
        ref_fmap = fmap_PA_do_file
        source_fmap = fmap_AP_do_file

    # return files
    return (ped, ref_fmap, source_fmap)


@create_output_path
def align_and_qwarp(
    output_path: str, ref_fmap: str, source_fmap: str, epi: str, epi_bet: str, t1_bet: str
) -> tuple[str]:
    # align the functional to the fieldmap
    epi_to_fmap_xfm_afni = (Path(output_path) / "epi_to_fmap_xfm.aff12.1D").as_posix()
    epi_to_fmap_out = (Path(output_path) / "epi_to_fmap_out.nii.gz").as_posix()
    run_process(
        f"3dAllineate -base {ref_fmap} -source {epi} -1Dmatrix_save {epi_to_fmap_xfm_afni} "
        f"-prefix {epi_to_fmap_out} -warp shift_rotate -cost nmi -final wsinc5 -nmatch 100% -twopass -overwrite"
    )

    # unwarp fieldmaps
    unwarp = (Path(output_path) / "unwarp.nii.gz").as_posix()
    run_process(f"3dQwarp -base {ref_fmap} -source {source_fmap} -prefix {unwarp} -plusminus -minpatch 7 -overwrite")

    # apply alignment and unwarp
    unwarp_file = append_suffix(unwarp, "_MINUS_WARP")
    epi_bet_unwarped = repath(output_path, append_suffix(epi_bet, "_unwarped"))
    NwarpApply(epi_bet_unwarped, ref_fmap, epi_bet, [unwarp_file, epi_to_fmap_xfm_afni])

    # align functional to the anat
    epi_bet_unwarped_anataligned = append_suffix(epi_bet_unwarped, "_anataligned")
    epi_to_anat_xfm_afni = (Path(output_path) / "epi_to_anat_xfm.aff12.1D").as_posix()
    run_process(
        f"3dAllineate -prefix {epi_bet_unwarped_anataligned} -base {t1_bet} -source {epi_bet_unwarped} "
        f"-1Dmatrix_save {epi_to_anat_xfm_afni} -warp shift_rotate "
        f"-cost nmi -final wsinc5 -nmatch 100% -twopass -overwrite"
    )

    # return outputs
    return (epi_to_fmap_xfm_afni, unwarp_file, epi_to_anat_xfm_afni)


@create_output_path
@use_abspaths
def qwarp_proc(output_path: str, **kwargs) -> None:
    # make symlinks to pipeline outputs
    (
        bids_path,
        anat_path,
        epi_path,
        t1,
        t1_debias,
        t1_bet,
        t1_mask,
        ref_epi_basic,
        ref_epi,
        ref_epi_bet,
        ref_epi_mask,
        atlas_xfm,
        rigid_body_params,
        func_ab,
        atlas_resampled,
    ) = create_pipeline_symlinks(output_path, kwargs)

    # use epi_path as working directory
    with working_directory((Path(output_path) / epi_path).as_posix()):
        # create stages
        setup_stage = Stage(
            qwarp_setup,
            stage_outputs=["ped", "ref_fmap", "source_fmap"],
            hash_output="0_setup",
            stage_name="0_setup",
            output_path="0_setup",
            func=kwargs["func"],
            metadata=kwargs["metadata"],
            bids_path=bids_path,
            subject=kwargs["subject"],
            session=kwargs["session"],
        )
        align_and_qwarp_stage = Stage(
            align_and_qwarp,
            stage_outputs=["ref_to_fmap_xfm_afni", "afni_warp", "fmap_to_anat_xfm_afni"],
            hash_output="1_align_and_qwarp_stage",
            stage_name="1_align_and_qwarp_stage",
            output_path="1_align_and_qwarp_stage",
            epi=ref_epi.as_posix(),
            epi_bet=ref_epi_bet.as_posix(),
            t1_bet=t1_bet.as_posix(),
        )
        combine_transforms_stage = Stage(
            combine_transforms,
            stage_outputs=["0"],
            hash_output="2_combine_transforms",
            stage_name="2_combine_transforms",
            output_path="2_combine_transforms",
            atlas_xfm=atlas_xfm.as_posix(),
            rigid_body_params=rigid_body_params.as_posix(),
            func=func_ab.as_posix(),
            atlas_resampled=atlas_resampled.as_posix(),
            final_dir="output_data",
        )

        # define pipleine
        pipeline = Pipeline(
            [
                ("start", setup_stage),
                (setup_stage, align_and_qwarp_stage),
                (align_and_qwarp_stage, combine_transforms_stage),
            ]
        )

        # run pipeline
        pipeline.run()


@create_output_path
def ants_setup(output_path: str, t1_debias: str, t1_mask: str) -> tuple[str]:
    # get mni atlas
    mni_atlas = (Path(ATLASDIR) / "mni_icbm152_t1_tal_nlin_sym_09c.nii.gz").as_posix()

    # align mni to t1
    output_basename = (Path(output_path) / "mni2t1_").as_posix()
    output_warp = output_basename + "warped.nii.gz"
    output_iwarp = output_basename + "inversewarped.nii.gz"
    run_process(
        f"antsRegistration -d 3 -o [{output_basename},{output_warp},{output_iwarp}] "
        f"-n LanczosWindowedSinc -w [0.005,0.995] -u 1 -x {t1_mask} -v "
        f"--initial-moving-transform [{t1_debias},{mni_atlas},1] --transform Rigid[0.1] "
        f"--metric Mattes[{t1_debias},{mni_atlas},1,32,Regular,0.25] --convergence [1000x500x250x100,1e-6,10] "
        f"--shrink-factors 8x4x2x1 --smoothing-sigmas 3x2x1x0vox --transform Affine[0.1] "
        f"--metric Mattes[{t1_debias},{mni_atlas},1,32,Regular,0.25] --convergence [1000x500x250x100,1e-6,10] "
        f"--shrink-factors 8x4x2x1 --smoothing-sigmas 3x2x1x0vox"
    )
    inverse_mni_transform = (Path(output_path) / "mni2t1_0GenericAffine.mat").as_posix()

    # return transform
    return inverse_mni_transform


@create_output_path
def ants_sdc(
    output_path: str,
    ref_epi: str,
    ref_epi_mask: str,
    metadata: dict,
    t1_debias: str,
    t1_mask: str,
    std2anat_xfm: str,
):
    # create ants SDC workflow
    workflow = Workflow("1_ants_sdc", base_dir=Path(".").resolve().as_posix())

    # preprocess workflow
    wf1 = init_syn_preprocessing_wf(omp_nthreads=8)
    wf1_input_node = wf1.get_node("inputnode")
    wf1_input_node.inputs.in_epis = [
        ref_epi,
    ]
    wf1_input_node.inputs.in_meta = [
        metadata,
    ]
    wf1_input_node.inputs.t_masks = [
        True,
    ]
    wf1_input_node.inputs.in_anat = t1_debias
    wf1_input_node.inputs.mask_anat = t1_mask
    wf1_input_node.inputs.std2anat_xfm = Path(std2anat_xfm).resolve().as_posix()

    # correction workflow
    wf2 = init_syn_sdc_wf(omp_nthreads=8)
    wf2_input_node = wf2.get_node("inputnode")
    wf2_input_node.inputs.epi_mask = ref_epi_mask

    # unwarp workflow
    wf3 = init_unwarp_wf(omp_nthreads=8)
    wf3_input_node = wf3.get_node("inputnode")
    wf3_input_node.inputs.distorted = ref_epi
    wf3_input_node.inputs.metadata = metadata

    # create datasink
    datasink = Node(DataSink(), name="output_sink")
    datasink.inputs.base_directory = Path("1_ants_sdc").resolve().as_posix()
    datasink.inputs.substitutions = [("_syn0InverseWarp_fieldmap_trans_extra", ""), ("_xfm", "_warp")]

    # connect workflows
    workflow.connect(wf1, "outputnode.epi_ref", wf2, "inputnode.epi_ref")
    workflow.connect(wf1, "outputnode.anat_ref", wf2, "inputnode.anat_ref")
    workflow.connect(wf1, "outputnode.anat_mask", wf2, "inputnode.anat_mask")
    workflow.connect(wf1, "outputnode.sd_prior", wf2, "inputnode.sd_prior")
    workflow.connect(wf2, "outputnode.fmap", wf3, "inputnode.fmap_coeff")
    workflow.connect(wf3, "outputnode.fieldmap", datasink, "outputs")
    workflow.connect(wf3, "outputnode.fieldwarp", datasink, "outputs.@a")

    # run workflow
    workflow.run()

    # apply warp to ref_func
    warp = repath(os.path.join(output_path, "outputs"), append_suffix(ref_epi, "_warp"))
    ref_epi_unwarped = repath(output_path, append_suffix(ref_epi, "_unwarped"))
    NwarpApply(
        ref_epi_unwarped,
        ref_epi,
        ref_epi,
        [
            warp,
        ],
    )

    # return files
    return (warp, ref_epi_unwarped)


@create_output_path
def ants_align_anat(output_path: str, ref_epi_unwarped: str, t1_debias: str, t1_bet: str) -> tuple[str]:
    # align unwarped to T1 with epi_reg
    epi_reg_files = (Path(output_path) / "epi_reg_out").as_posix()
    run_process(f"epi_reg --epi={ref_epi_unwarped} --t1={t1_debias} --t1brain={t1_bet} --out={epi_reg_files} -v")
    epi_reg_xfm = epi_reg_files + ".mat"

    # convert from fsl to afni type
    epi_to_anat_xfm_afni = (Path(output_path) / "epi_to_anat_xfm.aff12.1D").as_posix()
    convert_affine_file(epi_to_anat_xfm_afni, epi_reg_xfm, "afni", target=t1_debias, source=ref_epi_unwarped)

    # return files
    return epi_to_anat_xfm_afni


@create_output_path
@use_abspaths
def ants_proc(output_path: str, **kwargs) -> None:
    # set up nipype logging
    # config.set('logging', 'workflow_level', 'DEBUG')
    config.set("execution", "hash_method", "content")
    nilogging.update_logging(config)

    # make symlinks to pipeline outputs
    (
        bids_path,
        anat_path,
        epi_path,
        t1,
        t1_debias,
        t1_bet,
        t1_mask,
        ref_epi_basic,
        ref_epi,
        ref_epi_bet,
        ref_epi_mask,
        atlas_xfm,
        rigid_body_params,
        func_ab,
        atlas_resampled,
    ) = create_pipeline_symlinks(output_path, kwargs)

    # use epi_path as working directory
    with working_directory((Path(output_path) / epi_path).as_posix()):
        # run alignment from mni to t1
        setup_stage = Stage(
            ants_setup,
            stage_outputs=["std2anat_xfm"],
            hash_output="0_setup",
            stage_name="0_setup",
            output_path="0_setup",
            t1_debias=t1_debias.as_posix(),
            t1_mask=t1_mask.as_posix(),
        )
        ants_sdc_stage = Stage(
            ants_sdc,
            stage_outputs=["afni_warp", "ref_epi_unwarped"],
            hash_output="1_ants_sdc",
            stage_name="1_ants_sdc",
            output_path="1_ants_sdc",
            ref_epi=ref_epi.as_posix(),
            ref_epi_mask=ref_epi_mask.as_posix(),
            metadata=kwargs["metadata"],
            t1_debias=t1_debias.as_posix(),
            t1_mask=t1_mask.as_posix(),
        )
        ants_align_anat_stage = Stage(
            ants_align_anat,
            stage_outputs=["epi_to_anat_xfm_afni"],
            hash_output="2_align_anat",
            stage_name="2_align_anat",
            output_path="2_align_anat",
            t1_debias=t1_debias.as_posix(),
            t1_bet=t1_bet.as_posix(),
        )
        combine_transforms_stage = Stage(
            pd_combine_transforms,
            stage_outputs=["0"],
            hash_output="3_combine_transforms",
            stage_name="3_combine_transforms",
            output_path="3_combine_transforms",
            atlas_xfm=atlas_xfm.as_posix(),
            rigid_body_params=rigid_body_params.as_posix(),
            func=func_ab.as_posix(),
            atlas_resampled=atlas_resampled.as_posix(),
            final_dir="output_data",
        )

        # define pipleine
        pipeline = Pipeline(
            [
                ("start", setup_stage),
                (setup_stage, ants_sdc_stage),
                (ants_sdc_stage, ants_align_anat_stage),
                ((ants_sdc_stage, ants_align_anat_stage), combine_transforms_stage),
            ]
        )

        # run pipeline
        pipeline.run()


@create_output_path
def synb0_setup(output_path: str, t1: str, t1_bet: str, epi: str, raw_epi: str, metadata: dict) -> tuple[str]:
    # copy T1 and epi into directory
    t1_path = (Path(output_path) / "T1.nii.gz").as_posix()
    t1_mask_path = (Path(output_path) / "T1_mask.nii.gz").as_posix()
    b0_path = (Path(output_path) / "b0.nii.gz").as_posix()
    shutil.copy2(t1, t1_path)
    shutil.copy2(t1_bet, t1_mask_path)
    shutil.copy2(epi, b0_path)

    # get the total read out time of the epi
    try:
        readouttime = metadata["TotalReadoutTime"]
    except KeyError:
        logging.info("No TotalReadoutTime exists. Falling back to EffectiveEchoSpacing computation")
        try:
            readouttime = (metadata["ReconMatrixPE"] - 1) * metadata["EffectiveEchoSpacing"]
        except KeyError:
            ReconMatrixPE = nib.load(raw_epi).header.get("dim")[2]
            readouttime = (ReconMatrixPE - 1) * metadata["EffectiveEchoSpacing"]
            logging.info(f"Estimating ReconMatrixPE from Nifti header (={ReconMatrixPE}). Hopefully this is right...")

    # create acq_params
    acq_params = (Path(output_path) / "acqparams.txt").as_posix()
    with open(acq_params, "w") as f:
        f.write(f"0 1 0 {readouttime}\n")
        f.write(f"0 1 0 0\n")

    # create return value for inputs
    synb0_input = output_path

    # return outputs
    return (t1_path, t1_mask_path, b0_path, acq_params, synb0_input)


@create_output_path
def run_synb0(output_path: str, synb0_input: str, acqparams: str, license: str) -> tuple[str]:
    # call docker image
    outputs = Path(output_path).resolve().as_posix()
    inputs = Path(synb0_input).resolve().as_posix()
    run_process(
        f"docker run -t --rm -u $(id -u):$(id -g) "
        f"-v {license}:/extra/freesurfer/license.txt -v {inputs}:/INPUTS -v {outputs}:/OUTPUTS hansencb/synb0 --notopup"
    )

    # setup output paths for topup
    output_path = Path(output_path)
    out_files = (output_path / "out").as_posix()
    iout_file = (output_path / "iout.nii.gz").as_posix()
    dfout_files = (output_path / "dfout").as_posix()
    fout_file = (output_path / "fout.nii.gz").as_posix()
    rbmout_files = (output_path / "rbmout").as_posix()
    jacout_files = (output_path / "jacout").as_posix()

    # run topup
    b0_all = (Path(output_path) / "b0_all.nii.gz").as_posix()
    b0_d_smooth = (Path(output_path) / "b0_d_smooth.nii.gz").as_posix()
    b0_u = (Path(output_path) / "b0_u.nii.gz").as_posix()
    run_process(f"fslmerge -t {b0_all} {b0_d_smooth} {b0_u}")
    run_process(
        f"topup -v --imain={b0_all} --datain={acqparams} --config=b02b0.cnf --out={out_files} "
        f"--iout={iout_file} --dfout={dfout_files} --fout={fout_file} --rbmout={rbmout_files} --jacout={jacout_files} "
        f"--subsamp=1,1,1,1,1,1,1,1,1 --miter=10,10,10,10,10,20,20,30,30 "
        f"--lambda=0.00033,0.000067,0.0000067,0.000001,0.00000033,0.000000033,"
        f"0.0000000033,0.000000000033,0.00000000000067 --scale=0"
    )

    # return top up outputs
    return (iout_file, dfout_files, fout_file, rbmout_files, jacout_files)


@create_output_path
def synb0_epi_reg(
    output_path: str,
    ref_epi: str,
    t1_debias: str,
    t1_bet: str,
    dfout_files: str,
    jacout_files: str,
) -> tuple[str]:
    # convert warp to afni format
    ref_epi_img = nib.load(ref_epi)
    warp_img = nib.load(dfout_files + "_{:0>2d}.nii.gz".format(1))
    jac_img = nib.load(jacout_files + "_{:0>2d}.nii.gz".format(1))
    afni_warp = (Path(output_path) / "afni_warp.nii.gz").as_posix()
    jacobian = (Path(output_path) / "jacmag.nii.gz").as_posix()

    # we flip axis 0 b/c warps are somehow reversed???
    affine = ref_epi_img.affine.copy()
    new_data = np.flip(warp_img.get_fdata(), axis=0)
    nib.Nifti1Image(warp_img.get_fdata()[:, :, :, np.newaxis, :] * -1, affine).to_filename(afni_warp)
    # do the same for jacobian
    nib.Nifti1Image(jac_img.get_fdata(), ref_epi_img.affine).to_filename(jacobian)

    # apply warp to ref epi
    ref_epi_unwarped = repath(output_path, append_suffix(ref_epi, "_unwarped"))
    NwarpApply(
        ref_epi_unwarped,
        ref_epi,
        ref_epi,
        [
            afni_warp,
        ],
    )
    # apply jacobian modulation
    run_process(f"fslmaths {ref_epi_unwarped} -mul {jacobian} {ref_epi_unwarped}")

    # run epi_reg
    epi_reg_files = (Path(output_path) / "epi_reg_out").as_posix()
    run_process(f"epi_reg --epi={ref_epi_unwarped} --t1={t1_debias} --t1brain={t1_bet} --out={epi_reg_files} -v")
    fmap_to_anat_xfm = (Path(output_path) / "fmap_to_anat_xfm.mat").as_posix()
    shutil.copy2(epi_reg_files + ".mat", fmap_to_anat_xfm)

    # convert the fmap to anat transform to afni format
    fmap_to_anat_xfm_afni = (Path(output_path) / "fmap_to_anat_xfm.aff12.1D").as_posix()
    convert_affine_file(fmap_to_anat_xfm_afni, fmap_to_anat_xfm, "afni", target=t1_debias, source=ref_epi_unwarped)

    # return outputs
    return (epi_reg_files, fmap_to_anat_xfm_afni, afni_warp, jacobian)


@create_output_path
@use_abspaths
def synb0_proc(output_path: str, **kwargs) -> None:
    # make symlinks to pipeline outputs
    (
        bids_path,
        anat_path,
        epi_path,
        t1,
        t1_debias,
        t1_bet,
        t1_mask,
        ref_epi_basic,
        ref_epi,
        ref_epi_bet,
        ref_epi_mask,
        atlas_xfm,
        rigid_body_params,
        func_ab,
        atlas_resampled,
    ) = create_pipeline_symlinks(output_path, kwargs)

    # use epi_path as working directory
    with working_directory((Path(output_path) / epi_path).as_posix()):
        # define stages
        setup_stage = Stage(
            synb0_setup,
            stage_outputs=["t1", "t1_mask", "b0", "acqparams", "synb0_input"],
            hash_output="0_setup",
            stage_name="0_setup",
            output_path="0_setup",
            t1=t1.as_posix(),
            t1_bet=t1_bet.as_posix(),
            epi=ref_epi.as_posix(),
            raw_epi=ref_epi_basic.as_posix(),
            metadata=kwargs["metadata"],
        )
        run_synb0_stage = Stage(
            run_synb0,
            stage_outputs=["iout_file", "dfout_files", "fout_file", "rbmout_files", "jacout_files"],
            hash_output="1_run_synb0",
            stage_name="1_run_synb0",
            output_path="1_run_synb0",
            license=FSLICENSE,
        )
        epi_reg_stage = Stage(
            synb0_epi_reg,
            stage_outputs=["epi_reg_files", "epi_to_anat_xfm_afni", "afni_warp", "jacobian"],
            hash_output="2_epi_reg",
            stage_name="2_epi_reg",
            output_path="2_epi_reg",
            ref_epi=ref_epi.as_posix(),
            t1_debias=t1_debias.as_posix(),
            t1_bet=t1_bet.as_posix(),
        )
        combine_transforms_stage = Stage(
            pd_combine_transforms,
            stage_outputs=["0"],
            hash_output="3_combine_transforms",
            stage_name="3_combine_transforms",
            output_path="3_combine_transforms",
            atlas_xfm=atlas_xfm.as_posix(),
            rigid_body_params=rigid_body_params.as_posix(),
            func=func_ab.as_posix(),
            atlas_resampled=atlas_resampled.as_posix(),
            final_dir="output_data",
        )

        # setup pipeline
        pipeline = Pipeline(
            [
                ("start", setup_stage),
                (setup_stage, run_synb0_stage),
                (run_synb0_stage, epi_reg_stage),
                (epi_reg_stage, combine_transforms_stage),
            ]
        )

        # run pipeline
        pipeline.run()


# define processor choices
PROCESSOR_CHOICES = {
    "spinecho": topup_proc,
    "gre": pd_proc,
    "spinecho_afni": qwarp_proc,
    "fmapless_ants": ants_proc,
    "fmapless_synb0": synb0_proc,
}


# set default FSLICENSE variable
FSLICENSE = "/opt/freesurfer/license.txt"

# set default flag for jacobian modulation
DISABLE_JAC_MOD = False


def main():
    # create a command line parser
    parser = argparse.ArgumentParser(
        "Run fieldmap corrections",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 09/14/2021",
    )
    parser.add_argument("bids_dir")
    parser.add_argument("pipeline_output_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--participant_label", nargs="+")
    parser.add_argument("--combine_sessions", action="store_true")
    parser.add_argument("-p", "--processor", default="spinecho", choices=[key for key in PROCESSOR_CHOICES])
    parser.add_argument("-d", "--disable_jac_mod", action="store_true")
    parser.add_argument("-l", "--license")

    # get arguments
    args = parser.parse_args()

    # set common arguments
    command.set_common(args, threads=False)

    # call common parser
    command.parse_common(args, parser)

    # setup logs
    setup_logging()

    # if set, use different freesurfer license path
    if args.license:
        global FSLICENSE
        FSLICENSE = args.license

    # disable jac mod if enabled
    if args.disable_jac_mod:
        global DISABLE_JAC_MOD
        DISABLE_JAC_MOD = True

    # run pipeline
    bids_proc(
        bids_path=args.bids_dir,
        output_path=args.output_dir,
        participant_label=args.participant_label,
        function_to_run=PROCESSOR_CHOICES[args.processor],
        pipeline_output_path=args.pipeline_output_dir,
        combine_sessions=args.combine_sessions,
    )
