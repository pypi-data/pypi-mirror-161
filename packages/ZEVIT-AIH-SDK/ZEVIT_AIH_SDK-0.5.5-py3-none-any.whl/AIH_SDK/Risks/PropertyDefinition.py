from AIH_SDK.Risks.RisksObject import RisksObject


class PropertyDefinition(RisksObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'PropertyDefinitions'