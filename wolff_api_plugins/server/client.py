import resource

class Client:
    def __init__( self, cli_id, resources ):
        self._id = cli_id
        self._resouces_raw = resources
        self._resources = get_resources( resources )

    def get_resources( self, resources ):
        output = list()

        for res in resources:
            resource_type = get_resource( res )
            new_resource = resource_type( self.get_id(),
                                          resource[ 0 ],
                                          resources[ 1 ]
                                        )
            output.append( new_resource )
        return output

    def get_resource( resource ):
        return resource.ResourceFactory.get( resource[ 0 ] )

    def get_id( self ):
        return self._id
        
