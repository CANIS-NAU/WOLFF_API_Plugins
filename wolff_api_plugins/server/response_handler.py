import json
import logging

class ResponseHandler:
    def __init__( self, db_conn  ):
        self._conn = db_conn

    def get_handler( self, data_dict ):
        api_tuple = data_dict[ 'api_details' ]
        if api_tuple[ 0 ] == 'etsy':
            if api_tuple[ 1 ] == 'create_listing':
                logging.getLogger().debug( "Creating a ResponseHandler for "
                                           "Etsy/CreateListing"
                )
                return CreateListingResponseHandler( self._conn )

            elif api_tuple[ 1 ] == 'check_listing_stock':
                logging.getLogger().debug( "Creating a ResponseHandler for "
                                           "etsy/check_listing_stock"
                )
                return CheckListingStockResponseHandler( self._conn )

            else:
                logging.getLogger().error( "{api_tuple[ 0 ]}/{api_tuple[ 1 ]} is not a valid service/method specifier." )
                raise ValueError( "Invalid service/method specifier included" ) 




class CreateListingResponseHandler:
    def __init__( self, db_connection ):
        self._db = db_connection
        
    def handle_response( self, resp_message, client_id ):
        logging.getLogger().debug( "Attempting to retrieve a result from the database." )
        listing_id = json.loads( resp_message )[ 'results' ][ 0 ][ 'listing_id' ]
        logging.getLogger().debug( f"ID Retrieved: {listing_id}" )
        return self._db.add_listing( listing_id, client_id ).to_bytes( 4, byteorder = 'big' )


class CheckListingStockResponseHandler:
    def __init__( self, db_connection ):
        self._db = db_connection

    def handle_response( self, resp_message, client_id ):
        logging.getLogger().warning( "CheckListingStockResponseHandler.handle_response is currently not implemented. "
                                     "It uses a dummy value that can be used to simulate a response from the server."
                                   )

        return bytearray( [ 0x01, 0x02, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ] )
