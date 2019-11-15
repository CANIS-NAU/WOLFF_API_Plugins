
class APIMap:
    
    def __init__( self ):
        self.api_map = { "etsy": { 'base_url': 'https://openapi.etsy.com/v2',
                                   'create_listing': { 'uri': 'listings',
                                                       'http_method': 'post',
                                                       'service_identifier': 'shipping_template_id'
                                                     },
                                   'auth_type': "oauth1"
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
