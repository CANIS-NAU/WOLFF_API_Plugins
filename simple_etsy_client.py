#!/usr/bin/env python3
import wolff_api_plugins.client.api_hook as hook
import wolff_api_plugins.client.client as client
import wolff_api_plugins.client.server_connection as conn
import wolff_api_plugins.client.oauth_credentials as cred

def main():

    args = { 'quantity': 0, 'title': '', 'description': '',
                'price': 0, 'who_made': '', 'is_supply': True, 'when_made': '',
                'shipping_template_id': 0
           }

    create_listing = hook.APIMethod( uri = 'listings',
                                     args = args,
                                     http_method = 'post',
                                     name = 'createListing'
                                   )


    connect = conn.MQTTServerConnection( ip = "127.0.0.1",
                                         port = 1883
                                      )
    auth = cred.OAuth1Credentials()
    auth.get_from_file( 'etsy_keys.tsv' )

    args = { 'user_id': '' }

    gubo = hook.APIMethod( uri = '/users/:user_id/billing/overview',
                           args = args, http_method = 'get', name = 'gubo'
                         )

    etsy_hook = hook.APIHook( base_url = 'https://openapi.etsy.com/v2',
                              methods = [ create_listing, gubo ]
                            )


    etsy_client = client.Client( connection = connect, endpoint = etsy_hook,
                                 credentials = auth
                                )
    etsy_client.specialize()

    # result = etsy_client.createListing( quantity = 1, title = "Will this work?",
    #                                     description = "Description of the item.",
    #                                     price = 0.45, who_made = 'i_did', is_supply = True,
    #                                     when_made = 'made_to_order', shipping_template_id = 76575991147
    #                                   )

    result = etsy_client.gubo( user_id = 'ezk6e2q6' )
    print( result )


if __name__ == '__main__':
    main()
