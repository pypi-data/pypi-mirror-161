import warnings
from memori import Stage
from .align import align_affine_epi_to_anat, combine_transforms, distortion_correction


warnings.warn("Subclassed Stages are deprecated. Explictly use Stage instead.", DeprecationWarning, stacklevel=2)


class AlignAffineEpiToAnatStage(Stage):
    """Align affine epi to anat stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="epi_proc_0_align_affine_epi_to_anat", **kwargs):
        super().__init__(
            align_affine_epi_to_anat,
            stage_outputs=["final_epi_to_anat_affine", "final_anat_to_epi_affine"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class DistortionCorrectionStage(Stage):
    """Distortion correction stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="epi_proc_1_distortion_correction", **kwargs):
        super().__init__(
            distortion_correction,
            stage_outputs=["final_synth_to_epi_warp", "final_epi_to_synth_warp"],
            hash_output=path,
            output_path=path,
            **kwargs,
        )


class CombineTransformsStage(Stage):
    """Combine transforms stage.

    Methods
    -------
    __init__:
    """

    def __init__(self, path="epi_proc_2_combine_transforms", **kwargs):
        super().__init__(
            combine_transforms, stage_outputs=["raw_epi_atlas"], hash_output=path, output_path=path, **kwargs
        )
