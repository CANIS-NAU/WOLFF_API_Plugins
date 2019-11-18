#!/usr/bin/env python3 

from . resource import *

class Client:
    """
    A client has a certain number of resources that 
    are each stored in a file at a path. 
    """
    def __init__( self, cli_id, resources, base_path = '.' ):
        """
        Initialize a client with an id, certain resources, and 
        a base path from which the client references it sresources.
        
        Params:
           cli_id: Id of the client to create. This ID should be unique to a 
                  certain directory in which clients are located.
           resources: The resources a client is created with.
           base_path: The base path for the client's resources.

        """
        self._id = cli_id
        self._resouces_raw = resources.copy()
        self._resources = self.instantiate_resources( resources, base_path )

    def instantiate_resources( self, resources, base ):
        """
        Instantiate resources for a client. 
        
        Params:
            resources: A list of resources to instantiate
            
            base: the base path for the resources
        """
        output = dict()

        get_val = lambda x: x[ 2 ] if len( x ) == 3 else None

        for res in resources:
            res_trim = res[ 0 : 2 ]
            resource_type = self._get_resource( res_trim )
            new_resource = resource_type( self.get_id(), 
                                          '/'.join( res_trim ),
                                          root_path = base,
                                          values = get_val( res )
                                        )
            output[ '/'.join( res_trim ) ] = new_resource
        return output

    def _get_resource( self, to_get ):
        return ResourceFactory.get( to_get[ 1 ] )

    def get_id( self ):
        return self._id

    def get_resource( self, service, resource ):
        return self._resources[ '/'.join( [ service, resource ] ) ]

if __name__ == '__main__':

    cli = Client( 'client_1', [ ( 'etsy', 'oauth1' ) ] )

    print( cli.get_id() )
    etsy_resource = cli.get_resource( 'etsy', 'oauth1' )
    data = etsy_resource.get_data().copy()
    etsy_resource.write( data, override = True )
