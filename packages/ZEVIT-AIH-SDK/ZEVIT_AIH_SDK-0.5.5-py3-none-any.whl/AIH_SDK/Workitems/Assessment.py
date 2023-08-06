from AIH_SDK.v1Object import v1Object


class Assessment(v1Object):
    
    def __init__(self):
        super().__init__()
        self._api = 'aih'
        self._endpoint = 'api/v1/assessments'
        
        
    
    def get(self, id:str=None, ids:list=[], workorderitem:str=None):
        """
        To get a list of all assessments or a specific assessment.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['assessment']
        elif ids:
            ids = ','.join(ids)
            self.value = self._client._get(self._api, f'{self._endpoint}/filter/ids/{ids}')
            self.value = self.value['assessments']
        elif workorderitem:
            self.value = self._client._get(self._api, f'{self._endpoint}/inspection/{workorderitem}')
            self.value = self.value['assessments']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['assessment']
            
        return self
    
    
    def post(self):
        """
        To post the updates that have been made to self.value
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['id']
        
        return self



class AssessmentTemplate(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/assessment-templates'
        
        
    
    def get(self, id:str=None):
        """
        To get a list of all assessment-templates or a specific assessment-template.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['assessmentTemplate']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['assessmentTemplates']
            
        return self
    
    
    def post(self):
        """
        To post the updates that have been made to self.value
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['id']
        
        return self