import json
from collections import defaultdict

import numpy as np
import pandas as pd

from AIH_SDK.AIHClient import AIHClient
from AIH_SDK.Object import Object


class v1Object(Object):
    
    def __init__(self):
        super().__init__()
        self._api = 'aih'
    
     
    def get_keys(self):
        """
        get_keys is used to get the keys for the value.
        OUT: (list) - list of strings of the keys. Each key is a string seperated by '__' for each indent.
        """
        
        # If the value is a dictionary
        if type(self.value) == dict:
            return self._get_keys(self.value)
        
        # If the value is a list
        elif type(self.value) == list:
            result = []
            for val in self.value[-100:]:
                result .extend(self._get_keys(val))
            return list(set(result))
