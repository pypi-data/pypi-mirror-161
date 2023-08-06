import unittest
from omni.interfaces import common, ants


class TestInterfacesAnts(unittest.TestCase):
    def test_antsRegistration(self):
        common.TEST_MODE = True
        self.assertEqual(
            ants.antsRegistration("test0", "test1", "test2"),
            "antsRegistration -d 3 -u 1 -o [test0] -n BSpline[5] "
            "-w [0.005,0.995] --transform Syn[1,0,0] "
            "--metric CC[test1,test2,1,10] -c [500x200x200x0,1e-06,15] "
            "-s 2x1x0x0 -f 4x3x2x1 -g 1x1x1 -v 1",
        )
        common.TEST_MODE = False

    def test_antsApplyTransform(self):
        common.TEST_MODE = True
        self.assertEqual(
            ants.antsApplyTransform("test0", "test1", "test2", "test3 test4"),
            "antsApplyTransforms -d 3 -o test0 -r test1 -i test2 " "-n BSpline[5] -t test3 test4 -v 1",
        )
        self.assertEqual(
            ants.antsApplyTransform("test0", "test1", "test2", ["test3", "test4"]),
            "antsApplyTransforms -d 3 -o test0 -r test1 -i test2 " "-n BSpline[5] -t test3 test4 -v 1",
        )
        common.TEST_MODE = False

    def test_N4BiasFieldCorrection(self):
        common.TEST_MODE = True
        self.assertEqual(
            ants.N4BiasFieldCorrection("test0", "test1"), "N4BiasFieldCorrection -d 3 -i test1 -o test0 -v 1"
        )
        self.assertEqual(
            ants.N4BiasFieldCorrection("test0", "test1", "[100,3,1x1x1,3]"),
            "N4BiasFieldCorrection -d 3 -i test1 " "-o test0 -b [100,3,1x1x1,3] -v 1",
        )
        common.TEST_MODE = False
