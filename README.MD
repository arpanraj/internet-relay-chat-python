IRC chat in Python
This is a Python project that demonstrates Instant relay chat

server.py   : A server program that listens for incoming connections from clients, executes commands received from them, and sends back the results. <br />

client.py   : A client program that connects to the server and sends commands to it, and receives the results. <br />

strings.py  : A program that defines constants for messages related to the functionality and error handling of an application. <br />

settings.py : A program that defines constants for a socket connection and a custom Enum class with two states, ON and OFF. <br />

terminal.py : A program that defines terminal category functions such as map client commands to corresponding server functions, and to filter and send client commands to the server. <br />

manager.py  : A program that defines manegorial category functions such as authentication, creating and disconnecting clients, sending messages to rooms, and listing available chat rooms. <br />

Prerequisites <br />
Python 3.x installed <br />
Command line interface <br />

Run <br />
Run the server program in terminal: 
python server.py <br />
In another terminal window, run the client program: 
python client.py <br />

License <br />
This project is licensed under the MIT License - see the LICENSE file for details.
