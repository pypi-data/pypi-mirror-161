from omni.pipelines.func import stages


def test_DeobliqueFuncStage():
    stages.DeobliqueFuncStage()


def test_CreateReferenceAndMocoStage():
    stages.CreateReferenceAndMocoStage()


def test_DebiasStage():
    stages.DebiasStage()


def test_BrainExtractionStage():
    stages.BrainExtractionStage()


def test_AutoboxAndNormalizeStage():
    stages.AutoboxAndNormalizeStage()
