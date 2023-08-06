from AIH_SDK.v1Object import v1Object


class PanoramicTour(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/panoramic-tours'
    
    
    
    def get(self, id:str=None):
        """
        To get a list of all panorama tours or a specific panorama tour.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['panoramicTour']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['panoramicTours']
        
        return self

    
    
    def post(self):
        """
        To put the updates that have been made.
        """
        
        response_json = self._client._post(self._api, self._endpoint, self.value)
        self.value['id'] = response_json['panoramicTour']['id']
        
        return self
    
    
