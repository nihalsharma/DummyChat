import random
import socket, select
import ast
import sys
from chat.exception import ChatServerInitException
from chat.persistent import RedisPersistent
from chat.resources import Messages, Mappings

RECEIVE_BUFFER = 4096
PORT = 5000


def broadcast_data(sock, message):
    # Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock:
            try:
                socket.send(bytes(message, 'UTF-8'))
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                cleanup_client_disconnect(socket)


def sendto(socket, message):
    """
    send to a particular socket
    :param socket:
    :param message:
    :param address:
    """
    try:
        socket.send(bytes(message, 'UTF-8'))
    except:
        # broken socket connection may be, chat client pressed ctrl+c for example
        socket.close()
        cleanup_client_disconnect(socket)


def verify_message_format(data) -> bool:
    """
    verify if message packet is in desired format - data packet, register packet
    :param data:
    :return:
    """
    if data:
        if isinstance(data, dict):
            return all(key in data for key in ("message", "sender", "receiver", "token")) or \
                   all(key in data for key in ("register", "sender")) or \
                   all(key in data for key in ("reconnect", "sender", "token"))

    return False


def verify_message(data):
    """
    verify the client against the token he has sent
    :param data:
    """
    sender = data.get('sender')
    token = data.get('token')
    return sender and token and Mappings.IDENTITY_CHECK.get(sender) == token


def get_random_token():
    """
    get a random token for a client
    :return:
    """
    # TODO: need to use proper hashing here
    return ''.join(random.choice('01289nihal') for i in range(10))


def update_sender_receiver_map(sender, receiver):
    """
    Update mapping of sender receiver
    :param sender:
    :param receiver:
    """
    sender_receivers = Mappings.SENDER_RECEIVER_MAP.get(sender) or set()
    sender_receivers.add(receiver)
    Mappings.SENDER_RECEIVER_MAP.update({sender: sender_receivers})


def send_or_persist(sender_sock, data):
    """
    Send the chat message to the destination else persist it if the destination is offline
    :param data:
    """
    receiver = data.get('receiver')
    message = sender + ":" + data.get('message') + "\n"
    receiver_add = Mappings.USER_SOCKET_MAP.get(receiver)
    if Mappings.CONNECTION_MAP.get(receiver_add):
        update_sender_receiver_map(sender, receiver)
        # if the message is not duplicate send it and store for a while as well(ttl)
        if persistent.check_message(sender, receiver, message):
            persistent.save_message(sender, receiver, message)
            sendto(Mappings.CONNECTION_MAP.get(receiver_add), message)
        else:
            # notify about duplicate message
            sendto(sender_sock, Messages.DUPLICATE_MESSAGE.get('message'))
    else:
        # persist the data to some persistent storage
        if persistent.check_message(sender, receiver, message):
            persistent.save_message(sender, receiver, message)
            persistent.save_persist_offline_messages(sender, receiver, message)
            sendto(sock, Messages.SEND_OFFLINE.get('message'))
        else:
            # notify about duplicate message
            sendto(sender_sock, Messages.DUPLICATE_MESSAGE.get('message'))


def register_client(sock, sender):
    """
    identify a user
    :param sock:
    :param sender:
    """
    token = get_random_token()
    Mappings.IDENTITY_CHECK.update({sender: token})
    Mappings.USER_SOCKET_MAP.update(
        {sender: str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1])})
    Mappings.SOCKET_USER_MAP.update(
        {str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]): sender})
    Mappings.CONNECTION_MAP.update(
        {str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]): sock})
    sendto(sock, Messages.SEND_TOKEN.get('message').format(token))


def notify_reconnect(sender):
    """
    Notify the active client that this user is online again
    :param sender:
    """
    # update all the mappings as they were removed when disconnected
    Mappings.USER_SOCKET_MAP.update(
        {sender: str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1])})
    Mappings.SOCKET_USER_MAP.update(
        {str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]): sender})
    Mappings.CONNECTION_MAP.update(
        {str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]): sock})
    if Mappings.SENDER_RECEIVER_MAP.get(sender) and len(
            Mappings.SENDER_RECEIVER_MAP.get(sender)):
        for value in Mappings.SENDER_RECEIVER_MAP.get(sender):
            receiver_add = Mappings.USER_SOCKET_MAP.get(value)
            if Mappings.CONNECTION_MAP.get(receiver_add):
                sendto(Mappings.CONNECTION_MAP.get(receiver_add),
                       Messages.NOTIFY_USER_ONLINE.get('message').format(sender))


