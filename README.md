# WOLFF API Plugins
## Requirements:
    - paho-mqtt
    - requests_oauthlib 
    - An MQTT client such as mosquitto

### To create the Reference Manual:
```
	cd doc
	doxygen doxygen.conf
	cd latex
	make
```
This will produce refman.pdf, detailing class and method documentation.

### Examples:
```simple_etsy_client.py``` contains an example of 
what arguments are used in an etsy message.
