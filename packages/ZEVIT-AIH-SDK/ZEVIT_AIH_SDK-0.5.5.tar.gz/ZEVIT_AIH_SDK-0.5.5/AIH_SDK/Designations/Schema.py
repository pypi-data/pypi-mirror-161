from AIH_SDK.Designations.DesignationsObject import DesignationsObject


class Schema(DesignationsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'schemas'

    
    def get_nodes(self, depth=1):
        """
        get_nodes gets the nodes in the schema.

        IN: depth (int) - The depth of the tree to get back. -1 return the full tree.

        OUT: if self.value is a dict it returns a SchemaNode object with the nodes of the schema.
             if self.value is a list it will return a list of SchemaNode objects.
        """
        if isinstance(self.value, dict):
            nodes = SchemaNode(self.get_value('id')).get(parameters=[('depth', depth)])
        
        elif isinstance(self.value, list):
            nodes = [
                SchemaNode(schema_id).get(parameters=[('depth', depth)])
                for schema_id
                in self.get_value('id')
            ]
        
        return nodes



class SchemaNode(DesignationsObject):
    
    def __init__(self, schema_id:str):
        super().__init__()
        self.schema_id = schema_id
        self._endpoint = f'schemas/{schema_id}/nodes'

