
class APIMethod:
    def __init__( self, uri = '',
                  http_method = '',
                  name = '',
                  args = None
                ):
        self._uri = uri
        self._http_method = http_method
        self._name = name
        self._args = args if args else dict()

    def get_name( self ):
        return self._name

    def get_uri( self ):
        return self._uri

    def get_http_hethod( self ):
        return self._http_method
