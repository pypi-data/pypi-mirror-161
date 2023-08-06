from AIH_SDK.DataUpload.DataUploadObject import DataUploadObject


class DataType(DataUploadObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'DataTypes'
