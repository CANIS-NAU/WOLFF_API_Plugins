import os
import resource
from . client import Client

class ClientManager:
    def __init__( self, client_dir ):
        self._dir = client_dir
        self._clients = dict()
        self._clients_from_dir( client_dir )

    def _clients_from_dir( self, search_dir ):
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
            self._clients[ new_client.get_id() ] = new_client

    def get_client_by_id( self, client_id ):
        return self._clients[ client_id ]

    def check_existing_client( self, client_id ):
        if client_id in self._clients:
            raise ValueError( f"Client with id {new_client.get_id()}"
                               "already exists!"
                            )
        
    def register_existing_client( self, new_client ):
        self.check_existing_client( new_client.get_id() )
        self._clients[ new_client.get_id() ] = new_client

    def _get_client_nums( self ):
        get_num = lambda x: int( x.split( '_' )[ 1 ] )
        client_ids = list( self._clients.keys() )
        return [ get_num( cli_id ) for cli_id in client_ids ]

    def register_client( self, resources ):
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
