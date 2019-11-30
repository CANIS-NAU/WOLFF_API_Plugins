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
                  values = None,
                  root_path = '.'
                ):
        """
        Create a new FileResource, with resource_id and 
        a base path.
        
        @param resource_id The id of this resource. It should be unique.
        @param resource_name: The name of the value of the resource. This will 
                       be the name of the text file.
        
        @param base_path Base of the path to write files to. 
                     Files will be written to resource_id/base_path
        """
        self._id   = resource_id
        self._path = base_path
        self._root = root_path
        self._resource_name = resource_name
        self._data = None

        self._create_dir( f'{root_path}/{resource_id}/{base_path}' )

        if values:
            self.write( values )

    def contains( self, val ):
        """
        Determine if this resource contains a value.
        This method is generally not useful for the base class.
        """
        my_vals = self.get_data()

        return val in my_vals 

    def get_data( self ):
        """
        Return the data stored in this 
        resource, reading it from the file if 
        necessary
        """
        if not self._data:
            self._data = self.read()
        return self._data

    def _create_dir( self, path ):
        pathlib.Path( path ).mkdir( parents = True, exist_ok = True )
                
    def read( self ):
        """
        Read the data for a resource from its file. 
        The complete filepath is constructed from 
        id, base_path, and resource_name.
        
        @returns the lines from the resource file in a list.
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
        @note This method does not return the complete path of the resource,
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

    def __ne__( self, other ):
        return not ( self == other )

class OAuth1Resource( FileResource ):
    def __init__( self, resource_id, base_path, root_path = '.',
                  values = None
                ):
        """
        Create a new OAuth1 resource, with resource_id and 
        a base path.
        
        @param resource_id: The id of this resource. It should be unique.
        
        @param base_path Base of the path to write files to. 
                     Files will be written to resource_id/base_path
        """
        super().__init__( resource_id, base_path, "keys.tsv",
                          root_path = root_path
                        )

        self._data = dict()

        if values:
            self.write( values )
            self._data = values

    def read( self ):
        """
        Read the value for the resouce from a file.
        @returns A dictionary containing the necessary key/value pairs for 
          OAuth1 identification.
        """
        output = dict()
        
        file_lines = super().read()

        for line in file_lines:
            key, value  = line.split( '\t' )

            output[ key ] = value
        return output

    def write( self, values, override = False ):
        """
        Write a dictionary of OAuth1 key/value pairs to this resource.
        
        @throws OSError if override is false and the specified file already exists
        @param values a dictionary of key/value pairs necessary for oauth authentication
        @param override include if you want an existing file with this resources'
                     path to be overwritten. If this flag is not True,
                     an OSError will be raised upon existing file.
        """
        if not( override ) and os.path.exists( self.get_full_file_path() ):
            raise OSError( f"File {self.get_full_file_path()} exists!" )

        with open( self.get_full_file_path(), 'w' ) as out_file:
            for key, value in values.items():
                out_file.write( f'{key}\t{value}\n' )
        self._data = values.copy()

    def __hash__( self ):
        return hash( "oauth1" )

class ShippingTemplateIdResource( FileResource ):
    """
    A resource representing the ShippingTemplateId 
    for Etsy's create listing method.
    """
    def __init__( self, resource_id, base_path, root_path = '.',
                  values = None
                ):
        super().__init__( resource_id, base_path, "shipping_template_id.txt",
                          root_path = root_path
                        )

        self._data = dict()

        if values:
            self.write( values )
            self._data = values

    def write( self, values, override = False ):
        if not( override ) and os.path.exists( self.get_full_file_path() ):
            raise OSError( f"File {self.get_full_file_path()} exists!" )

        with open( self.get_full_file_path(), 'w' ) as of:
            for val in values:
                of.write( f'{val}\n' )

    def read( self ):
        output = set()

        with open( self.get_full_file_path(), 'r' ) as of:
            for line in of:
                stripped = line.strip()
                output.add( stripped )
        return output
    

    def __hash__( self ):
        return hash( "shipping_template_id" )
            
class ResourceFactory:
    def get( str_type ):
        if str_type == "oauth1":
            return OAuth1Resource
        if str_type == "shipping_template_id":
            return ShippingTemplateIdResource
        return None
