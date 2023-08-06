from AIH_SDK.v1Object import v1Object


class ApplierLanguage(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/applier-languages'
    
    
    
    def get(self, id:str=None):
        """
        To get a list of all Applier languages or a specific applier language.
        Result is set as self.value
        """

        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['applierLanguage']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['applierLanguages']

        return self
            
    
    def post(self):
        """
        To post the updates that have been made.
        """
        
        response_json = self._client._post('aih', 'api/v1/applier-languages/', self.value)
        self.value['id'] = response_json['applierLanguage']['id']
        
        return self