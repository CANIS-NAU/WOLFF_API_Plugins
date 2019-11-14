import api_method

class EndpointManager:
    def __init__( self ):
        pass



class EtsyEndpointManager( EndpointManager ):
    def __init__( self ):
        self._base_url = 'https://openapi.etsy.com/v2/'

        create_listing = api_method.APIMethod( uri = 'listings',
                                               http_method = 'post',
                                               name = 'create_listing',
                                               args = { 'quantity': 0, 'title': '',
                                                        'description': '', 'price': 0,
                                                        'who_made': '', 'is_supply': True,
                                                        'when_made': '',
                                                        'shipping_template_id': 0
                                               }
                                             )

        self._methods = { 'create_listing': create_listing
                        }

    def get_base_url( self ):
        return self._base_url

    def get_method( self, method_name ):
        return self._methods[ method_name ]