def cleanup_client_disconnect(sock):
    """
    Handle when a client is disconnected
    1. Remove from list of active connections
    2. Notify the users which were chatting with this user
    :param sock:
    """
    CONNECTION_LIST.remove(sock)
    Mappings.CONNECTION_MAP.pop(str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]))
    receiver = Mappings.SOCKET_USER_MAP.get(
        str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]))
    for value in Mappings.SENDER_RECEIVER_MAP.get(receiver):
        receiver_add = Mappings.USER_SOCKET_MAP.get(value)
        if Mappings.CONNECTION_MAP.get(receiver_add):
            sendto(Mappings.CONNECTION_MAP.get(receiver_add),
                   Messages.NOTIFY_USER_OFFLINE.get('message').format(receiver) + "\n")
    Mappings.SOCKET_USER_MAP.pop(str(sock.getpeername()[0]) + ":" + str(sock.getpeername()[1]))


def reconnect_client(sender, token):
    """
    update a client's connection
    :param sender:
    :param token:
    """
    return sender and token and Mappings.IDENTITY_CHECK.get(sender) == token


def send_offline_messages(sock, messages):
    """
    When a client comes online - send him the offline messages, if any
    :param sock:
    :param messages:
    """
    if messages and len(messages):
        sendto(sock, Messages.OFFLINE_MESSAGES.get('message'))
        for key, value in messages.items():
            message_list = value  # a list
            for msg in message_list:
                sendto(sock, msg)
    else:
        sendto(sock, Messages.NO_OFFLINE_MESSAGES.get('message'))


if __name__ == "__main__":
    try:
        persistent = RedisPersistent()
    except Exception as e:
        print("Could not start Redis on local system. Please check the installation.")
        sys.exit()

    CONNECTION_LIST = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    CONNECTION_LIST.append(server_socket)
    print("Chat server started on port " + str(PORT))

    while 1:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        for sock in read_sockets:
            if sock == server_socket:
                # Handle the case in which there is a new connection received through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print("Client ({0}, {1}) connected".format(addr[0], addr[1]))

            else:
                # Data received from client, process it
                try:
                    data = sock.recv(RECEIVE_BUFFER)
                    if data:
                        data = data.decode()
                        try:
                            data = ast.literal_eval(data.strip())
                            if verify_message_format(data):
                                sender = data.get('sender')
                                if 'reconnect' not in data and verify_message(data):
                                    send_or_persist(sock, data)
                                else:
                                    # if it is a register packet
                                    if 'register' in data and data.get('register') in ['true', 'True', 't']:
                                        register_client(sock, sender)
                                    elif 'reconnect' in data and data.get('reconnect') in ['true', 'True', 't']:
                                        reconnected = reconnect_client(sender, data.get('token'))
                                        if reconnected:
                                            # fetch the offline messages
                                            messages = persistent.fetch_offline_messages(sender)
                                            send_offline_messages(sock, messages)
                                            notify_reconnect(sender)
                                        else:
                                            sendto(sock, Messages.INVALID_TOKEN.get('message'))
                                    else:
                                        # ask to send the register packet
                                        sendto(sock, Messages.ASK_FOR_TOKEN.get('message'))
                            else:
                                sendto(sock, Messages.INVALID_PACKET_FORMAT.get('message'))
                        except ValueError as e:
                            sendto(sock, Messages.INVALID_PACKET_FORMAT.get('message'))
                        except Exception as ex:
                            sendto(sock, Messages.INVALID_PACKET_FORMAT.get('message'))

                    else:
                        print("Client ({0}, {1}) disconnected".format(addr[0], addr[1]))
                        cleanup_client_disconnect(sock)

                except Exception as e:
                    print("Client ({0}, {1}) is offline".format(addr[0], addr[1]))
                    sock.close()
                    cleanup_client_disconnect(sock)
                    continue

    server_socket.close()
