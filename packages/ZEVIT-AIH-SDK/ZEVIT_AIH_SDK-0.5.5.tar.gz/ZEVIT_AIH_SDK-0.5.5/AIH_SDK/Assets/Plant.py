from AIH_SDK.Assets.AssetsObject import AssetsObject


class Plant(AssetsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'plants'
    
    
