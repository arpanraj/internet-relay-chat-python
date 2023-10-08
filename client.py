import socket   
import sys
import select

import settings
import manager
import strings
import terminal

def connect_to_server():
    """
    Creates a socket object for the client, sets the socket timeout as specified in settings,
    attempts to connect to the server at the default host and port specified in settings,
    and prints a message indicating whether the connection was successful. If the connection
    was not successful, exits the program with an error message.

    Args: None

    Returns:
        client: a socket object representing the client's connection to the server
    """
    client = socket.socket(settings.IPV4, settings.CONNECT_TCP)
    client.settimeout(settings.CLIENT_TIMEOUT)
    try:
        print(strings.TRYING_CONNECTION)
        client.connect((settings.LOCAL_HOST, settings.PORT))
    except:
        sys.exit(strings.CAN_NOT_CONNECT)
    print(strings.CONNECTION_SUCCESS)
    return client

def read_from_server(client):
    """
    Attempts to read data from the client socket representing the server's response.
    If the read is successful, prints the response to the terminal using terminal.print_response.
    If there is an error reading the socket or the socket is closed, exits the program with an error message.

    Args:
        client: a socket object representing the client's connection to the server
    
    Returns: None
    """
    try:
        response = client.recv(settings.INPUT_SIZE)
    except:
        sys.exit(strings.DISCONNECTED_FROM_SERVER)
    if response:
        terminal.print_response(response)
    else:
        sys.exit(strings.DISCONNECTED_FROM_SERVER)

def send_to_server(client):
    """
    Reads a line of text from standard input and filters it as a client command using terminal.filter_client_command,
    then sends the resulting command string to the server using the client socket.

    Args:
        client: a socket object representing the client's connection to the server

    Returns: None
    """
    send_command = sys.stdin.readline()
    filtered_command = terminal.filter_client_command(send_command, client)
    client.send(filtered_command.encode(settings.SUPPORTED_TEXT_TYPE))

def run_client():
    """
    Runs the client program by connecting to the server, creating a client stream with the client socket and standard input,
    and entering a loop that selects from the client stream and handles input accordingly.

    Args: None

    Returns: None
    """
    client = connect_to_server()
    manager.welcome(client)
    client_stream = [client, sys.stdin]
    while True:
        read_list, _, _ = select.select(client_stream, [], [])
        for input in read_list:
            if input == client:
                read_from_server(client)
            else:
                send_to_server(client)

if __name__ == '__main__':
    run_client()
