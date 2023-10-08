#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
from enum import Enum

DEFAULT_HOST = "" #empty because naming host in mac causes error so localhost as default name will be accepted
LOCAL_HOST   = "localhost" 
PORT         = 31415
INPUT_SIZE   = 102400
IPV4         = socket.AF_INET
CONNECT_TCP  = socket.SOCK_STREAM
MAX_CONNECT_REQUEST = 6
CLIENT_TIMEOUT      = 6
MIN_COMMAND_SIZE    = 4
SUPPORTED_TEXT_TYPE   = "utf-8"

class switch(Enum):
    ON = True
    OFF = False
