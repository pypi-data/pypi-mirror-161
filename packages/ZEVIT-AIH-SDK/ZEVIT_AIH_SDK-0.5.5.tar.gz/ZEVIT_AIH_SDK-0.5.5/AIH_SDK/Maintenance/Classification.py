from AIH_SDK.Maintenance.MaintenanceObject import MaintenanceObject
from AIH_SDK import AIHExceptions as AIHE


class Classification(MaintenanceObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Classifications'
    
    def get_elements(self, classification_id=None):
        if not classification_id:
            if type(self.value) == dict:
                classification_id = self.get_value('id')
            else:
                raise AIHE.AIHException(f'This method is not supported for self.value of type {type(self.value)}')

        return ClassificationElement(classification_id).get()


class ClassificationElement(MaintenanceObject):

    _classification_id = None

    def __init__(self, classification_id):
        self._classification_id = classification_id
        super().__init__()
        self._endpoint = f'Classifications/{self._classification_id}/Elements'