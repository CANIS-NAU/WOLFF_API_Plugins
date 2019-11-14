from enum import Enum

class Applications( Enum ):
    ETSY = 1

class DecoderFactory:
    def get_decoder( self, message ):
        application = self.get_service( message )

    def get_service( self, message ):
        application = message[ 0 ]

        if application == Aplications.ETSY:
            return EtsyDecoder()

class EtsyDecoder:
    class Services( Enum ):
        CREATE_LISTING = 1

    def __init__( self ):
        pass

