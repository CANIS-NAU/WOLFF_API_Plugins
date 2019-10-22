#!/usr/bin/env python3
import argparse
import wolff_api_plugins.server.server as wolff_server

def main():
    argp = argparse.ArgumentParser( description = "Node proxy for the WOLFF server architecture. "
                                    "This proxy sits on a node and communicates between a WOLFF client "
                                    "and the WOLFF gateway server."
                                  )

if __name__ == '__main__':
    main()
