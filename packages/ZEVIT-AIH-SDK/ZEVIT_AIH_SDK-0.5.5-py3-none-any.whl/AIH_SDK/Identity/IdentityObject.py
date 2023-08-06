from AIH_SDK.v2Object import v2Object


class IdentityObject(v2Object):
    
    def __init__(self):
        super().__init__()
        self._api = 'idsvr'
        self._version = '1.0'

