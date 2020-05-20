#!/usr/bin/env python3
import logging
import json
import time
import sys
import argparse


def main():
    argp = argparse.ArgumentParser( description = "Script to update an existing listing." ) 
    argp.add_argument( '--ip', help = "IP of the Proxy server that an update request will be sent to." )
    argp.add_argument( '--port', help = "Port of the proxy server's update_listing service.", type = int )
    argp.add_argument( '--listing_id', help = "Listing id (as located in the file containing listings) of the id to update." )
    argp.add_argument( '--listings_file', help = "Name of the file containing listings that can be updated.",
                       default = "submitted_listings.json"
    )
    argp.add_argument( '--update', action = 'append', nargs = '+',
                       help = "The value you wish to update, combined with its new value, separated by an 'equals'. "
                       'Example: title="This is the new title". To update multiple values, include this argument multiple times.'
    )
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "update_listing.log"
                     )

    
    args = argp.parse_args()

    logging.basicConfig( level = logging.NOTSET,
                         format = '%(asctime)s [%(levelname)-5.5s] %(message)s', 
                         handlers = [
                             logging.FileHandler( args.log_file ),
                             logging.StreamHandler( sys.stdout )
                         ]
    )

    logging.getLogger().debug( "Parsed arguments with values: \n"
                               f"--ip: {args.ip}\n"
                               f"--port: {args.port}\n"
                               f"--log_file: {args.log_file}\n"
    )




if __name__ == '__main__':
    main()
