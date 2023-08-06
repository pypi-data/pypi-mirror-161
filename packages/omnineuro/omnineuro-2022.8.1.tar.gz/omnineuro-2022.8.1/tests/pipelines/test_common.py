import unittest
import os
import tempfile
import json
from omni.pipelines import common


class TestPipelinesCommon(unittest.TestCase):
    def test_stage(self):
        # create a function
        def func(x, y):
            def sum(a, b):
                return a + b

            return sum(x, y)

        # create another function
        def func2(a="test"):
            return a

        # create a third function
        def func3(a, b):
            return [
                [a, b, 1],
            ]

        # wrap function in a stage
        stage0 = common.Stage(func, stage_outputs=["z"])

        # check stage inputs/outputs
        self.assertListEqual(stage0.inputs, ["x", "y"])
        self.assertListEqual(stage0.outputs, ["z"])

        # check args
        self.assertDictEqual(stage0.args, {})

        # run stage
        stage0.run(1, 2)
        self.assertDictEqual(stage0.input_args, {"x": 1, "y": 2})
        self.assertDictEqual(stage0.results, {"z": 3})
        self.assertTrue(stage0.state)

        # test override stage arguments
        stage1 = common.Stage(func, x=2, stage_outputs=["z"])
        stage1.run(1, 2)
        self.assertDictEqual(stage1.results, {"z": 4})
        stage2 = common.Stage(func, x=4, y=5, stage_outputs=["z"])
        stage2.run()
        self.assertDictEqual(stage2.results, {"z": 9})
        self.assertDictEqual(stage2.args, {"x": 4, "y": 5})

        # test stage hashing
        with tempfile.TemporaryDirectory() as d:
            with tempfile.NamedTemporaryFile() as f:
                with tempfile.NamedTemporaryFile() as f2:
                    # initial run
                    stage3 = common.Stage(func, stage_outputs=["z"], hash_output=d)
                    self.assertDictEqual(stage3.run(1, 2), {"z": 3})

                    # run again, this should load results from cache
                    self.assertDictEqual(stage3.run(1, 2), {"z": 3})

                    # should be new results
                    self.assertDictEqual(stage3.run(1, 3), {"z": 4})

                    # should be wrong results, due to force loading info from cache
                    self.assertDictEqual(stage3.run(1, 2, force_skip_stage=True), {"z": 4})

                    # should be correct results
                    self.assertDictEqual(stage3.run(1, 2), {"z": 3})

                    # test file hashing
                    stage4 = common.Stage(func2, stage_outputs=["a"], hash_output=d)
                    self.assertDictEqual(stage4.run(f.name), {"a": f.name})
                    with open(os.path.join(d, "func2.inputs")) as hash_file:
                        input_dict = json.load(hash_file)
                        assert "hash" in input_dict["a"] and "file" in input_dict["a"]
                    with open(os.path.join(d, "func2.outputs")) as hash_file:
                        output_dict = json.load(hash_file)
                        assert "hash" in output_dict["a"] and "file" in output_dict["a"]

                    # rerun stage4 with outputs from hash
                    self.assertDictEqual(stage4.run(f.name), {"a": f.name})

                    # test force running and writing
                    self.assertDictEqual(stage3.run(1, 3, force_run_stage=True, force_hash_write=True), {"z": 4})

                    # test list hashing
                    stage5 = common.Stage(func3, stage_outputs=["a"], hash_output=d)
                    results = stage5.run(f.name, f2.name)
                    self.assertDictEqual(results, {"a": [f.name, f2.name, 1]})
                    with open(os.path.join(d, "func3.inputs")) as hash_file:
                        input_dict = json.load(hash_file)
                        assert "hash" in input_dict["a"] and "file" in input_dict["a"]
                        assert "hash" in input_dict["b"] and "file" in input_dict["b"]
                    with open(os.path.join(d, "func3.outputs")) as hash_file:
                        output_dict = json.load(hash_file)
                        assert "hash" in output_dict["a"][0] and "file" in output_dict["a"][0]
                        assert "hash" in output_dict["a"][1] and "file" in output_dict["a"][1]

    def test_pipeline(self):
        def func0(x, y):
            return x + y

        def func1(z, a):
            return z * a

        def func2(z, b):
            return z * b

        def func3(b, c, d):
            return (b + c + d, b * c * d)

        def func4(b, c, d):
            return (b + c + d, b * c * d)

        def func5(b, c, d=1):
            return 1

        def func6(b, c, d):
            return 1

        def func7(filename="test"):
            return filename

        with tempfile.TemporaryDirectory() as d:
            # define stages
            stage0 = common.Stage(func0, stage_outputs=["z"], hash_output=d)
            stage1 = common.Stage(func1, a=2, stage_outputs=["b"], hash_output=d)
            stage2 = common.Stage(func2, stage_outputs=["c"], hash_output=d)
            stage3 = common.Stage(func3, d=2, stage_outputs=["e", "f"], hash_output=d)

            # create a pipeline
            pipeline0 = common.Pipeline(
                [("start", stage0), (stage0, stage1), ((stage0, stage1), stage2), ((stage1, stage2), stage3)]
            )

            # run the pipeline
            pipeline0.run(1, 2)

            # get results
            self.assertDictEqual(pipeline0.results, {"z": 3, "b": 6, "c": 18, "e": 26, "f": 216})

            # test cached results (all tuples are converted to lists)
            self.assertDictEqual(pipeline0.run(1, 2), {"z": 3, "b": 6, "c": 18, "e": 26, "f": 216})

            # test with new stage
            stage4 = common.Stage(func4, d=1, stage_outputs=["e", "f"], hash_output=d)
            pipeline1 = common.Pipeline(
                [("start", stage0), (stage0, stage1), ((stage0, stage1), stage2), ((stage1, stage2), stage4)]
            )
            self.assertDictEqual(pipeline1.run(1, 2), {"z": 3, "b": 6, "c": 18, "e": 25, "f": 108})

            # test with keyword argument in function
            stage5 = common.Stage(func5, stage_outputs=["e"], hash_output=d)
            pipeline2 = common.Pipeline(
                [("start", stage0), (stage0, stage1), ((stage0, stage1), stage2), ((stage1, stage2), stage5)]
            )
            self.assertDictEqual(
                pipeline2.run(1, 2),
                {
                    "z": 3,
                    "b": 6,
                    "c": 18,
                    "e": 1,
                },
            )

            # test with argument exception
            stage6 = common.Stage(func6, stage_outputs=["e"], hash_output=d)
            pipeline3 = common.Pipeline(
                [("start", stage0), (stage0, stage1), ((stage0, stage1), stage2), ((stage1, stage2), stage6)]
            )
            with self.assertRaises(TypeError):
                pipeline3.run(1, 2)

            # test with file
            with tempfile.NamedTemporaryFile() as f:
                stage7 = common.Stage(func7, stage_outputs=["filename"], hash_output=d)
                pipeline4 = common.Pipeline([("start", stage7)])
                pipeline4.run(filename=f.name)
                assert os.path.isfile(pipeline4.results["filename"])

            # test stage type checking
            with self.assertRaises(ValueError):
                common.Pipeline([("invalid_string", lambda x: x)])

    def test_redefine_result_key(self):
        dictionary = {"hello": 1, "test": 2}
        new_dict = common.redefine_result_key(dictionary, "hello", "testing")
        self.assertDictEqual(new_dict, {"testing": 1, "test": 2})
