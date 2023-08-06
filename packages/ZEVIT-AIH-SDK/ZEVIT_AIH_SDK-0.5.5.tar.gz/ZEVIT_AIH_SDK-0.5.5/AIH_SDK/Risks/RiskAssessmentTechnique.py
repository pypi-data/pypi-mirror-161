from AIH_SDK.Risks.RisksObject import RisksObject


class RiskAssessmentTechnique(RisksObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'RiskAssessmentTechniques'