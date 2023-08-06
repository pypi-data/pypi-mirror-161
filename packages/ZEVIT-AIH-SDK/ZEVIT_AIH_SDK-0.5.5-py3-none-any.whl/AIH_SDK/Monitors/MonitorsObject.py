from AIH_SDK.v2Object import v2Object


class MonitorsObject(v2Object):

    def __init__(self):
        super().__init__()
        self._api = 'monitors'
        self._version = '1.0'

    