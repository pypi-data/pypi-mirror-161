from AIH_SDK.Maintenance.MaintenanceObject import MaintenanceObject


class WorkItem(MaintenanceObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'WorkItems'
    
    def get_activities(self, parameters:dict={}):
        """
        get_activities gets the workItemActivity for the workItem.

        OUT: if self.value is a dict it returns a input object with the workItemActivity of the workItem.
                if self.value is a list it will return a list of workItemActivity objects.
        """
        if isinstance(self.value, dict):
            workItemActivity = WorkItemActivity(self.get_value('id')).get(parameters=parameters)

        elif isinstance(self.value, list):
            workItemActivity = [
                WorkItemActivity(design_id).get(parameters=parameters)
                for design_id
                in self.get_value('id')
            ]

        return workItemActivity

class WorkItemActivity(MaintenanceObject):

    def __init__(self, workItem_id:str):
        super().__init__()
        self.workItem_id = workItem_id
        self._endpoint = f'workItems/{workItem_id}/activities'