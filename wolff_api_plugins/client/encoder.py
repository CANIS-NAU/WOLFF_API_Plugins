from enum import Enum

# TODO: Applications is duplicated between encoder/decoder
class Applications( Enum ):
    ETSY = 1

class EtsyEncoder:
    class Services( Enum ):
        CREATE_LISTING = 1

    def __init__( self ):
        self.title_map       = { 'title_1': 0x01 }
        self.description_map = { 'desc_1': 0x02 }
        self.who_made_map    = { 'i_did': 0x01,
                                 'collective': 0x02,
                                 'someone_else': 0x03
                               }
        self.when_made_map   = { 'made_to_order': 0x01,
                                 '2010_2019': 0x02,
                                 '2000_2009': 0x03,
                                 'before_2000': 0x04,
                                 '1990s': 0x05,
                                 '1980s': 0x06,
                                 '1970s': 0x07,
                                 '1960s': 0x08
                                 
                               }


    def encode( self, etsy_data ):
        encoding_method = self._get_encoding_method( etsy_data )

        return encoding_method( etsy_data )

    def _get_encoding_method( self, etsy_data ):
        if etsy_data[ 'method' ].get_name() == 'create_listing':
            return self._encode_create_listing

    def _encode_create_listing( self, create_listing_data ):
        payload = bytearray( [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] )
        payload[ 0 ] |= Applications.ETSY.value
        payload[ 1 ] |= EtsyEncoder.Services.CREATE_LISTING.value

        title = create_listing_data[ 'title' ]
        payload[ 2 ] |= self.title_map[ title ]

        description = create_listing_data[ 'description' ]
        payload[ 3 ] |= self.description_map[ description ]

        quantity = create_listing_data[ 'quantity' ]
        assert( quantity > 0 and quantity < 256 )
        payload[ 4 ] |= quantity

        price = create_listing_data[ 'price' ]
        price_integral = int( price )
        price_fraction = int( ( price * 100 ) % 100 )

        assert( price_integral < 4095 )
        assert( 0 <= price_fraction and price_fraction < 16 )

        integral_left_4digits = price_integral % 16
        integral_right_8digits = price_integral // 16
        price_fraction_digits = price_fraction

        payload[ 5 ] |= integral_left_4digits

        integral_mask = 0b11110000
        fraction_mask = 0b00001111

        payload[ 6 ] |= ( integral_mask & ( integral_right_8digits << 4 ) ) \
                       | ( fraction_mask & price_fraction_digits )

        # who_made, when_made, is_supply
        wm_whm_is_byte = 0x00
        wm_whm_is_byte = 0b10000000 & ( create_listing_data[ 'is_supply' ] << 7 )
        wm_whm_is_byte |= self.when_made_map[ create_listing_data[ 'when_made' ] ]
        wm_whm_is_byte |= self.who_made_map[ create_listing_data[ 'who_made' ] ]

        payload[ 7 ] |= wm_whm_is_byte

        shipping_template_id = int( create_listing_data[ 'shipping_template_id' ] )

        stp1 = shipping_template_id % 256
        shipping_template_id //= 256

        stp2 = shipping_template_id % 256
        shipping_template_id //= 256

        stp3 = shipping_template_id % 256
        shipping_template_id //= 256

        stp4 = shipping_template_id % 256
        shipping_template_id //= 256

        stp5 = shipping_template_id

        payload[ 8 ]  = stp1
        payload[ 9 ]  = stp2
        payload[ 10 ] = stp3
        payload[ 11 ] = stp4
        payload[ 12 ] = stp5

        return payload



