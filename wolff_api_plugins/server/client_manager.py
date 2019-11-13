import resource
import client

class ClientManager:
    def __init__( self, client_dir ):
        self._dir = client_dir
        self._clients = _clients_from_dir( client_dir )

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

    def client_from_dir( path ):
        client_details = path.split( '/' )






