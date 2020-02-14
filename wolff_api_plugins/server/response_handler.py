import json

class ResponseHandler:
    def __init__( self, db_conn  ):
        self._conn = db_conn

    def get_handler( self, data_dict ):
        api_tuple = data_dict[ 'api_details' ]
        if api_tuple[ 0 ] == 'etsy':
            if api_tuple[ 1 ] == 'create_listing':
                return CreateListingResponseHandler( self._conn )




class CreateListingResponseHandler:
    def __init__( self, db_connection ):
        self._db = db_connection
        
    def handle_response( self, resp_message, client_id ):
        listing_id = json.loads( resp_message )[ 'results' ][ 0 ][ 'listing_id' ]
        return self._db.add_listing( listing_id, client_id )
