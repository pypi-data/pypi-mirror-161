#from __future__ import annotations
from AIH_SDK.Object import Object
from AIH_SDK.AIHClient import AIHClient
from collections import defaultdict
import pandas as pd
import numpy as np
import json

class v2Object(Object):
    
    def __init__(self):
        super().__init__()
        self._object_schemas = None


    def get(self, id:str=None, parameters:dict={}):
        """
        To get a list of all objects or a specific object.
        Result is set as self.value

        IN: id (str)          - The id of the object to get.
            parameters (dict) - A dictionary of the parameters to include in the query.
        
        OUT: self
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}', parameters)
        else:
            self.value = self._client._get(self._api, self._endpoint, parameters)
    
        return self


    def get_object_schema(self, object_name=None, max_depth=5):
        
        # Get all schemas if not already gotten
        if self._object_schemas is None:
            json = self._client._get(self._api, f'swagger/{self._version}/swagger.json')
            self._object_schemas = json['components']['schemas']
        
        # Override object name if specified in class or in method
        if object_name is None:
            if hasattr(self, '_object_name'):
                object_name = self._object_name
            else:
                object_name = self.__class__.__name__

        # Get schema for the given object
        object_schema = self._object_schemas[object_name]
        if 'properties' in object_schema:
            object_schema = object_schema['properties']

        # Extract nested objetc references
        object_schema = self._extract_references(object_schema, max_depth)

        return object_schema


    def _extract_references(self, object_schema, max_depth):

        if max_depth == 0:
            return object_schema
        
        for key, value in object_schema.items():
            ref_name = self._get_ref_name(value)
            if 'allOf' in value:
                object_schema[key] = self.get_object_schema(ref_name, max_depth-1)

            elif 'items' in value and '$ref' in value['items']:
                object_schema[key]['items'] = self.get_object_schema(ref_name, max_depth-1)
            
            elif '$ref' in value:
                object_schema[key] = self.get_object_schema(ref_name, max_depth-1)

        return object_schema
    

    def _get_ref_name(self, value):

        if 'allOf' in value:
            value = value['allOf'][0]
        elif 'items' in value and '$ref' in value['items']:
            value = value['items']
        elif '$ref' in value:
            value = value
        else:
            return None

        name = value['$ref'].split('/')[-1]

        return name