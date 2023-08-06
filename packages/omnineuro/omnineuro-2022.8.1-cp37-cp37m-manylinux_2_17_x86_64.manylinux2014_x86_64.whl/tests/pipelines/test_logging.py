import logging
from omni.pipelines.logging import setup_logging


def test_setup_logging(capsys, tmp_path):
    log_file = tmp_path / "file.log"
    setup_logging(str(log_file))
    logging.info("test test test")
    assert log_file.exists()
