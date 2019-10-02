#!/usr/bin/env python3
from requests_oauthlib import OAuth1Session
import json
import socket
import argparse

def main():
    arg_parser = argparse.ArgumentParser( description = "Perform the Etsy OAuth 1.0 authentication flow, store keys in a file "
                                                        "usable by our credentials class."
                                        )
    arg_parser.add_argument( '--key_file', help = "Headerless tab-delimited file that will initially contain the client_key and client_secret items. "
                                                  "Using these, this script goes through the authentication flow for full authentication. "
                                                  "Two new lines will be written to this file: resource_owner_key and resource_owner_secret. " ,
                             type = str
                           )

    args = arg_parser.parse_args()

    credentials =  parse_keys_from_f( args.key_file )

    base_url = 'https://openapi.etsy.com/v2/oauth'

    req_url = f'{base_url}/request_token'
    auth_url = f'{base_url}/signin'
    access_url = f'{base_url}/access_token'

    oauth = OAuth1Session( credentials[ 'client_key' ],
                           client_secret = credentials[ 'client_secret' ],
                           callback_uri = "https://canis-lab.com"
    ) 

    fetch_response = oauth.fetch_request_token( req_url )

    resource_owner_key = fetch_response.get( 'oauth_token' )
    resource_owner_secret = fetch_response.get( 'oauth_token_secret' )
    login_url = fetch_response.get( 'login_url' )

    authorization_url = oauth.authorization_url( login_url )

    print( f"Please go to the following and authorize: {authorization_url}" )

    authorization_response = input( "Enter the URL:\n" )

    oauth_response = oauth.parse_authorization_response( authorization_response )

    verifier = oauth_response.get( 'oauth_verifier' )


    oauth = OAuth1Session( credentials[ 'client_key' ],
                           client_secret = credentials[ 'client_secret' ],
                           resource_owner_key = resource_owner_key,
                           resource_owner_secret = resource_owner_secret,
                           verifier = verifier
    )

    oauth_tokens = oauth.fetch_access_token( access_url ) 

    resource_owner_key = oauth_tokens.get( 'oauth_token' )
    resource_owner_secret = oauth_tokens.get( 'oauth_token_secret')

    credentials[ 'resource_owner_key' ] = resource_owner_key
    credentials[ 'resource_owner_secret' ] = resource_owner_secret
    write_keys( args.key_file, credentials )


def write_keys( fname, creds ):
    credential_order = [ 'client_key',
                         'client_secret',
                         'resource_owner_key',
                         'resource_owner_secret'
                       ]
    with open( fname, 'w' ) as of:

        for cred in credential_order:
            of.write( f"{cred}\t{creds[ cred ]}\n" )

def parse_keys_from_f( fname ):
    return_credentials = dict()
    with open( fname, 'r' ) as of:
        for line in of:
            key, val = line.strip().split( '\t' )
            return_credentials[ key ] = val
    return return_credentials





if __name__ == '__main__':
	main()

