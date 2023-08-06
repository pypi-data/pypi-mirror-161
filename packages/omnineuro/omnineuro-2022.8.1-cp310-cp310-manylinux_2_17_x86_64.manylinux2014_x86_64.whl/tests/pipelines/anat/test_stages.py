from omni.pipelines.anat import stages


def test_DeobliqueAnatStage():
    stages.DeobliqueAnatStage()


def test_DebiasStage():
    stages.DebiasStage()


def test_AlignAnatStage():
    stages.AlignAnatStage()


def test_BrainExtractionStage():
    stages.BrainExtractionStage()


def test_AlignAtlasStage():
    stages.AlignAtlasStage()


def test_WeightMaskAndAutoboxStage():
    stages.WeightMaskAndAutoboxStage()
