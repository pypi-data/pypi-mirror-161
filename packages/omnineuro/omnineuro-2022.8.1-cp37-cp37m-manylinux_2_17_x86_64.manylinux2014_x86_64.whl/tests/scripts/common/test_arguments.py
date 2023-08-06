from argparse import ArgumentParser
import pytest
from omni.scripts.common.arguments import *


def test_Arguments(monkeypatch):
    monkeypatch.setattr("sys.argv", ["test_script", "--test_flag", "test_arg"])
    parser = ArgumentParser()
    arg_test_flag = Argument.create("test_flag", "test description")
    arg_test_flag(parser, "-t", required=True)
    args = parser.parse_args()
    assert args.test_flag == "test_arg"
    monkeypatch.setattr("sys.argv", ["test_script"])
    with pytest.raises(SystemExit):
        parser.parse_args()
