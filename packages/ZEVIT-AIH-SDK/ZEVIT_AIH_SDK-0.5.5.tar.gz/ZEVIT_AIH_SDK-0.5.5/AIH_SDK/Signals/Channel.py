from AIH_SDK.Signals.SignalsObject import SignalsObject
from AIH_SDK.Signals.Signal import Signal

class Channel(SignalsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Channels'


    def get_signals(self, from_millis):
        channel_numbers = self.get_value('channelNumber')
        
        if isinstance(self.value, dict):
            parameters = [('ChannelNumbers', self.get_value('channelNumber'))]

        elif isinstance(self.value, list):
            parameters = [('ChannelNumbers', cha_no) for cha_no in self.get_value('channelNumber')]

        parameters.append(('TimestampFrom', from_millis))
        signals = Signal().get(parameters=parameters)

        return signals


    def post(self):
        if type(self.value) == list:
            for i, val in enumerate(self.value):
                response = self._client._post(self._api, self._endpoint, val)
                self.value[i] = response
                
        elif type(self.value) == dict:
            response = self._client._post(self._api, self._endpoint, self.value)
            self.value = response

        return self