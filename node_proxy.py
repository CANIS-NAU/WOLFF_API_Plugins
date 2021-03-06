#!/usr/bin/env python3
import argparse
import wolff_api_plugins.server.server as wolff_server
import wolff_api_plugins.server.DBConnection as wolff_db
import logging
import sys

def main():
    argp = argparse.ArgumentParser( description = "Node proxy for the WOLFF server architecture. "
                                    "This proxy sits on a node and communicates between a WOLFF client "
                                    "and the WOLFF gateway server."
                                  )
    argp.add_argument( '--client_ip', help = "The IP address to listen for "
                       "client connections on. connect to.", type = str,
                       default = '127.0.0.1' 
                     )
    argp.add_argument( '--broker_ip', help = "The IP address to connect to the "
                       "MQTT broker on.", type = str,
                       default = '127.0.0.1' 
                     )

    argp.add_argument( '--client_port', help = "The port to listen for "
                       "client connections.", type = int, default = 5556
                     )
    argp.add_argument( '--broker_port', help = "The port of the MQTT broker",
                       type = int, default = 1883
                     )
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "node_proxy.log"
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
                               f"--client_ip: {args.client_ip}\n"
                               f"--client_port: {args.client_port}\n"
                               f"--broker_ip: {args.broker_ip}\n"
                               f"--broker_port: {args.broker_port}\n"
                               f"--log_file: {args.log_file}\n"
    )

    logging.getLogger().debug( "Creating a WOLFF Node proxy" )


    server = wolff_server.WOLFFNodeProxy( client_ip = args.client_ip,
                                          client_port = args.client_port,
                                          broker_ip = args.broker_ip,
                                          broker_port = args.broker_port 
                                        )

    server.start()

if __name__ == '__main__':
    main()
