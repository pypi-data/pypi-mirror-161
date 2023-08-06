from AIH_SDK.v2Object import v2Object


class MaintenanceObject(v2Object):

    def __init__(self):
        super().__init__()
        self._api = 'quality'
        self._version = '1.0'

    