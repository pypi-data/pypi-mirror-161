# pylint: disable=redefined-outer-name,unused-import
import os
import json
import logging
import numpy as np
import nibabel as nib
import pytest
from omni.interfaces.common import append_suffix
from omni.scripts.affine import main as affine
from omni.scripts.deoblique import main as deoblique
from omni.scripts.extract import main as extract
from omni.scripts.info import main as info
from omni.scripts.intmat2nifti import main as intmat2nifti
from omni.scripts.pipeline import main as pipeline
from omni.scripts.preprocess import main as preprocess
from omni.scripts.realign4d import main as realign4d
from omni.scripts.resample import main as resample
from omni.scripts.synthnoisemask import main as synthnoisemask
from omni.scripts.synthpreproc import main as synthpreproc
from omni.scripts.synthpreproc import generate_parser as synthpreproc_parser
from omni.scripts.synthregressionmask import main as synthregressionmask
from omni.scripts.synthtarget import main as synthtarget
from omni.scripts.synthunwarp import main as synthunwarp
from omni.scripts.synthunwarp import generate_parser as synthunwarp_parser
from omni.io import read_affine_file


# import pytest fixtures
from .. import (
    fake_epi_and_mask,
    fake_epi,
    afni_affine,
    fsl_affine,
    omni_affine,
    plumb_oblique_data,
    test_intmat,
    test_bids,
)

# checks
from .. import afni_exists


def test_affine(monkeypatch, tmp_path, afni_affine, fsl_affine, omni_affine):
    # separate img/affine fsl
    img = fsl_affine[1]
    fsl_affine = fsl_affine[0]

    # setup affines
    affines = [afni_affine, fsl_affine, omni_affine]

    # test conversions
    conversion_flags = ["-a", "-f", "-o"]
    affine_exts = [".aff12.1D", ".mat", ".affine"]

    # loop over conversion combinations
    for affine_file in affines:
        for gaffine_mat, ext, flag in zip(affines, affine_exts, conversion_flags):
            output_affine = tmp_path / ("test_output" + ext)
            arguments = ["omni_affine", str(output_affine), "-i", affine_file, flag]
            if ".mat" in affine_file or ext == ".mat":
                arguments += ["-t", img, "-s", img]
            monkeypatch.setattr("sys.argv", arguments)
            affine()
            matrix1, atype1 = read_affine_file(str(output_affine))
            matrix2, atype2 = read_affine_file(gaffine_mat)
            assert atype1 == atype2
            assert np.all(np.isclose(matrix1, matrix2))

    # generate an affine transform
    output_affine = tmp_path / "test.affine"
    monkeypatch.setattr("sys.argv", ["omni_affine", str(output_affine), "-r", "0", "0", "0", "10", "10", "10"])
    affine()
    assert output_affine.exists()

    # check conflicting flags
    with pytest.raises(ValueError):
        monkeypatch.setattr(
            "sys.argv", ["omni_affine", str(output_affine), "-i", omni_affine, "-r", "0", "0", "0", "10", "10", "10"]
        )
        affine()


def test_deoblique(monkeypatch, tmp_path, plumb_oblique_data):
    plumb_img = nib.load(plumb_oblique_data[0])
    deobliqued = str(tmp_path / "deobliqued.nii.gz")
    monkeypatch.setattr("sys.argv", ["omni_deoblique", plumb_oblique_data[1], deobliqued])
    deoblique()
    deobliqued_img = nib.load(deobliqued)
    assert np.all(np.isclose(plumb_img.affine, deobliqued_img.affine))


def test_extract(monkeypatch, tmp_path, fake_epi):
    test = tmp_path / "test.nii.gz"
    img = fake_epi[0]
    img.to_filename(test)
    test2 = tmp_path / "test2.nii.gz"
    monkeypatch.setattr("sys.argv", ["omni_extract", str(test), str(test2), "-l", "[0:1, 0:1, 0:1, 0:1]"])
    extract()
    img2 = nib.load(str(test2))
    assert img2.shape == (1, 1, 1, 1)

    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            "sys.argv",
            [
                "omni_extract",
                str(test),
                str(test2),
                "-l",
                "[This should fail!, This should fail!, This should fail!, This should fail!]",
            ],
        )
        extract()


def test_info(monkeypatch, tmp_path, fake_epi, capsys):
    test = tmp_path / "test.nii.gz"
    img = fake_epi[0]
    img.to_filename(test)
    monkeypatch.setattr("sys.argv", ["omni_info", str(test)])
    info()
    out, _ = capsys.readouterr()
    assert "nibabel.nifti1.Nifti1Header" in out


def test_intmat2nifti(monkeypatch, tmp_path, test_intmat):
    output_path = tmp_path / "output"
    output_path.mkdir()
    monkeypatch.setattr("sys.argv", ["omni_intmat2nifti", test_intmat, str(output_path), "-d", "59", "69", "59"])
    intmat2nifti()

    # loop over each nifti in directory
    for img_path in output_path.iterdir():
        img = nib.load(img_path)
        assert img.shape == (59, 69, 59)


