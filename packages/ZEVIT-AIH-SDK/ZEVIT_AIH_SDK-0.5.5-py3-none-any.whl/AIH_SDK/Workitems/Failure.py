from AIH_SDK.v1Object import v1Object


class Failure(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/failures'
        
    
    def get(self, id:str=None):
        """
        To get a list of all failures or a specific failure.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['failure']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['failures']
        
        return self
        
    def post(self):
        """
        To post the updates that have been made to self.value
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['id']
        
        return self
            
