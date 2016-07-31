### Problem statement ###

Mini Version of a persistent mobile chat


* Maintains a persistent socket connection to every mobile device that has requested a
connection to the server. Preferably assigns a destinationId to each mobile device which maps
to its socket connection.


* Routes messages tagged with the destinationId to a particular mobile device.


* Does not send duplicate messages. Duplicate messages are defined as ((“message1, destinationId1” == “message2, destinationId2”) && (arrivalTime2­arrivalTime1)<= 5sec)


### How do I get set up? ###


* needs Redis installed on the system - Refer - https://www.redis.io
* install the dependencies - python3 setup.py install
* run the server.py first
* run the client -  python3 chat/client.py localhost 5000

* There are three packets - 1. Register 2. Message 3. Reconnect (on the same token). The format must be as below.

    * Register - When the client does an authentication process with the server - 
      {'register':'true', 'sender':'0011001100'}, The server then sends a token which has to be used to maintain the indentity with the sever
 
    * Reconnect - When the client went offline and then reconnects with the server with the same old token - {'reconnect':'true', 'token':'ln8lha1i20', 'sender':'0011001100'}. If the old token is not provided the client has to do a re-register to get a new token.
    
    * Message - The actual message format from a sender to a receiver - {'message':'Kya Bhai?', 'sender':'0011001100', 'receiver':'987654321', 'token':'ln8lha1i20'}
     


### Scope of improvements ###

* needs a better designing of how the messages are exchanged.
* robust token generation system.

### What could be achieved during the exercise###

* understanding of how sockets work.
* persistence using redis
    * Redis is used to store the offline messages. Once a user returns online and reconnects using the same key - the offline messages are sent to him.
    
    * To check if message from sender A to Receiver B are not duplicate within 5 seconds - using key's ttl property.

