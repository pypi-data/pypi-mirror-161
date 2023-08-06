from omni.pipelines.epi import stages


def test_AlignAffineEpiToAnatStage():
    stages.AlignAffineEpiToAnatStage()


def test_DistortionCorrectionStage():
    stages.DistortionCorrectionStage()


def test_CombineTransformsStage():
    stages.CombineTransformsStage()
