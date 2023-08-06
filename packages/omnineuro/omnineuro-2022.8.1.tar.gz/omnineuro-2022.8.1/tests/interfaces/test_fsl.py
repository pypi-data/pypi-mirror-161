import os
import unittest
import tempfile
from omni.interfaces import common, fsl
from .. import fsl_exists, TESTDATA


class TestInterfacesFsl(unittest.TestCase):
    def test_flirt(self):
        common.TEST_MODE = True
        self.assertEqual(
            fsl.flirt("test0", "test1", "test2"),
            "flirt -out test0 -ref test1 -in test2 -dof 12 " "-cost corratio -interp sinc -v",
        )
        common.TEST_MODE = False

    @fsl_exists
    def test_bet(self):
        common.TEST_MODE = True
        self.assertListEqual(
            fsl.bet("test0.nii.gz", "test1.nii.gz", mask=True),
            ["bet test1.nii.gz test0.nii.gz -f 0.5 -m -v", "test0_mask.nii.gz"],
        )
        with self.assertRaises(ValueError):
            fsl.bet("test0", "test1", eye=True, neck=True)
        common.TEST_MODE = False
        # run actual bet test with eye mask
        with tempfile.TemporaryDirectory() as d:
            test_output = os.path.join(d, "test.nii.gz")
            test_file = os.path.join(TESTDATA, "imgs", "test_plumb.nii.gz")
            fsl.bet(test_output, test_file, 0.5, eye=True)
            assert os.path.exists(test_output)
