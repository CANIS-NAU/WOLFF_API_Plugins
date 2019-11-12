import sys
import os

class FileResource:
    """
    A FileResource is a resource that is located in a file. 
    This class provides methods for creation, editing, etc. of 
    FileResources.
    """
    def __init__( self, resource_id, base_path, resource_name ):
        """
        Create a new FileResource, with resource_id and 
        a base path.
        
        Params:
          resource_id: The id of this resource. It should be unique.
          resource_name: The name of the value of the resource. This will 
                       be the name of the text file.
        
          base_path: Base of the path to write files to. 
                     Files will be written to resource_id/base_path
        """
        self._id   = resource_id
        self._path = base_path
        self._resource_name = resource_name


