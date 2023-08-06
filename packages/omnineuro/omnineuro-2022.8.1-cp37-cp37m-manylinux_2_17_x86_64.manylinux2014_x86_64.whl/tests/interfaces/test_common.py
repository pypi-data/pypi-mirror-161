import unittest
import os
import tempfile
import subprocess
import numpy as np
import nibabel as nib
from omni.interfaces import common
from omni.io import write_affine_file
from .. import afni_exists, TESTDATA


class TestInterfacesCommon(unittest.TestCase):
    def test_run_process(self):
        # test mode (should not throw exception)
        common.TEST_MODE = True
        self.assertEqual(
            "cat a_non-existent_file 2> /dev/null", common.run_process("cat a_non-existent_file 2> /dev/null")
        )

        # test run_process exception throw
        common.TEST_MODE = False
        with self.assertRaises(subprocess.CalledProcessError):
            common.run_process("cat a_non-existent_file 2> /dev/null")

    @afni_exists
    def test_create_fov_masks(self):
        test_ref = os.path.join(TESTDATA, "imgs", "test_plumb.nii.gz")
        test_source = os.path.join(TESTDATA, "imgs", "test_plumb.nii.gz")
        test_affine = np.eye(4)

        # with auto mask naming
        with tempfile.NamedTemporaryFile(suffix=".aff12.1D") as test_affine_file:
            write_affine_file(test_affine_file.name, test_affine, "afni")
            ref_mask, source_mask = common.create_fov_masks(test_ref, test_source, test_affine_file.name)
            ref_mask_data = nib.load(ref_mask).get_fdata()
            source_mask_data = nib.load(source_mask).get_fdata()
            self.assertTrue(np.isclose(ref_mask_data, source_mask_data).all())

        # test when mask names specified
        with tempfile.NamedTemporaryFile(suffix=".aff12.1D") as test_affine_file:
            with tempfile.NamedTemporaryFile(suffix=".nii.gz") as ref_mask:
                with tempfile.NamedTemporaryFile(suffix=".nii.gz") as source_mask:
                    write_affine_file(test_affine_file.name, test_affine, "afni")
                    ref_mask, source_mask = common.create_fov_masks(
                        test_ref, test_source, test_affine_file.name, ref_mask.name, source_mask.name
                    )
                    ref_mask_data = nib.load(ref_mask).get_fdata()
                    source_mask_data = nib.load(source_mask).get_fdata()
                    self.assertTrue(np.isclose(ref_mask_data, source_mask_data).all())

    def test_get_prefix(self):
        test_path = "/test0/test1/test2.nii.gz"
        self.assertEqual(common.get_prefix(test_path), "test2")

    def test_get_path_and_prefix(self):
        test_path = "/test0/test1/test2.nii.gz"
        self.assertEqual(common.get_path_and_prefix(test_path), "/test0/test1/test2")

    def test_append_suffix(self):
        self.assertEqual("/test0/test1/test2_test3.nii.gz", common.append_suffix("/test0/test1/test2.nii.gz", "_test3"))

    def test_replace_suffix(self):
        self.assertEqual("/test0/test1_test3", common.replace_suffix("/test0/test1_test2", "_test3"))

    def test_repath(self):
        self.assertEqual("/test4/test5/test2", common.repath("/test4/test5", "/test0/test1/test2"))

    def test_normalize(self):
        self.assertTrue(
            np.all(common.normalize(np.array([0.0, 1.0, 2.0, 3.0, 4.0])) == np.array([0, 0.25, 0.5, 0.75, 1.0]))
        )
