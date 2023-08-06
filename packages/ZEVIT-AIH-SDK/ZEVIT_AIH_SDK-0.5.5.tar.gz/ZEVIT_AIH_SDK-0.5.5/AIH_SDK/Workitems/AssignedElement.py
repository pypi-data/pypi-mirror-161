from AIH_SDK.v1Object import v1Object


class AssignedElement(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/assigned-elements'
    
    
    def get(self, id:str=None):
        """
        To get a list of all designation templates or a specific designation template.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['assignedElement']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            
            self.value = self.value['assignedElements']
        
        return self
            
       
    def post(self):
        """
        To post the updates that have been made.
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['assignedElementId']
        
        return self
    

class AssignedElementTemplate(v1Object):
    
    def __init__(self):
        super().__init__()
        #self._api = 'aih'
        self._api = 'assetdatahub'
        self._endpoint = 'api/v1/assigned-element-template'
    
    
    def get(self, id:str=None):
        """
        To get a list of all designation templates or a specific designation template.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['template']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['templates']
        
        return self
            
        
    def post(self):
        """
        To post the updates that have been made.
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['assignedElementTemplateId']
        
        return self
    