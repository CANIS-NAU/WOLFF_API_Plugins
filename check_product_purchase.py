#!/usr/bin/env python3
import logging
import json
import socket
import time
import sys
import argparse


def main():

    argp = argparse.ArgumentParser( description = "Script to update an existing listing." ) 
    argp.add_argument( '--ip', help = "IP of the Proxy server that an update request will be sent to.", required = True )
    argp.add_argument( '--port', help = "Port of the proxy server's update_listing service.", type = int, required = True )
    argp.add_argument( '--listing_id', help = "Integer ID of the listing to check for an update to. This should be the ID "
                       "returned by the proxy server when the listing was originally posted.", type = int,
                       required = True 
                     )
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "check_product_purchase.log"
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
                               f"--listing_id: {args.listing_id}\n"
                               f"--log_file: {args.log_file}\n"
    )


if __name__ == '__main__':
    main()
