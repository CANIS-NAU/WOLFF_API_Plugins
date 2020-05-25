import logging
import re
import sys

class APIMap:
    """
    An APIMap contains the information necessary to retrieve 
    the base url, methods and their arguments, 
    and authentication types for services.
    """
    def __init__( self ):
        """
        Create the api map.
        For each service, we list its base url,
        its methods, and the authentication type.
        
        For each method, the uri, http method, and service 
        identifier are listed. The service_identifier is an identifier 
        that is unique to a user that wants to perform a method.
        From this service identifier, a user can be identified.
        """
        self.api_map = { "etsy": { 'base_url': 'https://openapi.etsy.com/v2',
                                   'create_listing': { 'uri': 'listings',
                                                       'http_method': 'post',
                                                       'service_identifier': 'shipping_template_id',
                                                       'special': { 'taxonomy_id': 1 }
                                                     },
                                   'update_listing': { 'uri': '/listings/:listing_id',
                                                       'http_method': 'put',
                                                       'service_identifier': 'listing_id'
                                                     },
                                   'check_listing_stock': { 'uri': '/listings/:listing_id',
                                                            'http_method': 'get',
                                                            'service_identifier': 'listing_id'
                                                     },
                                   'auth_type': "oauth1",
                                   'uri_re': re.compile( ":((?:[a-zA-Z]|_)+)" )
                                  }
                       }

    def get_base_url( self, service ):
        return self.api_map[ service ][ 'base_url' ]
    def get_uri( self, service, method ):
        logging.getLogger().debug( f"Retrieving URI for: {service}/{method}" )
        return self.api_map[ service ][ method ][ 'uri' ]

    def uri_is_substitutable( self, uri ):
        return ':' in uri

    def perform_uri_replacement( self, uri, uri_re, value ):
        return re.sub( uri_re, value, uri )

    def get_replacement( self, service, method, data_dict, database ):
        identifier = self.get_service_identifier( service, method )
        if identifier == 'listing_id':
            listing_id = database.get_record_id( data_dict[ 'listing_id' ] )
            return listing_id

    def get_complete_url( self, service, method,
                         replace = None
                       ):
        complete_url = f'{self.get_base_url( service )}'

        request_uri = self.get_uri( service, method )

        if self.uri_is_substitutable( request_uri ) and not replace:
            error_str = f"A substitutable URI ('{request_uri}') was "
            "included, but the 'replace' argument is None"

            logging.getLogger().error( error_str )
            raise ValueError( error_str )

        elif self.uri_is_substitutable( request_uri ) and replace:
            request_uri = self.perform_uri_replacement( request_uri,
                                                        self.api_map[ service ][ 'uri_re' ],
                                                        replace
                                                      )
            logging.getLogger().debug( f"URI after replacement: {request_uri}" )

        complete_url += f"/{request_uri}/"

        logging.getLogger().debug( f"Complete url: {complete_url}" )
        return complete_url

    def get_http_method( self, service, method ):
        return self.api_map[ service ][ method ][ 'http_method' ]

    def get_auth_type( self, service ):
        return self.api_map[ service ][ 'auth_type' ]

    def get_service_identifier( self, service, method ):
        return self.api_map[ service ][ method ][ 'service_identifier' ]

    def get_identifier_value( self, service, method, data ):
        identifier = self.get_service_identifier( service, method )

        if identifier == 'shipping_template_id':
            return data[ 'message' ][ service_identifier ]
        elif identifier == 'listing_id':
            return data[ 'listing_id' ]
