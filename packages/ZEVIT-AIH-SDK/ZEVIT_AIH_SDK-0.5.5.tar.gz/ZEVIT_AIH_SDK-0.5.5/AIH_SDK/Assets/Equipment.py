from AIH_SDK.Assets.AssetsObject import AssetsObject


class Equipment(AssetsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'equipment'

        
