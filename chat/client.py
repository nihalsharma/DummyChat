import socket, select, sys


def prompt():
    """
    Display a prompt
    """
    sys.stdout.write('<Me> ')
    sys.stdout.flush()


def display_message(data):
    """
    displays the data on client's terminal
    :param data:
    """
    sys.stdout.write("\n")
    message = data.decode()
    sys.stdout.write(message)
    prompt()


# main function
if __name__ == "__main__":

    if (len(sys.argv) < 3):
        print('Usage : python client.py hostname port')
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print('Unable to connect')
        sys.exit()

    print('Connected to remote host. Start sending messages')
    prompt()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:
            # incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from chat server')
                    sys.exit()
                else:
                    display_message(data)

            else:
                msg = sys.stdin.readline()
                s.send(bytes(msg, 'UTF-8'))
                prompt()
