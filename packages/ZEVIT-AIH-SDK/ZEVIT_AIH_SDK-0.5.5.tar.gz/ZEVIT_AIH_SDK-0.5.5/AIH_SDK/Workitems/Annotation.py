import AIH_SDK.AIHExceptions as AIHE
from AIH_SDK.v1Object import v1Object


class Annotation(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/annotations'
        
    
    def get(self, id:str=None):
        """
        To get a list of all annotations or a specific annotations.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            try:
                self.value = self.value['annotation']
            except:
                raise AIHE.AIHException(f'Annotation does not exist with id: {id}')
                
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['annotations']
        
        return self
        
    def post(self):
        """
        To post the updates that have been made to self.value
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['annotation']['id']
        
        return self
    
