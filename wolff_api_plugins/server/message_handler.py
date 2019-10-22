#!/usr/bin/env python3

class MQTTMessageHandler:
    def on_connect( client, userdata, flags, rc, channels = None ):
        """
        Callback used by Paho MQTT upon connection 
        with the MQTT broker.
        """
        print( "Connected with result code " + str( rc )  )

        client.subscribe( 'posts/#' )
        for chan in channels:
            client.subscribe( chan )

    def on_message( client, userdata, msg ):
        """
        Callback used by Paho MQTT upon reception of a message 
        from the MQTT broker.
        """

        # get the method name from the URL 
        data_dict = self.decode_data( msg.payload )
        topic = str( msg.topic ).split( '/' )
        topic[ 0 ] = 'responses'

        # Note: topic is of the form /posts/client_x, where x is the ID for the client
        topic = '/'.join( topic )

        #result = self.do_request( data_dict )

        #self.get_client().publish( topic, result.text, qos = 1 )
        time.sleep( 10 )
        self.get_client().publish( topic, msg.payload, qos = 1 )

