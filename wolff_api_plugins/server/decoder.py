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

    def __init__( self ):
        self.title_map       = { 0x00: '' }
        self.description_map = { 0x00: '' }
        self.who_made_map    = { 0x00: '' }
        self.when_made_map   = { 0x00: '' }

    def is_etsy_message( self, message ):
        return message[ 0 ] in EtsyDecoder.Services

    def get_service_decoder( self, message ):
        if message[ 1 ] == EtsyDecoder.Services.CREATE_LISTING:
            return self._decode_create_listing_message


    def _decode_create_listing_message( self, message ):
        output = dict()

        title = message[ 2 ]
        output[ 'title' ] = self.title_map[ title ]

        description = message[ 3 ]
        output[ 'description' ] = self.description_map[ description ]

        quantity = message[ 4 ]
        output[ 'quantity' ] = quantity

        price = self._get_price( message[ 5:7 ] )
        output[ 'price' ] = price

        who_made = message[ 7 ] >> 4
        output[ 'who_made' ] = self.who_made_map[ who_made ]

        when_made_mask = 0b00001110
        when_made = ( message[ 7 ] & when_made_mask ) >> 1
        output[ 'when_made' ] = self.when_made_map[ when_made ]

        is_supply = ( message[ 7 ] & 0b10000000 ) >> 7
        output[ 'is_supply' ] = is_supply

        # stp = shipping_template_part
        stp1 = int( message[ 8 ] )
        stp2 = int( message[ 9 ] )
        stp3 = int( message[ 10 ] )
        stp4 = int( message[ 11 ] )
        stp5 = int( message[ 12 ] )

        shipping_template_id = ( stp1 * ( 256 ** 4 ) ) + \
                               ( stp2 * ( 256 ** 3 ) ) + \
                               ( stp3 * ( 256 ** 2 ) ) + \
                               ( stp4 * ( 256 ** 1 ) ) + \
                               ( stp5 * ( 256 ** 0 ) )
        output[ 'shipping_template_id' ] = shipping_template_id

        return output
        
