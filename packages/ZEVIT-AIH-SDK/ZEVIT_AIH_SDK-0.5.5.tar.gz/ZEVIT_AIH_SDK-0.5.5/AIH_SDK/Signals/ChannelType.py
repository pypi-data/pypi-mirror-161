from AIH_SDK.Signals.SignalsObject import SignalsObject

class ChannelType(SignalsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'ChannelTypes'