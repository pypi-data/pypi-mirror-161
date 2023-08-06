from AIH_SDK.Monitors.MonitorsObject import MonitorsObject


class Model(MonitorsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Models'