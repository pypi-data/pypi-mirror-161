from AIH_SDK.v1Object import v1Object


class WorkorderItem(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/work-order-items'
        
    
    def get(self, id:str=None, ids:list=[]):
        """
        To get a list of all workorderitems or a specific workorderitem.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/filter/ids/{id}')
            self.value = self.value['workOrderItems'][0]
        elif ids:
            self.value = self._client._get(self._api, f'{self._endpoint}/filter/ids/{ids}')
            self.value = self.value['workOrderItems']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['workOrderItems']
        
        return self
        
    def post(self):
        """
        To post the updates that have been made to self.value
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['workOrderItems']['id']
        
        return self
            
