from AIH_SDK.DataProcessing.DataProcessingObject import DataProcessingObject


class Job(DataProcessingObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Jobs'