# -*- coding: utf-8 -*-
import sys

__version__ = "1.0.0"

from ChatRoom.main import Room, User
from ChatRoom.net import Server, Client
from ChatRoom.net import hash_encryption

del log, encrypt, main, net, sys
