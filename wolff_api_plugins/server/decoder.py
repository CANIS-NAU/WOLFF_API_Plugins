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
        self.title_map       = { 0x01: 'title_1' }
        self.description_map = { 0x02: 'desc_1' }
        self.who_made_map    = { 0x01: 'i_did',
                                 0x02: 'collective',
                                 0x03: 'someone_else'
                               }
        self.when_made_map   = { 0x01: 'made_to_order',
                                 0x02: '2010_2019',
                                 0x03: '2000_2009',
                                 0x04: 'before_2000',
                                 0x05: '1990s',
                                 0x06: '1980s',
                                 0x07: '1970s',
                                 0x08: '1960s'
                               }


    def is_etsy_message( self, message ):
        return message[ 0 ] in EtsyDecoder.Services

    def get_service_decoder( self, message ):
        if message[ 1 ] == EtsyDecoder.Services.CREATE_LISTING:
            return self._decode_create_listing_message

    def decode( self, message ):
        assert( self.is_etsy_message( message ) )

        decode_fn = self.get_service_decoder( message )

        return decode_fn( message )

    def _get_price( self, price_bytes ):
        integral_byte   = price_bytes[ 0 ]

        # mask off first 4 bytes
        fractional_byte = price_bytes[ 1 ] & 0x0F
        fractional_price = int( fractional_byte ) / 100.0

        integral_second_half = ( price_bytes[ 1 ] & 0xF0 ) >> 4

        integral_price = ( int( integral_byte ) * 16 ) + int( integral_second_half )

        price = integral_price + fractional_price

        return price



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

        when_made_mask = 0b01110000
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
        
