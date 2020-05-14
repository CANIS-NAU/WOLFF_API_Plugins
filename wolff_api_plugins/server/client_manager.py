import os
import resource
from . client import Client

class ClientManager:
    """
    A ClientManager handles clients and the resources 
    that they use. Each managed client has a number of resources
    that allow the client to have persistent data. 
    """
    def __init__( self, client_dir ):
        """
        Create a ClientManager, whose clients are in client_dir.
        Within client_dir, each client with id x is represented in 
        client_dir/client_x, where x is the client's id. 
        
        Additionally stores a connection to a WOLFF database 
        containing information regarding records that have been created
        """
        self._dir = client_dir
        self._clients = dict()
        self._clients_from_dir( client_dir )

    def _clients_from_dir( self, search_dir ):
        """
        Get clients from a specified search_dir. 
        Each client is retrieved with its resources.
        """
        clients = dict()

        # get the full path for each client
        for root, dirs, files in os.walk( search_dir ):
            if files:
                separated_path = root.split( '/' )
                base, client_id, service, resource = separated_path

                if client_id not in clients:
                    clients[ client_id ] = list()
                clients[ client_id ].append( ( service, resource ) )

        for client, resources in clients.items():
            new_client = Client( client, resources, base_path = self._dir )
            # logging.getLogger().debug( f"Created new client {client.get_id()} "
            #                            f"with resources: {''.join( resources )}"
            # )
            self._clients[ new_client.get_id() ] = new_client

    def get_client_by_id( self, client_id ):
        return self._clients[ client_id ]

    def check_existing_client( self, client_id ):
        """
        Check whether a client already exists. 
        A client exists if 'client_x' exists in 
        client_dir, where x is the id of this client.
        
        Throws:
           ValueError if the client with client_id already exists.
        """
        if client_id in self._clients:
            raise ValueError( f"Client with id {new_client.get_id()}"
                               "already exists!"
                            )

    def get_client_by_service_identifier( self, service,
                                          identifier,
                                          identifier_value
                                        ):
        """
        Retrieve a client by a service identifier. 
        A service identifier is used to uniquely identify a client 
        that uses a service. 

        @param service the service (etsy, for example) to identify 
                  a client in.
        @param identifier the identifier to try and identify a client by.
                     For example, an etsy client can be identified by 
                     a 'shipping_template_id'.
        @param identifier_value the value of the identifier. A client who has this
                           identifier (if any) will be returned.
        """
        identifier_value = str( identifier_value )

        if identifier == 'listing_id':
            listing_id = self.conn.get_listing_id( identifier_value )
            cli_id = self.conn.get_client_by_listing_id( listing_id )
            return self.get_client_by_id( cli_id )
        
        for client in self.get_clients():
            
            try:
                result = client.get_resource( service, identifier ) \
                               .contains( identifier_value )
                if result:
                    return client

            # client doesn't have this service
            except:
                pass

        logging.getLogger().debug( f"Failed to find a client with identifier ({identifier}) for "
                                   f"service {service}."
        )
        
    def get_clients( self ):
        return self._clients.values()

    def register_existing_client( self, new_client ):
        """
        Register a client object that has already been initialized.
        
        @param new_client a Client object that will be initialized.
        
        @pre new_client.get_id() cannot be in self.client_dir
        """
        self.check_existing_client( new_client.get_id() )
        self._clients[ new_client.get_id() ] = new_client

    def _get_client_nums( self ):
        """
        Get the client numbers for each client. 
        
        Returns:
           a list of integer client ids.
        """
        get_num = lambda x: int( x.split( '_' )[ 1 ] )
        client_ids = list( self._clients.keys() )
        return [ get_num( cli_id ) for cli_id in client_ids ]

    def register_client( self, resources ):
        """
        Register a client with certain resources.
        Creates the necessary file structure for each resource.
        """
        client_num = max( self._get_client_nums() ) + 1

        new_cl_id = f'client_{client_num}'

        self.check_existing_client( new_cl_id )

        new_client = Client( new_cl_id, resources,
                             base_path = self._dir
                           )

        self.register_existing_client( new_client )

if __name__ == '__main__':
    cli = ClientManager( 'clients' )
    data = cli.get_client_by_id( 'client_1' ) \
           .get_resource( 'etsy', 'oauth1' ) \
           .get_data()

    print( data )
    cli.register_client( [ ( 'etsy', 'oauth1', data ) ] )
    cli.register_client( [ ( 'etsy', 'oauth1', data ) ] )
    cli.register_client( [ ( 'etsy', 'oauth1', data ) ] )
    cli.register_client( [ ( 'etsy', 'oauth1', data ) ] )
