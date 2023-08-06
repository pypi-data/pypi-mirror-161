from AIH_SDK.Signals.SignalsObject import SignalsObject
from AIH_SDK.AIHExceptions import AIHClientException


class Signal(SignalsObject):

    def __init__(self):
        super().__init__()
        self._endpoint = 'signals'

    
    def post(self):
        if isinstance((self.value), dict):
            self._client._post(self._api, self._endpoint, self.value)
        
        elif isinstance((self.value), list):
            try:
                self._client._post(self._api, f'{self._endpoint}/bulk', self.value)
            except AIHClientException as e:
                if 'Cannot interpret response as JSON' in e.message:
                    pass
                else:
                    raise e