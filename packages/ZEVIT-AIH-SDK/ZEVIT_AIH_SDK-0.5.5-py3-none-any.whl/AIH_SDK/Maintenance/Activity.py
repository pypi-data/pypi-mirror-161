from AIH_SDK.Maintenance.MaintenanceObject import MaintenanceObject


class Activity(MaintenanceObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Activities'
    
    def get_inputs(self, parameters:dict={}):
        """
        get_inputs gets the inputs for the activity.

        OUT: if self.value is a dict it returns a input object with the inputs of the activity.
                if self.value is a list it will return a list of inputs objects.
        """
        if isinstance(self.value, dict):
            inputs = Input(self.get_value('id')).get(parameters=parameters)

        elif isinstance(self.value, list):
            inputs = [
                Input(design_id).get(parameters=parameters)
                for design_id
                in self.get_value('id') 
            ]

        return inputs
    
class Input(MaintenanceObject):
    
    def __init__(self, activities_id:str):
        super().__init__()
        self.activities_id = activities_id
        self._endpoint = f'activities/{activities_id}/inputs'