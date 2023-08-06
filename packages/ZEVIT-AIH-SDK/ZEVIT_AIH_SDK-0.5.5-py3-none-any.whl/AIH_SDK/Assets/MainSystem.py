from AIH_SDK.Assets.AssetsObject import AssetsObject
from AIH_SDK.AIHExceptions import AIHException


class MainSystem(AssetsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'mainsystems'
    
    
    def get_design_objects(self):
        """
        get_design_objects gets the design objects related to the given mainsystem.

        OUT: returns a list of json objects representing the objects of the design.
        """
        if isinstance(self.value, dict):
            return self._client._get(self._api, f'{self._endpoint}/{self.get_value("id")}/DesignObjects')
        
        elif isinstance(self.value, list):
            raise AIHException("This functionality is only supported for a single mainsystem")

        return objects
