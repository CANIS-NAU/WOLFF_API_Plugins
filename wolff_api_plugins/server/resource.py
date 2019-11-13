import sys
import os
import pathlib

class FileResource:
    """
    A FileResource is a resource that is located in a file. 
    This class provides methods for creation, editing, etc. of 
    FileResources.
    """
    def __init__( self, resource_id, base_path, resource_name = "resource.txt",
                  root_path = '.'
                ):
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
        self._root = root_path
        self._resource_name = resource_name

        self._create_dir( f'{root_path}/{resource_id}/{base_path}' )

    def _create_dir( self, path ):
        pathlib.Path( path ).mkdir( parents = True, exist_ok = True )
                
    def read( self ):
        """
        Read the data for a resource from its file. 
        The complete filepath is constructed from 
        id, base_path, and resource_name.
        
        Returns:
           the lines from the resource file in a list.
        """
        full_path = self.get_full_file_path()

        open_f = open( full_path )
        out_data = list( map( str.strip, open_f.readlines() ) )
        open_f.close()
        
        return out_data

    def write( self, str_data ):
        pass

    def get_file_name( self ):
        """
        Get the filename for the resource, 
        without any of the leading path information.

        Returns:
          the name of the file this resource is associated with
        """
        return self._resource_name
    
    def get_full_path( self, include_trailing = True ):
        """
        Get the full path of the location of the resource.
        Note:
          This method does not return the complete path of the resource,
          only the path of its location.
        """
        trailing = ""
        if include_trailing:
            trailing = "/"

        return f'{self._root}/{self._id}/{self._path}{trailing}'

    def get_full_file_path( self ):
        """
        Get the entire path of the resource.
        """
        return self.get_full_path() + self.get_file_name()

    def __eq__( self, other ):
        return self.__class__ == other.__class__


        """
        Create a new OAuth1 resource, with resource_id and 
        a base path.
        
        Params:
          resource_id: The id of this resource. It should be unique.
        
          base_path: Base of the path to write files to. 
                     Files will be written to resource_id/base_path
        """
        super().__init__( resource_id, base_path, "keys.tsv",
                          root_path = root_path
                        )

        self._data = dict()

    def read( self ):
        """
        Read the value for the resouce from a file.
        Returns:
          A dictionary containing the necessary key/value pairs for 
          OAuth1 identification.
        """
        output = dict()
        
        file_lines = super().read()

        for line in file_lines:
            key, value  = line.split( '\t' )

            output[ key ] = value
        return output

    def get_data( self ):
        if not self._data:
            self._data = self.read()
        return self._data

    def write( self, values, override = False ):
        """
        Write a dictionary of OAuth1 key/value pairs to this resource.
        
        Throws:
          OSError if override is false and the specified file already exists
        Params:
           values: a dictionary of key/value pairs necessary for oauth authentication
           override: include if you want an existing file with this resources'
                     path to be overwritten. If this flag is not True,
                     an OSError will be raised upon existing file.
        """
        if not( override ) and os.path.exists( self.get_full_file_path() ):
            raise OSError( f"File {self.get_full_file_path()} exists!" )

        with open( self.get_full_file_path(), 'w' ) as out_file:
            for key, value in values.items():
                out_file.write( f'{key}\t{value}\n' )

class ResourceFactory:
    def get( str_type ):
        if str_type == "oauth1":
            return OAuth1Resource
