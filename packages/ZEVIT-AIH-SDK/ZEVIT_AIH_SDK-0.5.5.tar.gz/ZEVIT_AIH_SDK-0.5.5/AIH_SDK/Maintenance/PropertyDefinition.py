from AIH_SDK.Maintenance.MaintenanceObject import MaintenanceObject


class PropertyDefinition(MaintenanceObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'PropertyDefinitions'