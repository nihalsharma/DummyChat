class Messages:
    INVALID_PACKET_FORMAT = {
        'message': "Server:The message received is not in a proper format. Send a valid json with keys - 'message', 'sender', 'receiver', 'token'.\n"}

    ASK_FOR_TOKEN = {
        'message': 'Server:Reveal your identity son. Send me message with your key else send the register packet.\n'}
    SEND_TOKEN = {'message': "Server:Here is your key {0}. Use it for further communications.\n"}
    SEND_OFFLINE = {'message': 'Server:Receiver is not online. He will get the message when he is up.\n'}
    NOTIFY_USER_ONLINE = {'message': 'Server:User {0} is now online. You can talk to him.\n'}
    NOTIFY_USER_OFFLINE = {'message': 'Server:User {0} is went offline.'}
    INVALID_TOKEN = {'message': 'Server:Could not identify you son. Reveal you identity or ask for a new life.\n'}
    OFFLINE_MESSAGES = {'message': 'Server:You have offline messages.\n'}
    NO_OFFLINE_MESSAGES = {'message': 'Server:You do not have offline messages.\n'}
    DUPLICATE_MESSAGE = {'message': 'Server:Kindly avoid sending duplicate messages.\n'}


class Mappings:
    IDENTITY_CHECK = {}  # store a hash of sender to verify the identity
    CONNECTION_MAP = {}  # maps a sender/receiver with their sockets
    SENDER_RECEIVER_MAP = {}  # {sender: {'receiver1': addr, 'receiver2': addr}} stores the sender and receiver mapping
    USER_SOCKET_MAP = {}  # user mapped with the socket address
    SOCKET_USER_MAP = {}  # socket address mapped with user
