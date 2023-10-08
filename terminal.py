#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
import strings
import manager
import sys

def execute(client_input_string: str, client) -> None:
    """
    Executes a command based on a client input string.
    
    Args:
        client_input_string (str): The client input string.
        client: The client object.
    """
    command_string = client_input_string.strip()
    if len(command_string) < settings.MIN_COMMAND_SIZE: 
        client.send(strings.INPUT_INVALID.encode(settings.SUPPORTED_TEXT_TYPE))
    else:
        command = command_string[0:4].upper()
        argument = command_string[5:]
        command_to_fun(command, argument, client)

def command_to_fun(command, argument, client):
    """
    Maps a command string to a corresponding function call in the `manager` module.

    Args:
        command (str): The command to execute.
        argument (str): The argument to the command.
        client: The client connection.

    Returns:
        None
    """
    actions = {
        strings.USER: manager.create_user,
        strings.LIRO: manager.list_rooms,
        strings.LIME: manager.list_members,
        strings.ROOM: manager.create_room,
        strings.JOIN: manager.join_room,
        strings.LEVE: manager.leave_room,
        strings.SEND: manager.send_message,
        strings.HELP: help_commands,
    }
    action = actions.get(command, lambda _, client: client.send(strings.UNKNOWN_COMMAND.encode(settings.SUPPORTED_TEXT_TYPE)))
    action(argument, client)
    
def help_commands(argument, client):
    """
    Send a help message to the client.

    Parameters:
    argument (str): Argument for the help command (not used in this function).
    client (socket): Client socket object.

    Returns:
    None
    """
    client.send(strings.HELP_MESSAGE.encode(settings.SUPPORTED_TEXT_TYPE))


def direct(name):
    """
    Print a direct prompt to the console.

    Parameters:
    name (str): Username of the client.

    Returns:
    None
    """
    print(f'> {name} $ ', end='', flush=True) 


def print_response(response):
    """
    Print a response to the console.

    Parameters:
    response (str): Response message.

    Returns:
    None
    """
    print(f"\n{response}\n")
    direct(manager.username)


def filter_client_command(command, client):
    """
    Filter client command to check for exit command and send the command to the server.

    Parameters:
    command (str): Command string.
    client (socket): Client socket object.

    Returns:
    None
    """
    if str.upper(command[0:4]) == strings.EXIT:
        client.close()
        sys.exit(strings.EXIT_SUCCESSFUL)
    client.send(command.encode(settings.SUPPORTED_TEXT_TYPE))