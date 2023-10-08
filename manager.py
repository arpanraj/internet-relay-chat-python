import settings
import strings
import sys
import terminal

clients       = {}
rooms         = {}
total_clients = 0
username      = strings.DEFAULT_USERNAME

def welcome(client):
    """Prompts the user to input their name, sends it to the server as a 'USER' command, and waits for a welcome message
    from the server before displaying it. If the welcome message indicates success, returns and prints the user's name as
    a prompt for further input.

    Args:
    - client: a socket representing the client's connection to the server.

    Returns: None
    """
    complete = 0
    global username
    while not complete:
        print(strings.YOUR_NAME, end='', flush=True)
        username = sys.stdin.readline().rstrip()
        send_data = strings.USER + username
        client.send(send_data.encode(settings.SUPPORTED_TEXT_TYPE))

        try:
            response = client.recv(settings.INPUT_SIZE).decode(settings.SUPPORTED_TEXT_TYPE).rstrip()
        except:
            sys.exit(strings.DISCONNECTED_FROM_SERVER)

        print(response)

        if (response[0:2] == strings.WELCOME_CLIENT[0:2]):
            complete = 1
    terminal.direct(username)

def disconnect(server_stream, client):
    """
    Disconnects a client from the chat server, removing them from any rooms they are in and 
    updating the server state. 

    Args:
        server_stream (socket.socket): The server's socket stream.
        client (socket.socket): The client's socket stream to be disconnected.

    Returns:
        None
    """
    global total_clients,clients

    try:
        
        print(strings.CLIENT_DISCONNECT)
        _rooms = clients[client][strings.ROOMS]
        for room in _rooms:
            rooms[room][strings.CLIENTS].remove(clients[client])
        clients.pop(client)

    except:
        print(strings.CLIENT_DISCONNECT_ERR)


    client.close()
    server_stream.remove(client)
    total_clients -= 1

