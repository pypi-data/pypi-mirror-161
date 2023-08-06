import os
import argparse
import pytest
from omni.scripts.common import command


def test_set_common(monkeypatch):
    # test number of threads setting
    monkeypatch.setattr("sys.argv", ["test", "-n", "10"])
    parser = argparse.ArgumentParser()
    command.set_common(parser)
    args = parser.parse_args()
    assert int(args.number_of_threads) == 10

    # run the easter egg
    with pytest.raises(SystemExit):
        monkeypatch.setattr("sys.argv", ["test", "--easter"])
        parser = argparse.ArgumentParser()
        command.set_common(parser)


def test_set_env():
    namespace = argparse.Namespace()
    namespace.number_of_threads = 10
    command.set_env(namespace)
    assert int(os.environ["OMP_NUM_THREADS"]) == 10
    assert int(os.environ["OPENBLAS_NUM_THREADS"]) == 10
    assert int(os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"]) == 10