def test_pipeline(monkeypatch, tmp_path, test_bids, caplog):
    output_path = tmp_path / "output"
    caplog.set_level(logging.INFO)
    monkeypatch.setattr("sys.argv", ["omni_pipeline", test_bids, str(output_path), "--dryrun", "--combine_sessions"])
    pipeline()
    assert caplog.records[4].getMessage() == "anat_path: sub-test/ses-test/anat/sub-test_ses-test"
    assert caplog.records[5].getMessage() == "func_path: sub-test/ses-test/func/sub-test_ses-test_task-rest_bold"
    assert caplog.records[6].getMessage() == "epi_path: sub-test/ses-test/func/sub-test_ses-test_task-rest_bold"


def test_preprocess(monkeypatch, tmp_path, plumb_oblique_data):
    test = plumb_oblique_data[0]
    test2 = tmp_path / "test2.nii.gz"
    monkeypatch.setattr("sys.argv", ["omni_preprocess", "saturate", str(test2), "-o", "img=%s" % str(test), "n=0.05"])
    preprocess()
    assert os.path.exists(test2)

    with pytest.raises(TypeError):
        monkeypatch.setattr(
            "sys.argv", ["omni_preprocess", "saturate", str(test2), "-o", "img=%s" % str(test), "n=error"]
        )
        preprocess()


def test_realign4d(monkeypatch, tmp_path, fake_epi):
    epi = tmp_path / "epi.nii.gz"
    fake_epi[0].to_filename(epi)
    metadata = fake_epi[1]
    output = tmp_path / "output"
    monkeypatch.setattr("sys.argv", ["omni_realign4d", str(epi), metadata, str(output), "-l", "1", "-s", "10"])
    realign4d()
    assert os.path.exists(str(output) + "_rb.params") and os.path.exists(str(output) + ".nii.gz")


def test_resample(monkeypatch, tmp_path, plumb_oblique_data, omni_affine):
    test = plumb_oblique_data[0]
    img = nib.load(test)
    test2 = tmp_path / "test2.nii.gz"

    monkeypatch.setattr("sys.argv", ["omni_resample", str(test), str(test), str(test2)])
    resample()
    img2 = nib.load(test2)
    assert np.all(np.isclose(img.get_fdata(), img2.get_fdata()))

    monkeypatch.setattr("sys.argv", ["omni_resample", str(test), str(test), str(test2), "-a", omni_affine])
    resample()
    img2 = nib.load(test2)
    assert img.shape == img2.shape
    assert not np.all(np.isclose(img.get_fdata(), img2.get_fdata()))

    monkeypatch.setattr(
        "sys.argv", ["omni_resample", str(test), str(test), str(test2), "-r", "10", "0", "0", "0", "0", "0"]
    )
    resample()
    img2 = nib.load(test2)
    assert img.shape == img2.shape
    assert not np.all(np.isclose(img.get_fdata(), img2.get_fdata()))


def test_synthnoisemask(monkeypatch, tmp_path, fake_epi_and_mask):
    epi = tmp_path / "epi.nii.gz"
    mask = tmp_path / "mask.nii.gz"
    fake_epi_and_mask[0].to_filename(epi)
    fake_epi_and_mask[1].to_filename(mask)
    output = tmp_path / "noise_mask.nii.gz"
    monkeypatch.setattr("sys.argv", ["omni_synthnoisemask", str(epi), str(mask), str(output), "-i", "1"])
    synthnoisemask()
    assert os.path.exists(str(output)) and os.path.exists(append_suffix(str(output), "_smooth"))


@afni_exists
def test_synthregressionmask(monkeypatch, tmp_path, fake_epi_and_mask, afni_affine):
    epi = tmp_path / "epi.nii.gz"
    mask = tmp_path / "mask.nii.gz"
    fake_epi_and_mask[0].to_filename(epi)
    fake_epi_and_mask[1].to_filename(mask)
    output_path = tmp_path / "output"
    output_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        "sys.argv",
        [
            "omni_synthregressionmask",
            str(mask),
            str(mask),
            str(epi),
            afni_affine,
            str(output_path),
            "-d",
            str(1),
            "-i",
            str(10),
            "-s",
            str(1),
        ],
    )
    synthregressionmask()
    regression_mask = output_path / "synth_regression_mask.nii.gz"
    assert regression_mask.exists()


def test_synthpreproc():
    synthpreproc_parser()


def test_synthtarget(monkeypatch, tmp_path, plumb_oblique_data):
    test = plumb_oblique_data[0]
    test_output = tmp_path / "test_output"
    test_output_affine = str(test_output) + ".affine"
    test_output_rimg = str(test_output) + "_rimg.nii.gz"
    test_output_simg = str(test_output) + "_simg.nii.gz"
    test_output_stimg = str(test_output) + "_stimg.nii.gz"
    monkeypatch.setattr(
        "sys.argv",
        [
            "omni_synthtarget",
            str(test),
            "none(0)",
            str(test),
            "-p",
            "0",
            "-o",
            str(test_output),
            "-r",
            test_output_rimg,
            "-b",
            test_output_simg,
            "-f",
            test_output_stimg,
            "-c",
        ],
    )
    synthtarget()
    affine_mat, atype = read_affine_file(test_output_affine)

    # check if affine is identity
    assert np.all(np.isclose(np.eye(4), affine_mat))
    assert atype == "omni"

    # check if images are correct dimensions
    test_img = nib.load(test)
    rimg = nib.load(test_output_rimg)
    simg = nib.load(test_output_simg)
    stimg = nib.load(test_output_stimg)
    assert rimg.shape == test_img.shape
    assert simg.shape == test_img.shape
    assert stimg.shape == test_img.shape


def test_synthunwarp():
    synthunwarp_parser()
