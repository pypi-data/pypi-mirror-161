from AIH_SDK.Risks.RisksObject import RisksObject


class Mitigation(RisksObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Mitigations'
    

    def get(self, riskId:str):
        # super().get(parameters={'riskId': riskId})
        return super().get(parameters=[('riskId', riskId)])