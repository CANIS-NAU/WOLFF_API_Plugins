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
        decoded_response = json.loads( resp_message )[ 'results' ][ 0 ]
        listing_id = decoded_response[ 'listing_id' ]
        logging.getLogger().debug( f"Etsy Listing ID Retrieved: {listing_id}" )
        record_id = self._db.add_listing( listing_id, client_id )
        logging.getLogger().debug( f"Database record id: {record_id}" )
        logging.getLogger().debug( f"Writing quantity: {decoded_response[ 'quantity' ]} to the database." )
        self._db.add_listing_stock( record_id, decoded_response[ 'quantity' ] )
        record_bytes = record_id.to_bytes( 4, byteorder = 'big' )

        return record_bytes


class CheckListingStockResponseHandler:
    def __init__( self, db_connection ):
        self._db = db_connection

    def handle_response( self, resp_message, client_id ):
        logging.getLogger().warning( "CheckListingStockResponseHandler.handle_response is currently not implemented. "
                                     "It uses a dummy value that can be used to simulate a response from the server."
                                   )
        decoded_response = json.loads( resp_message )[ 'results' ][ 0 ]
        num_listings_now = decoded_response[ 'quantity' ]
        record_id = self._db.get_record_id( decoded_response[ 'listing_id' ] )

        num_listings_db = self._db.get_listing_stock( record_id )

        self._db.update_listing_stock( record_id, num_listings_now )

        num_listings_sold = num_listings_db - num_listings_now 
        num_listings_sold_bytes = num_listings_sold.to_bytes( 4, byteorder = 'big' )

        ret_val = bytearray( 2 )
        ret_val[ 0 ] = 0x01
        ret_val[ 1 ] = 0x02

        ret_val += num_listings_sold_bytes 
        ret_val += bytearray( 7 )

        return ret_val
