from socket import *
from _thread import *
import threading
import select
import logging
import os

BUFFER_SIZE = 32
SEPARATOR = "<SEPARATOR>"

class chatRoomServer(threading.Thread):
    # Peer server initialization
    def __init__(self, username, chatRoomServerPort):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # port number of the peer server
        self.chatRoomServerPort = chatRoomServerPort
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        self.isFileIncoming = 0
        self.isNameReceived = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer that is connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPort = None
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None
        self.firstJoin = 0
    
    # main method of the peer server thread
    def run(self):

        print("Chat room server started...")    
        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname=gethostname()
        try:
            self.chatRoomServerHostname=gethostbyname(hostname)
        except gaierror:
            import netifaces as ni
            self.chatRoomServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

        # ip address of this peer
        #self.peerServerHostname = 'localhost'
        # socket initializations for the server of the peer
        self.tcpServerSocket.bind(("127.0.0.1", self.chatRoomServerPort))
        self.tcpServerSocket.listen(30)
        # inputs sockets that should be listened
        clients = []
        nicknames = []
        def broadcast(inputs,message):
            for client in inputs:
                client.send(message)

        def handle(nicknames,client):
            while True:
                try:
                    message = client.recv(1024)
                    if(message[-4:].decode("ascii")=='QUIT'):
                        index = clients.index(client)
                        broadcast([client],message)
                        clients.remove(client)
                        print(clients)
                        client.close()
                        nickname = nicknames[index]
                        nicknames.remove(nickname)
                        broadcast(clients,f"{nickname} has left the chat!".encode("ascii"))
                        break
                    else:
                        broadcast(clients,message)
                        
                except Exception as e:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                    broadcast(clients,f"{nickname} has left the chat!".encode("ascii"))
                    break
        # server listens as long as there is a socket to listen in the inputs list and the user is online
        while not self.firstJoin or len(clients)!=0:
            connected, addr = self.tcpServerSocket.accept()
            #connected.setblocking(0)
            # if the user is not chatting, then the ip and the socket of
            # this peer is assigned to server variables
            connected.send("NICK".encode("ascii"))
            nickname =  connected.recv(1024).decode("ascii")
            nicknames.append(nickname)
            clients.append(connected)
            self.firstJoin = 1
            print(f"Username of the client  is {nickname}!")
            broadcast(clients,f"{nickname} joined the chat!".encode("ascii"))
            connected.send("Connected to the server!".encode("ascii"))

            # starting a thread for each user
            t = threading.Thread(target=handle, args=(nicknames,connected,))
            t.start()
        self.tcpServerSocket.close()
        print("Returning from room")