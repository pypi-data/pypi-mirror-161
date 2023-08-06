from AIH_SDK.Maintenance.MaintenanceObject import MaintenanceObject


class Deviation(MaintenanceObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Deviations'