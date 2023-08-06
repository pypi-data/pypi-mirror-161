from AIH_SDK.DataProcessing.DataProcessingObject import DataProcessingObject

class JobDefinition(DataProcessingObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'JobDefinitions'