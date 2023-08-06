import warnings
from memori import Stage
from .align import deoblique_func, create_reference_and_moco
from .normalize import debias
from .segmentation import brain_extraction
from .masks import autobox_and_normalize


warnings.warn("Subclassed Stages are deprecated. Explictly use Stage instead.", DeprecationWarning, stacklevel=2)


class DeobliqueFuncStage(Stage):
    """Deoblique func stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="func_proc_0_deoblique_func", **kwargs):
        super().__init__(
            deoblique_func,
            stage_outputs=[
                "func_do",
            ],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class CreateReferenceAndMocoStage(Stage):
    """Create reference and moco stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="func_proc_1_create_reference_and_moco", **kwargs):
        super().__init__(
            create_reference_and_moco,
            stage_outputs=["func_do_moco", "ref_func", "rigid_body_params"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class DebiasStage(Stage):
    """Debias stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="func_proc_2_debias", **kwargs):
        super().__init__(debias, stage_outputs=["ref_func_debias"], hash_output=path, output_path=path, **kwargs)


class BrainExtractionStage(Stage):
    """Brain extraction stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="func_proc_3_brain_extraction", **kwargs):
        super().__init__(
            brain_extraction,
            stage_outputs=["ref_func_debias_mask", "ref_func_debias_bet"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class AutoboxAndNormalizeStage(Stage):
    """Autobox and normalize stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="func_proc_4_autobox_and_normalize", **kwargs):
        super().__init__(
            autobox_and_normalize,
            stage_outputs=[
                "ref_func_debias_ab",
                "ref_func_debias_bet_ab",
                "ref_func_debias_mask_ab",
                "func_do_moco_ab",
                "func_do_ab",
            ],
            hash_output=path,
            output_path=path,
            **kwargs,
        )
