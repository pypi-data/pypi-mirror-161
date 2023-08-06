from AIH_SDK.v2Object import v2Object


class DataProcessingObject(v2Object):

    def __init__(self):
        super().__init__()
        self._api = 'dp'
        self._version = '1.2'

    