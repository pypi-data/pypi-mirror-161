from omni.scripts.common.help import CustomTextHelpFormatter


def test_CustomTextHelpFormatter():
    test_description = "This is a test.\n\nThis is another test."
    formatter = CustomTextHelpFormatter("test")

    assert test_description.replace("\n\n", "\n\n\n\n").split("\n\n") + [""] == formatter._split_lines(
        "\n" + test_description, width=130
    )  # pylint: disable=protected-access

    # simulate an action object
    class Action:
        def __init__(self, default):
            self.help = "This is a test."
            self.default = default
            self.option_strings = True

    assert formatter._get_help_string(Action(None)) == "This is a test."  # pylint: disable=protected-access
    assert (
        formatter._get_help_string(Action(1)) % {"default": 1}
        == "This is a test. (default: 1)"  # pylint: disable=protected-access
    )
