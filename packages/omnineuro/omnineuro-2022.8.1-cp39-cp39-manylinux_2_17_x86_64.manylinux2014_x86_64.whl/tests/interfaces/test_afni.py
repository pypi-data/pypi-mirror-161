import unittest
from omni.interfaces import common, afni


class TestInterfacesAnts(unittest.TestCase):
    def test_NwarpCat(self):
        common.TEST_MODE = True
        self.assertEqual(afni.NwarpCat("test0", "test1"), "3dNwarpCat -prefix test0 -warp1 test1 -verb -overwrite")
        self.assertEqual(
            afni.NwarpCat("test0", "test1", True), "3dNwarpCat -prefix test0 -warp1 test1 -iwarp -verb -overwrite"
        )
        with self.assertRaises(AssertionError):
            afni.NwarpCat("test0", ["test1", "test2"])
        self.assertEqual(
            afni.NwarpCat("test0", ["test1", "test2"], [False, False]),
            "3dNwarpCat -prefix test0 -warp1 test1 " "-warp2 test2 -verb -overwrite",
        )
        self.assertEqual(
            afni.NwarpCat("test0", ["test1", "test2"], [True, True]),
            "3dNwarpCat -prefix test0 -warp1 test1 -iwarp " "-warp2 test2 -iwarp -verb -overwrite",
        )
        common.TEST_MODE = False

    def test_NwarpApply(self):
        common.TEST_MODE = True
        self.assertEqual(
            afni.NwarpApply("test0", "test1", "test2", "test3"),
            "3dNwarpApply -nwarp test3 -prefix test0 -master " "test1 -source test2 -overwrite",
        )
        self.assertEqual(
            afni.NwarpApply("test0", "test1", "test2", ["test3", "test4"]),
            "3dNwarpApply -nwarp test3 test4 -prefix test0 " "-master test1 -source test2 -overwrite",
        )
        common.TEST_MODE = False

    def test_Allineate(self):
        common.TEST_MODE = True
        self.assertEqual(
            afni.Allineate("test0", "test1", "test2"),
            "3dAllineate -prefix test0 -base test1 -input " "test2 -final wsinc5 -overwrite",
        )
        common.TEST_MODE = False

    def test_Autobox(self):
        common.TEST_MODE = True
        self.assertEqual(afni.Autobox("test0", "test1"), "3dAutobox -prefix test0 -input test1 -overwrite")
        common.TEST_MODE = False

    def test_cat_matvec(self):
        common.TEST_MODE = True
        self.assertEqual(afni.cat_matvec("test0", "test1 test2"), "cat_matvec test1 test2 > test0")
        common.TEST_MODE = False

    def test_resample(self):
        common.TEST_MODE = True
        self.assertEqual(
            afni.resample("test0", "test1", "test2"),
            "3dresample -prefix test0 -master test1 " "-input test2 -rmode Cu -overwrite",
        )
        common.TEST_MODE = False
