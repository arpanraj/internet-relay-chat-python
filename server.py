
import socket
import select
import sys

import settings
import manager
import strings
import terminal

def start_server():
    """
    Creates and returns a socket object representing the server, bound to the default host and port specified in settings,
    and set to listen for incoming connections.

    Args: None

    Returns:
        server: a socket object representing the server
    """
    server = socket.socket(settings.IPV4, settings.CONNECT_TCP)
    server.bind((settings.DEFAULT_HOST, settings.PORT))
    server.listen(settings.MAX_CONNECT_REQUEST)
    return server

def accept_client(server, server_stream):
    """
    Accepts a new client connection and adds the client's socket object to the server stream
    and increments the total number of clients. Prints a message indicating the new client's IP address.

    Args:
        server: a socket object representing the server
        server_stream: a list of socket objects representing the server and standard input streams

    Returns: None
    """
    client, ip_address = server.accept()
    manager.total_clients += 1
    print(strings.NEW_CLIENT, ip_address)
    server_stream.append(client)

def read_stdin():
    """
    Reads a line of text from standard input and returns it.

    Args: None

    Returns:
        command: a string representing the line of text read from standard input
    """
    command = sys.stdin.readline()
    return command

def handle_client_input(client, server_stream):
    """
    Reads data from a client socket, decodes it as a string, executes it as a terminal command,
    and prints a message indicating that the client input was received. If there is an error reading
    the client socket, or if the socket is closed, disconnects the client.

    Args:
        client: a socket object representing the client socket
        server_stream: a list of socket objects representing the server and standard input streams

    Returns: None
    """
    try:
        client_input = client.recv(settings.INPUT_SIZE)
    except:
        manager.disconnect(server_stream, client)
                
    if client_input:
        client_input_string = client_input.decode(settings.SUPPORTED_TEXT_TYPE).rstrip()
        terminal.execute(client_input_string, client)
        print(strings.CLIENT_INPUT)
    else:
        manager.disconnect(server_stream, client)

def run_server():
    """
    Starts the server, creates a server stream with the server socket and standard input,
    and enters a loop that selects from the server stream and handles input accordingly.

    Args: None

    Returns: None
    """
    server = start_server()
    server_stream = [server, sys.stdin]
    while True:
        read_list, _, _ = select.select(server_stream, [], [])
        for input in read_list:
            if input == server:
                accept_client(server, server_stream)
            elif input == sys.stdin:
                command = read_stdin()
                if str.upper(command[0:4]) == strings.EXIT:
                    server.close()
                    print(strings.SERVER_STOPPED)
                    return
            else:
                handle_client_input(input, server_stream)

if __name__ == '__main__':
    print(strings.SERVER_STARTED)
    run_server()