from AIH_SDK.Signals.SignalsObject import SignalsObject

class ChannelAvailability(SignalsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'ChannelAvailabilities'