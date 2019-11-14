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

        @classmethod
        def has_value( cls, value ):
            return value in cls._value2member_map_

    def is_etsy_message( self, message ):

    def get_service_decoder( self, message ):
        if message[ 1 ] == EtsyDecoder.Services.CREATE_LISTING:
            return self._decode_create_listing_message


