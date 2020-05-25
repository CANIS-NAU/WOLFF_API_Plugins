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
        return self.api_map[ service ][ method ][ 'uri' ]

    def get_complete_url( self, service, method,
                         replace = None # replacement to be used later
                       ):
        return f'{self.get_base_url( service )}' \
               f'/{self.get_uri( service, method) }/' 

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
