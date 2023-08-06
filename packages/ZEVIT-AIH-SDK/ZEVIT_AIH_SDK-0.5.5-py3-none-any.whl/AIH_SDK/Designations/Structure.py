from AIH_SDK.Designations.DesignationsObject import DesignationsObject


class Structure(DesignationsObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'structures'
        self._object_name = 'StructureDTO'

    
    def get_nodes(self, depth=1):
        """
        get_nodes gets the nodes in the structure.

        IN: depth (int) - The depth of the tree to get back. -1 return the full tree.

        OUT: if self.value is a dict it returns a StructureNode object with the nodes of the structure.
             if self.value is a list it will return a list of StructureNode objects.
        """
        if isinstance(self.value, dict):
            nodes = StructureNode(self.get_value('id')).get(parameters=[('depth', depth)])
        
        elif isinstance(self.value, list):
            nodes = [
                StructureNode(structure_id).get(parameters=[('depth', depth)])
                for structure_id
                in self.get_value('id')
            ]
        
        return nodes



class StructureNode(DesignationsObject):
    
    def __init__(self, structure_id:str):
        super().__init__()
        self.structure_id = structure_id
        self._endpoint = f'structures/{structure_id}/nodes'
        self._object_name = 'StructureDTO'