def create_user(name, client):
    """
    Creates a new user with the given name and adds them to the clients list.

    Args:
        name (str): The name of the user to create.
        client (socket): The socket object representing the client.

    Returns:
        int: 0, indicating the function completed successfully.

    """
    if clients.__contains__(client):
        client.send(strings.CLIENT_ALREADY_IN.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    for _client in clients:
        if clients[_client][strings.NAME] == name:
            client.send(strings.CLIENT_EXISTS.encode(settings.SUPPORTED_TEXT_TYPE))
            return 0

    clients[client] = {
        strings.NAME: name,
        strings.ROOMS: [],
        strings.SOCKET: client
    }

    welcome = strings.WELCOME_CLIENT + strings.HELP_MESSAGE
    client.send(welcome.encode(settings.SUPPORTED_TEXT_TYPE))
    return 0

def authenticate(client):
    """
    Check if a client is authenticated.

    Args:
        client (socket): The client socket object to authenticate.

    Returns:
        bool: True if the client is authenticated, False otherwise.
    """
    if (client in clients):
        return True
    else:
        client.send(strings.CLIENT_INVALID.encode(settings.SUPPORTED_TEXT_TYPE))
        return False

def validate(name):
    """
    Validates the given name to ensure that it is not empty and does not contain any whitespace.

    Args:
        name (str): The name to validate.

    Returns:
        bool: True if the name is valid, False otherwise.
    """
    return (len(str.split(name,' ')) > 1 or len(name) == 0)
       
def transmit(rooms,note):
    """
    Sends a message to all clients in the specified rooms, or to all clients if no rooms are specified.

    Args:
        rooms (list): A list of room names to send the message to.
        note (str): The message to send.

    Returns:
        None.
    """
    if len(rooms) == 0:
        for client in clients:
            clients[client][strings.SOCKET].send(note.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    while len(rooms) > 0:
        name = rooms.pop(0)
        if rooms.__contains__(name):
            _clients = rooms[name][strings.CLIENTS]
            for client in _clients:
                client[strings.SOCKET].send(note.encode(settings.SUPPORTED_TEXT_TYPE))   
                
def list_rooms(argument, client):
    """
    Sends a list of available chat rooms to the client.

    Args:
        argument (str): The argument received from the client (ignored).
        client (socket): The socket object representing the client.

    Returns:
        int: Always returns 0 to indicate successful execution.
    """
    if not (authenticate(client)):
        return 0
    
    send_string = ''
    if len(rooms) > 0:
        send_string += strings.ROOMS_AVAILABLE_TITLE
        for room in rooms:
            send_string += rooms[room][strings.NAME] + strings.NEW_LINE
    else:
        send_string += strings.NO_ROOMS_TITLE  
    client.send(send_string.encode(settings.SUPPORTED_TEXT_TYPE))
    return 0

def list_members(argument, client):
    """
    Lists members in a particular chat room.

    Args:
        argument (str): The room name.
        client (socket): The socket object of the client.

    Returns:
        int: Returns 0.
    """
    if not (authenticate(client)):
        return 0
        
    if validate(argument):
        client.send(strings.INVALID_ROOM_NAME.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    if not rooms.__contains__(argument):
        client.send(strings.ROOM_DOES_NOT_EXIST.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    room_members = rooms[argument][strings.CLIENTS]
    send_string = ""
    send_string += strings.ROOM_MEMBERS
    for member in room_members:
        send_string += member[strings.NAME] + strings.NEW_LINE
    client.send(send_string.encode(settings.SUPPORTED_TEXT_TYPE))
    return 0

def create_room(name, client):
    """
    Create a new chat room with the given name, and add the client to the room's client list.

    Args:
        name (str): The name of the room to be created.
        client (socket): The client socket object.

    Returns:
        int: Always returns 0.
    """
    if not (authenticate(client)):
        return 0

    if validate(name):
        client.send(strings.INVALID_ROOM_NAME.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0
    
    for room in rooms:
        if rooms[room][strings.NAME] == name:
            client.send(strings.ROOM_DOES_NOT_EXIST.encode(settings.SUPPORTED_TEXT_TYPE))
            return 0

    rooms[name] = {
        strings.NAME    : name,
        strings.CLIENTS : []
    }

    send_string = ""
    send_string += strings.ROOM_ADDED
    client.send(send_string.encode(settings.SUPPORTED_TEXT_TYPE))
    return 0

def join_room(name, client):
    """
    Joins a user to a specified room if the user is authenticated and the room exists.
    If the user is already a member of the room, sends a message indicating so.
    Sends a message to all members of the room that a new member has joined.
    
    Args:
    - name: string, the name of the room to join.
    - client: socket object, the client socket to join the room.
    
    Returns:
    - 0 if the user was not able to join the room.
    - None otherwise.
    """
    if not (authenticate(client)):
        return 0

    if validate(name):
        client.send(strings.INVALID_ROOM_NAME.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    if not rooms.__contains__(name):
        client.send(strings.ROOM_DOES_NOT_EXIST.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    room_members = rooms[name][strings.CLIENTS]
    member = clients[client]
    if member in room_members:
        client.send(strings.ALREADY_MEMBER.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    transmit([name], strings.NEW_MEMBER_JOINED)
    room_members.append(member)
    member[strings.ROOMS].append(name)
    client.send(strings.MEMBERSHIP_GRANTED.encode(settings.SUPPORTED_TEXT_TYPE))
    return 0

def leave_room(name, client):
    """
    Removes a client from a room and broadcasts to all remaining members that they have left.
    Args:
        name (str): The name of the room to leave.
        client (socket): The client's socket object.

    Returns:
        int: Always returns 0.
    """
    if not (authenticate(client)):
        return 0

    if validate(name):
        client.send(strings.INVALID_ROOM_NAME.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    if not rooms.__contains__(name):
        client.send(strings.ROOM_DOES_NOT_EXIST.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    _clients = rooms[name][strings.CLIENTS]
    _client = clients[client]

    if not (_client in _clients):
        client.send(strings.NOT_MEMBER.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    _clients.remove(_client)
    _client[strings.ROOMS].remove(name)
    transmit([name], strings.MEMBER_LEFT)
    client.send(strings.YOU_LEFT_ROOM.encode(settings.SUPPORTED_TEXT_TYPE))
    
    return 0

def send_message(arguments, client):
    """Sends a message to a specified room and its members.

    Args:
        arguments (str): A string containing the name of the room and the message to be sent,
                         separated by a space.
        client (socket): The socket object representing the client that sent the message.

    Returns:
        int: Returns 0 to indicate the function has completed.

    """
    if not (authenticate(client)):
        return 0

    arguments_arr = str.split(arguments, " ",1)
    
    if not (len(arguments_arr) == 2 and len(arguments_arr[0]) > 0 and len(arguments_arr[1]) > 0 ):
        client.send(strings.INVALID_MESSAGE_FORMAT.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0

    room = arguments_arr[0]
    message = arguments_arr[1]

    # check if room exists
    if not rooms.__contains__(room):
        client.send(strings.ROOM_DOES_NOT_EXIST.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0    

    _clients = rooms[room][strings.CLIENTS]
    _client = clients[client]
    username = _client[strings.NAME]

    if not (_client in _clients):
        client.send(strings.NOT_MEMBER.encode(settings.SUPPORTED_TEXT_TYPE))
        return 0    

    for receiver in _clients:
        if not (receiver == _client):
            send_string = f"\n{username}@{room}: " + message
            receiver[strings.SOCKET].send(send_string.encode(settings.SUPPORTED_TEXT_TYPE))

    
    send_string = f"You@{room}: " + message
    client.send(send_string.encode(settings.SUPPORTED_TEXT_TYPE))
    return 0