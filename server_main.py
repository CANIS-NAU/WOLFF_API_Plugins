#!/usr/bin/env python3
import wolff_api_plugins.server.server as wolff_server
import argparse

def main():
    argp = argparse.ArgumentParser( description = "Start a WOLFF server than can handle HTTP requests." )

    argp.add_argument( '--ip', help = "The IP address to connect to.", type = str,
                       default = '127.0.0.1' 
                     )
    argp.add_argument( '--port', help = "The port to connect to.", type = int, default = 5555 )

    args = argp.parse_args()


    server = wolff_server.WOLFFServer( ip = args.ip, port = args.port )

    server.start()

if __name__ == '__main__':
    main()
