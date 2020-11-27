from socket import *
import threading
import select
import logging
import db
import netifaces as ni

# This class process peer messages that are sent to mainServer
# for each peer connected new client thread is created

class ClientPeerThread(threading.Thread):
    # initialisation for client thread
