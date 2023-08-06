from AIH_SDK.Risks.RisksObject import RisksObject


class RiskAssessmentResult(RisksObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'RiskAssessmentResults'