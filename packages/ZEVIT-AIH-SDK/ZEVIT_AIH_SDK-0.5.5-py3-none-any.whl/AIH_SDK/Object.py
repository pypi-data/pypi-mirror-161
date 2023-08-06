import json
from collections import defaultdict
from copy import deepcopy

import numpy as np
import pandas as pd
from numpyencoder import NumpyEncoder

import AIH_SDK.AIHExceptions as AIHE
from AIH_SDK.AIHClient import AIHClient


class Object:
    
    def __init__(self):
        self.value = dict()
        self._api = ''
        self._endpoint = ''
        self._client = AIHClient.get_instance()
        
    
    def get_value(self, key:str, index:int=None):
        """
        get_value gets the value for the input key. 
        Key gets split at '__' to access nested keys.
        If index is not specified it will return the values for the key for all elements in the list.
        If self.value is a dict, index is ignored and will just return the value for the key.

        IN: key (str)   - The key to use for accessing the desired value. '__' is used to access nested values.
            index (int) - The index to get if self.value is a list.

        OUT: The value for the specified key.
             If self.value is a dict it will return the value.
             If self.value is a list and index is provided it will return the value.
             If self.value is a list and index is not provided it will return a list of the values.   
        """

        keys = key.split('__')

        if isinstance(self.value, dict):
            value = self.value
            for k in keys:
                value = value[k]
        
        elif isinstance(self.value, list):
            value = self.value
            if index:
                value = value[index]
                for k in keys:
                    value = value[k]
        
            else:
                values = []
                for value in self.value:
                    for k in keys:
                        value = value[k]
                    values.append(value)
                value = values
            
        return value


    def set_value(self, key:str, value, index:int=None):
        """
        set_value sets the value for the input key. 
        Key gets split at '__' to access nested keys.
        If index is not specified it will set the values for the key for all elements in the self.value.
        If self.value is a dict, index is ignored and will just set the value for the key.

        IN: key (str)   - The key to use for accessing the desired value. '__' is used to access nested values.
            index (int) - The index to set if self.value is a list.

        OUT: self
        """

        keys = key.split('__')
        
        if type(self.value) == dict:
            _value = self.value
            for k in keys[:-1]:
                _value = _value[k]
            
            _value[keys[-1]] = value
                
        elif type(self.value) == list:
            _value = self.value
            if index is not None:
                _value = _value[index]
                for k in keys[:-1]:
                    _value = _value[k]
                    
                _value[keys[-1]] = value
                
            else:
                for _value in self.value:
                    for k in keys[:-1]:
                        _value = _value[k]
                    
                    _value[keys[-1]] = value
        
        return self


    def put(self):
        """
        To put the updates that have been made to the object.
        """
        
        if type(self.value) == list:
            for val in self.value:
                self._client._put(self._api, self._endpoint, val)
                
        elif type(self.value) == dict:
            self._client._put(self._api, self._endpoint, self.value)

        return self


    def post(self):
        """
        To post a new entry in the db for the object.
        """
        if type(self.value) == list:
            for i, val in enumerate(self.value):
                response = self._client._post(self._api, self._endpoint, val)

                # Sets the id for the posted value
                if 'id' in response:
                    self.value[i]['id'] = response['id']
                elif len(response) == 1:
                    key = response.keys()[0]
                    self.value[i]['id'] = response[key]['id']
                
        elif type(self.value) == dict:
            response = self._client._post(self._api, self._endpoint, self.value)

            # Sets the id for the posted value
            if 'id' in response:
                self.value['id'] = response['id']
            elif len(response) == 1:
                key = response.keys()[0]
                self.value['id'] = response[key]['id']

        return self


    def delete(self, id_to_delete=None):
        """
        To delete object or objects with the id or ids that exists in the self.value
        """
        
        id_to_delete_ = id_to_delete if id_to_delete else self.get_value('id')
        
        if type(id_to_delete_) == list:
            for id_to_delete in id_to_delete_:
                self._client._delete(self._api, self._endpoint, id_to_delete)
        
        elif type(id_to_delete_) == str:
            self._client._delete(self._api, self._endpoint, id_to_delete_)
        
        self.value = None
        

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
            return self._get_keys(self.value[0])         


    def _get_keys(self, value:dict, pre:list=[]):
        """
        _get_keys is used as a helper function to get_keys to get the keys for a dictionary
        OUT: (list) - list of strings of the keys. Each key is a string seperated by '__' for each indent.
        
        """
        
        if type(value) == dict:
            result = []
            
            for key, val in value.items():
                result.extend(self._get_keys(val, pre+[key]))
            
            return result
        
        # If the value is the leaf of the dictionary
        else:
            return ['__'.join(pre)]

        
    def to_dataframe(self, keys:list=None) -> pd.DataFrame:
        """
        to_dataframe is used to get the self.value as an Pandas DataFrame object
        
        IN: keys (list) : a list of keys to extract to the dataframe. By default it extracts everything
        
        OUT: df (DataFrame) : A Pandas DataFrame, where the columns are the keys.
        """
        
        # Set the default value for the keys
        if not keys:
            keys = self.get_keys()
        
        
        # If the self.value is a list, extract a dataframe for each of the objects and combine them
        if type(self.value) == list:
            if  self.value:
                dfs = [self._to_dataframe(val, keys) for val in self.value]
                df = pd.concat(dfs)
            else:
                return pd.DataFrame()
        
        # If it is a regular dict, just extract from that one
        else:
            df = self._to_dataframe(self.value, keys)
        
        
        return df.reset_index(drop=True)
        
    
    def _to_dataframe(self, value:dict, keys:list) -> pd.DataFrame:
        """
        _to_dataframe is used as a helper function for the to_dataframe, to get a dataframe for a dictionary instance
        """
        
        values = []
        for key in keys:
            
            ks = key.split('__')
            val = value
            
            for k in ks:
                
                if type(val) != dict:
                    val = np.nan
                    break
                val = val.get(k, np.nan)
                
            values.append(val)
        
                
        return pd.DataFrame({'a' : values}, keys).T


    def update_values(self, args, split='__'):
        """
        update_values is used to update the values in the object.
        NOTE: Remeber to call .put() to apply the changes to db.
        
        IN: args (dict or list) - A dict of all the keys that should be updated or inserted with their respective values. or a list of those dicts
            split (str) - the string it should split for, for nested keys
        """
        
        if isinstance(self.value, list) and isinstance(args, list):
            for val, args_ in zip(self.value, args):
                for arg, value in args_.items():
                    ks = arg.split(split)
                    temp = val
                    for k in ks[:-1]:
                        temp = temp[k]
                    temp[ks[-1]] = value

        elif isinstance(self.value, dict) and isinstance(args, dict):
            for arg, value in args.items():
                ks = arg.split(split)
                temp = self.value
                for k in ks[:-1]:
                    temp = temp[k]
                temp[ks[-1]] = value

        else:
            raise AIHE.AIHException(f'self.value and args must be both of type list or dict, got {type(self.value)} and {type(args)}')

            
        
        """
        if type(args) == list:            
            self.value = [self._dict_to_nested_dict(arg) for arg in args]
                    
        elif type(args) == dict:
            self.value = self._dict_to_nested_dict(args)
        """
        return self


    def copy(self):
        """
        copy is used to copy the content of the current object, except the id of the object.
        It can both copy self.value of type dict and list.
        NOTE: Remeber to call .post() to apply the changes to db.
        """
        
        # If self.value  is list, delete all ids 
        if type(self.value) == list:
            for val in self.value:
                val.pop('id')

        # If self.value is dict, delete id
        elif type(self.value) == dict:
            self.value.pop('id')

        return self


    def filter(self, args):
        """
        filter filters for the given arguments. This only support equal operations and all of them have to be True.
        
        IN: args(dict) - the keys it should filter for and the values the key should be equal to.
        """
        
        df = self.to_dataframe()
        
        for key, value in args.items():
            df = df[df[key] == value]

        return self.from_dataframe(df)


    def from_list(self, list_in):
        """
        from_list set the value of the object to the provided list.

        IN: list_in (list) - The list that should be set as self.value.
        """
        self.value = list_in

        return self

    
    def from_dict(self, dict_in):
        """
        from_dict set the value of the object to the provided dictionary.

        IN: dict_in (dict) - The dictionary that should be set as self.value.
        """
        self.value = dict_in

        return self


    def from_dataframe(self, df):
        """
        from_dataframe creates the object from a dataframe
        
        IN: df(Pandas.DataFrame) - datafrma it should use to create the object
        """
        
        values = [dict(df.iloc[i].dropna()) for i in range(len(df))]
        
        self.value = [self._dict_to_nested_dict(arg) for arg in values]
        #self.update_values(values)

        return self


    def _dict_to_nested_dict(self, dictionary, split:str='__'):
        """
        _dict_to_nested_dict is taking a dictionay nests it using the split parameter.
        
        IN: dictionary (dict) - The dict it should nest according to the split parameter.
            split (str) - The string is should split the keys for and nest for. 
            
        OUT: dict - the nested dict
        """
        
        def rec_dd():
            return defaultdict(rec_dd)
        
        result = defaultdict(rec_dd)
        
        for key, value in dictionary.items():
            ks = key.split(split)
            temp = result
            for k in ks[:-1]:
                temp = temp[k]
            temp[ks[-1]] = value
            
        return dict(json.loads(json.dumps(result, cls=NumpyEncoder)))
            
    
    def _implode(self, df, col, column_group=None):
        """
        _implode is a helper function for the deeply join functionality.
        But it can also be used as the opposite of explode function for a dataframe.

        IN: df (pd.DataFrame)    - The dataframe that should be imploded
            col (str)            - The name of the columns that should be imploded
            column_group (str)   - The column that it should group by to perform the implosion. Default value is the index of the dataframe.
            
        OUT:  The imploded dataframe (pd.DataFrame)
        """
    
        def implode_group(group):
            new_val = group[col].dropna().to_list()
            group = group.iloc[0]
            group[col] = new_val
            
            return group
        
        column_group = column_group if column_group else df.index
        
        return df.groupby(column_group).apply(implode_group)


    def join(self, other, self_key:str, other_key:str, keep_dataframe:bool=False, how:str='inner'):
        """
        join joins two AIH Objects. It matches the 'self_key' from the 'self' object and the 'other_key' on the 'other' object.
        
        IN: right (AIHObject)     - The AIH object that 'self' should be joined with.
            self_key (str)        - The key that it should use to match from the 'self' object.
            other_key (str        - The key that it should use to match from the 'other' object.
            keep_dataframe (bool) - To tell if the method should return the dataframe or return the object with the extended information. 
            how (str)             - Which kind of join to use. Default is 'inner'. Is ignored type of value of self_key is list.
            
        OUT:  if keep_dataframe=False - AIH Object (is also set as self.value)
              if keep_dataframe=True - Pandas.DataFrame
        """
        
        # Get the dataframes of the objects
        self_df = self.to_dataframe()
        other_df = other.to_dataframe()
        
        if type(self.get_value(self_key, -1)) == list:
            # If value of 'self_key' is of type 'list', then it will perform deeply join
            
            # Explodes to have the list values on each line
            self_df = self_df.explode(self_key)
            self_df_empty = self_df[self_df[self_key].isna()] # to be added afterwards
            self_df = self_df[~self_df[self_key].isna()]
            other_df = other_df.set_index(other_key)

            # Expands each of the values with the information from the other dataframe
            self_df[self_key] = self_df[self_key].apply(lambda x : other_df.loc[x].to_dict())

            # Concatenate with the elements that had empty lists for the key
            self_df = pd.concat([self_df, self_df_empty])

            # Implodes so the values that were split on each line are recombined into a list for the correct element
            merged = self._implode(self_df, self_key)

        else:
            # If value of 'self_key' is not of type 'list', then it will join as the 'how' parameter
            other_df.columns = other_df.columns.map(lambda name : f'{self_key}__'+ str(name))
            merged = self_df.merge(other_df, left_on=self_key, right_on=f'{self_key}__{other_key}', how=how)
            merged = merged.drop(self_key, axis=1)
        
        # Set self to the result of the join
        self = self.from_dataframe(merged)
        
        if keep_dataframe:
            return merged
        
        return self
        
    
    def __getstate__(self):
        """
        __getstate__ is used to get the state of the object.
        It is used for pickle to be able to pickle objects.

        OUT: The self.value
        """
        return self.value
    

    def __setstate__(self, state):
        """
        __setstate__ is used to set the state of the object.
        It is used for pickle to be able to unpickle pickled objects.

        IN: state - The value that should be the objects value
        """
        self.__init__()
        self.value = state


    def __str__(self):
        """
        __str__ is used to represent the object as a string.
        """

        return str(self.value)

    def __repr__(self):
        return str(self)

    def __len__(self):
        """
        __len__ is used to return the length of the object.
        In other words it returns the number objects that is represented in the self.value
        """
        
        # if isinstance(self.value, type(None)):
        #     return 0

        if isinstance(self.value, dict):
            return 1 if self.value else 0

        elif isinstance(self.value, list):
            return len(self.value)
    

    def __iter__(self):
        """
        __iter__ returns and iterator over the self.value
        """

        if isinstance(self.value, dict):
            if self.value:
                yield self.value

        elif isinstance(self.value, list):
            for elem in self.value:
                yield elem
        
        else:
            raise AIHE.AIHException(f'self.value is not of type list or dict but was {type(self.value)}')


    def __add__(self, other):
        """
        __add__ is used to combine to objects of the same type.
        It always returns the result with the self.value as a list.
        The returned object is a new object and does not operate inplace. 
        Use augmented assignmet to update self inplace.
        """

        # Check if both object are of same type
        if type(self) != type(other):
            type_self = str(self.__class__).split()[1][1:-2].rsplit(".", 1)[0]
            type_other = str(other.__class__).split()[1][1:-2].rsplit(".", 1)[0]
            raise AIHE.AIHException(f'Both objects must be of the same type. Got {type_self} and {type_other}')
        
        new_value = list(deepcopy(self))
        other_new_value = list(deepcopy(other))

        new_value.extend(other_new_value)
        new_object = self.__class__().from_list(new_value)

        return new_object

    
    def __iadd__(self, other):
        """
        __iadd__ is used to combine to objects of the same type inplace.
        It always returns the result with the self.value as a list.
        """
        
        new_object = self + other
        self.value = new_object.value
        return self

    
    def __sub__(self, other):
        """
        __sub__ is used to filter out the elements in the self.value that exists in other.value.
        It always returns the result with the self.value as a list.
        The returned object is a new object and does not operate inplace. 
        Use augmented assignmet to update self inplace.
        """

        # Check if both object are of same type
        if type(self) != type(other):
            type_self = str(self.__class__).split()[1][1:-2].rsplit(".", 1)[0]
            type_other = str(other.__class__).split()[1][1:-2].rsplit(".", 1)[0]
            raise AIHE.AIHException(f'Both objects must be of the same type. Got {type_self} and {type_other}')

        ids_to_filter_out = [elem.get('id') for elem in list(other)]

        new_value = [elem for elem in list(deepcopy(self)) if elem.get('id') not in ids_to_filter_out]

        new_object = self.__class__().from_list(new_value)

        return new_object

    
    def __isub__(self, other):
        """
        __isub__ is used to filter out the elements in the self.value that exists in other.value inplace.
        """
        
        new_object = self - other
        self.value = new_object.value
        return self