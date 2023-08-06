from AIH_SDK.Risks.RisksObject import RisksObject


class Risk(RisksObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Risks'