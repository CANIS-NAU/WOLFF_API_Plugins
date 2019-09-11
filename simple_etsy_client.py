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
                                     http_method = 'put',
                                     name = 'createListing'
                                   )
    etsy_hook = hook.APIHook( base_url = 'https://openapi.etsy.com/v2/',
                              methods = [ create_listing ]
                            )

    connect = conn.TCPServerConnection( ip = "127.0.0.1",
                                        port = 5555
                                      )

if __name__ == '__main__':
    main()
