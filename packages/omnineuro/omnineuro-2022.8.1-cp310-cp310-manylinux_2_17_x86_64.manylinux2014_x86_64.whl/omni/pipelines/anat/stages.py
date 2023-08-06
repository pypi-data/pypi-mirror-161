import warnings
from memori import Stage
from .align import align_atlas, align_anat, deoblique_anat
from .normalize import debias
from .segmentation import brain_extraction
from .masks import weight_mask_and_autobox


warnings.warn("Subclassed Stages are deprecated. Explictly use Stage instead.", DeprecationWarning, stacklevel=2)


class DeobliqueAnatStage(Stage):
    """Deoblique anat stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path: str = "anat_proc_0_deoblique_anat", **kwargs):
        super().__init__(deoblique_anat, stage_outputs=["t1_do", "t2_do"], hash_output=path, output_path=path, **kwargs)


class DebiasStage(Stage):
    """Debias stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path: str = "anat_proc_1_debias", **kwargs):
        super().__init__(debias, stage_outputs=["t1_debias", "t2_debias"], hash_output=path, output_path=path, **kwargs)


class AlignAnatStage(Stage):
    """Align anat stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path: str = "anat_proc_2_align_anat", **kwargs):
        super().__init__(
            align_anat,
            stage_outputs=["t1_debias", "t2_debias", "anat_align_affine"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class BrainExtractionStage(Stage):
    """Brain extraction stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path: str = "anat_proc_3_brain_extraction", **kwargs):
        super().__init__(
            brain_extraction,
            stage_outputs=["anat_bet_mask", "anat_eye_mask", "t1_debias_bet", "t2_debias_bet"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class AlignAtlasStage(Stage):
    """Align atlas stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path: str = "anat_proc_4_align_atlas", **kwargs):
        super().__init__(
            align_atlas,
            stage_outputs=["t1_atlas", "t2_atlas", "atlas_align_affine"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class WeightMaskAndAutoboxStage(Stage):
    """Weight mask and autobox stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path: str = "anat_proc_5_weight_mask_and_autobox", **kwargs):
        super().__init__(
            weight_mask_and_autobox,
            stage_outputs=[
                "weight_mask",
                "weight_mask_ab",
                "anat_bet_mask_ab",
                "t1_debias_ab",
                "t2_debias_ab",
                "t1_debias_ab_sat_lce",
                "t2_debias_ab_sat_lce",
                "t1_debias_ab_sat_lce_bet",
                "t2_debias_ab_sat_lce_bet",
            ],
            hash_output=path,
            output_path=path,
            **kwargs,
        )
